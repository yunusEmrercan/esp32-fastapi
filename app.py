# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from MongoDB.mongo import MongoDB
from datetime import datetime
import logging

logger = logging.getLogger("kart_api")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'))
logger.addHandler(ch)

app = FastAPI(title="Kart & QR Bakiye API", version="1.2.0")

# ---------------- Models ----------------
class KartRequest(BaseModel):
    kart_id: int
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

# ---------------- Helper ----------------
def get_card(kart_id: int):
    return db["cards"].find_document({"kart_id": kart_id})

def get_program_price(program_name: str):
    return db["pricing"].find_document({"program": program_name})

def get_program_time(program_name: str):
    doc = db["times"].find_document({"program": program_name})
    return doc.get("time") if doc else None

def get_qr_data(qr_id: str):
    return db["qr"].find_document({"veri": qr_id})

# ---------------- Endpoints ----------------
@app.post("/kart", response_model=KartResponse)
def kart_endpoint(req: KartRequest):
    card = get_card(req.kart_id)
    if not card:
        return KartResponse(status=False, message="Kart bulunamadı")

    bakiye = float(card.get("bakiye", 0.0))

    if not req.program:
        # Sadece bakiye sorgu
        return KartResponse(status=True, bakiye=bakiye)

    # Program kullanım
    price_doc = get_program_price(req.program)
    if not price_doc:
        return KartResponse(status=False, message="Program bulunamadı")

    price = float(price_doc.get("price", 0.0))
    if bakiye < price:
        return KartResponse(status=False, message="Yetersiz bakiye")

    # Bakiye düş
    new_card = db["cards"].find_one_and_update(
        {"kart_id": req.kart_id},
        {"$inc": {"bakiye": -price}}
    )
    new_bakiye = float(new_card.get("bakiye", 0.0))

    # Program süresi
    time_sec = get_program_time(req.program)

    return KartResponse(status=True, bakiye=new_bakiye, time=time_sec)

@app.post("/qr", response_model=QRResponse)
def qr_endpoint(req: QRRequest):
    qr_doc = get_qr_data(req.qr_id)
    if not qr_doc:
        return QRResponse(status=False, message="QR bulunamadı")

    if qr_doc.get("kullanildi", False):
        return QRResponse(status=False, message="QR kod zaten kullanılmış")

    # Kullanıldığı işaretle
    db["qr"].update_one({"veri": req.qr_id}, {"$set": {"kullanildi": True, "kullanildi_tarih": datetime.utcnow()}})

    # Program bilgisi
    veri = qr_doc.get("veri", "")
    parts = veri.split(".")
    program_name = parts[1] if len(parts) > 1 else None
    time_sec = get_program_time(program_name) if program_name else None

    return QRResponse(status=True, program=program_name, time=time_sec)
