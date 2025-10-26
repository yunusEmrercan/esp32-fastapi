# app.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
from MongoDB.mongo import MongoDB
from datetime import datetime
import logging
from threading import Lock
from collections import defaultdict
from pymongo import ReturnDocument

# ---------------- Logging ----------------
logging.basicConfig(
    filename="/home/emre/Desktop/API/api_logs.log",
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
    encoding="utf-8"
)

logger = logging.getLogger("kart_api")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'))
logger.addHandler(ch)

# ---------------- FastAPI ----------------
app = FastAPI(title="Kart & QR Bakiye API", version="1.2.0")

# ---------------- Models ----------------
class KartRequest(BaseModel):
    kart_id: str
    program: Optional[str] = None

class KartResponse(BaseModel):
    status: bool
    bakiye: Optional[float] = None
    time: Optional[int] = None
    message: Optional[str] = None

class QRRequest(BaseModel):
    qr_id: str

class QRResponse(BaseModel):
    status: bool
    program: Optional[str] = None
    time: Optional[int] = None
    message: Optional[str] = None

# ---------------- Database ----------------
db = {
    "cards": MongoDB("OtomatMap", "customers"),
    "qr": MongoDB("OtomatMap", "qrcode"),
    "pricing": MongoDB("OtomatMap", "pricing"),
    "times": MongoDB("OtomatMap", "times")
}

# ---------------- Locks ----------------
kart_locks = defaultdict(Lock)
ip_lock = Lock()  # tek bir ip lock (ip_last_processed erişimini korur)
qr_lock = Lock()

# ---------------- Helper ----------------
def get_card(kart_id: str):
    return db["cards"].find_document({"kart_id": kart_id})

def get_program_price(program_name: str):
    return db["pricing"].find_document({"program": program_name})

def get_program_time(program_name: str):
    doc = db["times"].find_document({"program": program_name})
    return doc.get("time") if doc else None

def get_qr_data(qr_id: str):
    return db["qr"].find_document({"veri": qr_id})

import time

# kart_id başına son işlem zamanı
kart_last_processed = defaultdict(lambda: 0.0)
# ip başına son başarılı işlem zamanı
ip_last_processed = defaultdict(lambda: 0.0)

# Bekleme süreleri (saniye)
WAIT_CARD_SECONDS = 4    # kart başına tekrar işlem bekleme süresi (istek üzerine dedin 4s)
WAIT_IP_SECONDS = 30     # aynı IP için tekrar işlem bekleme süresi (aynı IP 30s içinde tekrar gelirse duplicate say)

@app.post("/kart", response_model=KartResponse)
def kart_endpoint(req: KartRequest, request: Request):
    """
    - Kart bazlı koruma: 4 saniye içinde ikinci işlem gelirse ücretlendirme yapılmaz.
    - IP bazlı koruma: aynı IP 30 saniye içinde ikinci işlem gelirse ücretlendirme yapılmaz.
    Amaç: 27 adet ESP32 cihazının (internet problemi nedeniyle) arka arkaya post atması durumunda
    kullanıcının hesabından fazla para çekmeyi engellemek.
    """
    card_lock = kart_locks[req.kart_id]
    with card_lock:
        now = time.time()
        last_card_time = kart_last_processed[req.kart_id]

        # İstemcinin IP adresini al
        client_ip = None
        try:
            client_ip = request.client.host
        except Exception as e:
            # IP alınamazsa, ip korumasını devre dışı bırakıyoruz (mantıklı bir fallback).
            logger.warning("Client IP alınamadı: %s", e)
            client_ip = None

        last_ip_time = 0.0
        if client_ip:
            with ip_lock:
                last_ip_time = ip_last_processed.get(client_ip, 0.0)

        logger.info("Kart %s: now-last_card=%.3f, IP %s: now-last_ip=%.3f",
                    req.kart_id, now - last_card_time, client_ip, now - last_ip_time)

        card = get_card(req.kart_id)
        if not card:
            return KartResponse(status=False, message="2")  # kart bulunamadı

        bakiye = float(card.get("bakiye", 0.0))

        # Eğer program belirtilmemişse sadece bakiye döner (sorgu). Bu durumda zaman güncellenmez.
        if not req.program:
            return KartResponse(status=True, bakiye=bakiye)

        price_doc = get_program_price(req.program)
        if not price_doc:
            return KartResponse(status=False, message="3")  # program bulunamadı

        price = float(price_doc.get("price", 0.0))
        if bakiye < price:
            return KartResponse(status=False, message="1")  # bakiye yetersiz

        # Kart ve IP bazlı izin kontrolleri
        allow_by_card = (now - last_card_time) > WAIT_CARD_SECONDS
        allow_by_ip = True
        if client_ip:
            allow_by_ip = (now - last_ip_time) > WAIT_IP_SECONDS

        # Eğer hem kart hem IP izin veriyorsa tahsilat yap
        if allow_by_card and allow_by_ip:
            new_card = db["cards"].find_one_and_update(
                {"kart_id": req.kart_id},
                {"$inc": {"bakiye": -price}},
                return_document=ReturnDocument.AFTER
            )
            new_bakiye = float(new_card.get("bakiye", 0.0))

            # Başarılı tahsilatsa zamanları güncelle
            kart_last_processed[req.kart_id] = now
            if client_ip:
                with ip_lock:
                    ip_last_processed[client_ip] = now

        else:
            # Duplicate / erken istek: tahsilat yapılmaz, mevcut bakiye döndürülür
            # (Davranış, eski '30s içinde' olmayan branch ile aynı)
            new_bakiye = float(card.get("bakiye", 0.0))
            logger.info("Tahsilat yapılmadı (duplicate): kart_allow=%s, ip_allow=%s", allow_by_card, allow_by_ip)

        time_sec = get_program_time(req.program)

        return KartResponse(status=True, bakiye=new_bakiye, time=time_sec)


@app.post("/qr", response_model=QRResponse)
def qr_endpoint(req: QRRequest):
    with qr_lock:
        qr_doc = get_qr_data(req.qr_id)
        if not qr_doc:
            return QRResponse(status=False, message="4")  # QR bulunamadı

        if qr_doc.get("kullanildi", False):
            return QRResponse(status=False, message="5")  # QR zaten kullanılmış

        db["qr"].update_one(
            {"veri": req.qr_id},
            {"$set": {"kullanildi": True, "kullanildi_tarih": datetime.utcnow()}}
        )

        veri = qr_doc.get("veri", "")
        parts = veri.split(".")
        program_name = parts[1] if len(parts) > 1 else None
        time_sec = get_program_time(program_name) if program_name else None

        return QRResponse(status=True, program=program_name, time=time_sec)
