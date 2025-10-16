from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from MongoDB.mongo import MongoDB
from datetime import datetime

app = FastAPI(title="Otomat API")

# MongoDB bağlantıları
customers = MongoDB("OtomatMap", "customers")
transactions = MongoDB("OtomatMap", "transactions")
qr_collection = MongoDB("OtomatMap", "qrcode")
pricing_collection = MongoDB("OtomatMap", "pricing")  # Fiyatlandırma

# -------------------- MODELLER --------------------
class CardRequest(BaseModel):
    kart_id: str

class QRRequest(BaseModel):
    qr_id: str

class QRUseRequest(BaseModel):
    kart_id: str
    qr_id: str

class TransactionRequest(BaseModel):
    kart_id: str
    tutar: float
    islem: str

# -------------------- ENDPOINTLER --------------------

@app.get("/pricing")
def get_pricing():
    """Tüm aktif fiyatlandırmaları döndürür"""
    pricing_docs = pricing_collection.find_documents({"active": True})
    result = [{"program": doc["program"], "price": doc["price"], "active": doc["active"]} for doc in pricing_docs]
    return result

@app.post("/balance")
def get_balance(data: CardRequest):
    """Kart ID ile bakiyeyi döndürür"""
    kart = customers.find_document({"kart_id": data.kart_id})
    if not kart:
        raise HTTPException(status_code=404, detail="Kart bulunamadı")
    return {"kart_id": kart["kart_id"], "balance": kart["bakiye"]}

@app.post("/deduct_balance")
def deduct_balance(data: QRUseRequest):
    """Kart bakiyesinden QR fiyatını düşer"""
    kart = customers.find_document({"kart_id": data.kart_id})
    if not kart:
        raise HTTPException(status_code=404, detail="Kart bulunamadı")

    qr = qr_collection.find_document({"qr_id": data.qr_id})
    if not qr:
        raise HTTPException(status_code=404, detail="QR kod bulunamadı")

    fiyat_doc = pricing_collection.find_document({"program": qr["tip"], "active": True})
    if not fiyat_doc:
        raise HTTPException(status_code=404, detail="Program fiyatlandırması bulunamadı")

    fiyat = fiyat_doc["price"]

    if kart["bakiye"] < fiyat:
        raise HTTPException(status_code=400, detail="Kart bakiyesi yetersiz")

    # Bakiye düş
    new_balance = kart["bakiye"] - fiyat
    customers.update_document({"kart_id": kart["kart_id"]}, {"$set": {"bakiye": new_balance}})

    return {"kart_id": kart["kart_id"], "remaining_balance": new_balance, "price_deducted": fiyat}

@app.post("/add_transaction")
def add_transaction(data: TransactionRequest):
    """Yeni transaction kaydı ekler"""
    date_str = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    transactions.insert_document({
        "kart_id": data.kart_id,
        "tutar": data.tutar,
        "tarih": date_str,
        "işlem": data.islem
    })
    return {"status": "success", "kart_id": data.kart_id, "amount": data.tutar, "operation": data.islem}

@app.post("/qr_status")
def qr_status(data: QRRequest):
    """QR kod var mı, kullanıldı mı kontrol eder"""
    qr = qr_collection.find_document({"qr_id": data.qr_id})
    if not qr:
        raise HTTPException(status_code=404, detail="QR kod bulunamadı")
    return {"qr_id": data.qr_id, "tip": qr["tip"], "kullanildi": qr["kullanildi"]}

@app.post("/mark_qr_used")
def mark_qr_used(data: QRUseRequest):
    """QR kodu kullanıldı olarak işaretler"""
    qr = qr_collection.find_document({"qr_id": data.qr_id})
    if not qr:
        raise HTTPException(status_code=404, detail="QR kod bulunamadı")

    if qr["kullanildi"]:
        raise HTTPException(status_code=400, detail="QR kod zaten kullanılmış")

    qr_collection.update_document({"qr_id": qr["qr_id"]}, {"$set": {"kullanildi": True}})
    return {"status": "success", "qr_id": data.qr_id, "used": True}
