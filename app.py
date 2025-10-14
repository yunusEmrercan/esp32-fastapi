from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Tuple
from MongoDB.mongo import MongoDB
import logging

# -------------------------------
# Logger Config
# -------------------------------
logger = logging.getLogger("kart_api")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(
    title="Kart & QR Bakiye API",
    description="Kart ve QR kod üzerinden bakiye ve hizmet sorgulama API'si.",
    version="1.0.0"
)

# -------------------------------
# MongoDB Bağlantısı
# -------------------------------
class Database:
    """MongoDB servislerini merkezi yönetir."""
    def __init__(self):
        self.cards = MongoDB('OtomatMap', 'customers')
        self.qr_codes = MongoDB('OtomatMap', 'qrcode')

db = Database()

# -------------------------------
# Modeller
# -------------------------------
class CardRequest(BaseModel):
    kart_id: int = Field(..., example=1135, description="Sorgulanacak kart ID")

class BalanceResponse(BaseModel):
    kart_id: int
    bakiye: float
    bulundu: bool

class QRRequest(BaseModel):
    qr_id: str = Field(..., example="3fa85f64-5717-4562-b3fc-2c963f66afa6", description="Sorgulanacak QR kod ID")

class QRResponse(BaseModel):
    qr_id: str
    hizmet_tipi: Optional[str]
    kullanildi: Optional[bool]

# -------------------------------
# Servis Fonksiyonları
# -------------------------------
def get_card_by_id(kart_id: int) -> Optional[dict]:
    """MongoDB'den kart bilgisi getirir."""
    try:
        return db.cards.find_document({'kart_id': kart_id})
    except Exception as e:
        logger.error(f"MongoDB sorgusu sırasında hata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Veritabanı hatası")

def get_qr_info_by_id(qr_id: str) -> Tuple[Optional[bool], Optional[str]]:
    """MongoDB'den QR kod bilgisi getirir."""
    try:
        qr_doc = db.qr_codes.find_document({'qr_id': qr_id})
    except Exception as e:
        logger.error(f"MongoDB sorgusu sırasında hata: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Veritabanı hatası")

    if not qr_doc:
        return None, None

    used = qr_doc.get('kullanildi', None)
    qr_value = qr_doc.get('veri', "")
    parts = qr_value.split('.')
    hizmet = parts[1] if len(parts) >= 3 else None
    return used, hizmet

# -------------------------------
# Endpoints
# -------------------------------
@app.post("/bakiye", response_model=BalanceResponse, summary="Kart bakiyesi sorgulama")
def get_balance(req: CardRequest):
    """
    Verilen kart ID üzerinden bakiyeyi sorgular.
    Kart bulunamazsa:
    - bakiye: 0.0
    - bulundu: False
    """
    user = get_card_by_id(req.kart_id)
    balance = float(user.get('bakiye', 0.0)) if user else 0.0
    found = bool(user)

    logger.info(f"Card ID: {req.kart_id}, Bakiye: {balance}, Bulundu: {found}")
    return BalanceResponse(kart_id=req.kart_id, bakiye=balance, bulundu=found)

@app.post("/qr", response_model=QRResponse, summary="QR kod bilgisi sorgulama")
def get_qr_info(req: QRRequest):
    """
    Verilen QR kod ID üzerinden:
    - hizmet tipi
    - kullanıldı bilgisi
    sorgular.
    Bulunamazsa her iki alan da None döner.
    """
    used, hizmet = get_qr_info_by_id(req.qr_id)
    logger.info(f"QR ID: {req.qr_id}, Hizmet: {hizmet}, Kullanildi: {used}")
    return QRResponse(qr_id=req.qr_id, hizmet_tipi=hizmet, kullanildi=used)
