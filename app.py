# app_full.py
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from MongoDB.mongo import MongoDB
import logging
from datetime import datetime

logger = logging.getLogger("kart_api")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'))
logger.addHandler(ch)

app = FastAPI(title="Kart & QR Bakiye API", version="1.1.0")

class CardRequest(BaseModel):
    kart_id: int = Field(..., example=1135)

class BalanceResponse(BaseModel):
    kart_id: int
    bakiye: float
    bulundu: bool

class QRRequest(BaseModel):
    qr_id: str

class QRResponse(BaseModel):
    qr_id: str
    hizmet_tipi: Optional[str] = None
    kullanildi: Optional[bool] = None

class ChargeRequest(BaseModel):
    kart_id: int
    miktar: float
    buton: int

class ChargeResponse(BaseModel):
    ok: bool
    bakiye: float

class PriceItem(BaseModel):
    buton: int
    fiyat: float

# Database containers
class Database:
    def __init__(self):
        self.cards = MongoDB('OtomatMap', 'customers')
        self.qr_codes = MongoDB('OtomatMap', 'qrcode')
        self.config = MongoDB('OtomatMap', 'config')
        self.transactions = MongoDB('OtomatMap', 'transactions')

db = Database()

# --- helper functions
def get_card_by_id(kart_id: int):
    try:
        return db.cards.find_document({'kart_id': kart_id})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="DB error")

def get_qr_by_id(qr_id: str):
    try:
        return db.qr_codes.find_document({'qr_id': qr_id})
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="DB error")

# --- endpoints
@app.post("/bakiye", response_model=BalanceResponse)
def bakiye(req: CardRequest):
    user = get_card_by_id(req.kart_id)
    bakiye = float(user.get('bakiye', 0.0)) if user else 0.0
    found = bool(user)
    logger.info(f"Bakiye sorgu kart:{req.kart_id} bakiye:{bakiye} bulundu:{found}")
    return BalanceResponse(kart_id=req.kart_id, bakiye=bakiye, bulundu=found)

@app.get("/prices", response_model=List[PriceItem])
def prices():
    # config collection'da fiyatları saklıyoruz: tek bir doc: { _id: "prices", items: [{buton:1,fiyat:2.5}, ...] }
    doc = db.config.find_document({'_id': 'prices'})
    if not doc:
        # default örnek
        defaults = [{'buton': i, 'fiyat': 1.0} for i in range(1,6)]
        return defaults
    return doc.get('items', [])

@app.post("/charge", response_model=ChargeResponse)
def charge(req: ChargeRequest):
    # Atomik bakiye düşümü: find_one_and_update ile bakiye >= miktar koşulu
    card = db.cards.find_document({'kart_id': req.kart_id})
    if not card:
        raise HTTPException(status_code=404, detail="Kart bulunamadı")
    bakiye = float(card.get('bakiye', 0.0))
    if bakiye < req.miktar:
        raise HTTPException(status_code=400, detail="Yetersiz bakiye")
    # update
    new_doc = db.cards.find_one_and_update({'kart_id': req.kart_id}, {'$inc': {'bakiye': -req.miktar}})
    new_balance = float(new_doc.get('bakiye', 0.0))
    # transaction log
    db.transactions.insert_one({
        'kart_id': req.kart_id,
        'miktar': req.miktar,
        'buton': req.buton,
        'tarih': datetime.utcnow()
    })
    return ChargeResponse(ok=True, bakiye=new_balance)

@app.post("/qr", response_model=QRResponse)
def get_qr(req: QRRequest):
    doc = get_qr_by_id(req.qr_id)
    if not doc:
        return QRResponse(qr_id=req.qr_id, hizmet_tipi=None, kullanildi=None)
    hizmet = None
    veri = doc.get('veri', '')
    parts = veri.split('.')
    if len(parts) >= 2:
        hizmet = parts[1]
    return QRResponse(qr_id=req.qr_id, hizmet_tipi=hizmet, kullanildi=doc.get('kullanildi', False))

@app.post("/qr/use")
def qr_use(req: QRRequest):
    doc = get_qr_by_id(req.qr_id)
    if not doc:
        raise HTTPException(status_code=404, detail="QR bulunamadı")
    if doc.get('kullanildi', False):
        raise HTTPException(status_code=400, detail="QR zaten kullanılmış")
    db.qr_codes.update_one({'qr_id': req.qr_id}, {'$set': {'kullanildi': True, 'kullanildi_tarih': datetime.utcnow()}})
    return {"ok": True}