# Abone Kart Otomatı & Kart/QR Bakiye API

Bu proje, **Raspberry Pi uyumlu bir kart otomatı arayüzü** ve **FastAPI tabanlı kart/QR bakiye sorgulama API** içerir.  
Proje ile:

- Kart bakiyesi yükleyebilir ve görüntüleyebilirsiniz.
- Yeni kart oluşturabilirsiniz.
- QR kod oluşturabilir ve yazdırabilirsiniz.
- MongoDB üzerinden bakiye ve QR kod verilerini yönetebilirsiniz.

---

## 📦 Gereksinimler

### Python
- Python 3.12 veya üstü önerilir.

### Paketler

```txt
fastapi==0.111.1
uvicorn==0.23.2
pydantic==2.6.2
pymongo==4.6.1
colorama==0.4.6
```

```shell
pip install -r requirements.txt
```



⚙️ MongoDB Yapısı
1. Kartlar (customers koleksiyonu)
```json
{
  "kart_id": "1135",
  "bakiye": 150.0,
  "tarih": "14-10-25"
}
```

2. İşlemler (transactions koleksiyonu)
```json
{
  "kart_id": "1135",
  "tutar": 50.0,
  "tarih": "14-10-25",
  "işlem": "Karta Para Yatırıldı."
}
```

3. QR Kodlar (qrcode koleksiyonu)
```json
{
  "qr_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "tip": "Yıkama",
  "tarih": "20251014 130000",
  "veri": "3fa85f64-5717-4562-b3fc-2c963f66afa6.yikama.20251014 130000",
  "kullanildi": false
}
```

veri formatı: UUID.HIZMET_TIPI.TIMESTAMP

# Çalıştırma

```bash
uvicorn main:app --reload
```


2️⃣ Kart Bakiyesi Sorgulama

Endpoint: /balance
Method: POST
Açıklama: Kart ID’ye göre bakiye sorgular. Kart yoksa hata döner.

Request (JSON):
```json
{
  "kart_id": "12345"
}
```

Response (Başarılı):
```json
{
  "kart_id": "12345",
  "balance": 50.0
}
```

Response (Kart yoksa):
```json
{
  "detail": "Kart bulunamadı"
}
```
3️⃣ Kart Bakiyesinden Para Düşme

Endpoint: /deduct_balance
Method: POST
Açıklama: Kart bakiyesinden QR program fiyatını düşer.

Request (JSON):
```json
{
  "kart_id": "12345",
  "qr_id": "b8f2e2a0-1234-4c56-9876-abcdef123456"
}
```

Response (Başarılı):
```json
{
  "kart_id": "12345",
  "remaining_balance": 48.0,
  "price_deducted": 2.0
}
```

Response (Yetersiz bakiye):
```json
{
  "detail": "Kart bakiyesi yetersiz"
}
```
4️⃣ QR Kod Durumu Sorgulama

Endpoint: /qr_status
Method: POST
Açıklama: QR kod var mı, kullanıldı mı sorgular.

Request (JSON):
```json
{
  "qr_id": "b8f2e2a0-1234-4c56-9876-abcdef123456"
}
```

Response (Başarılı):
```json
{
  "qr_id": "b8f2e2a0-1234-4c56-9876-abcdef123456",
  "tip": "cila",
  "kullanildi": false
}
```

Response (QR yoksa):
```json
{
  "detail": "QR kod bulunamadı"
}
```
5️⃣ QR Kod Kullanıldı Olarak İşaretleme

Endpoint: /mark_qr_used
Method: POST
Açıklama: QR kod kullanıldı olarak işaretler.

Request (JSON):
```json
{
  "kart_id": "12345",
  "qr_id": "b8f2e2a0-1234-4c56-9876-abcdef123456"
}
```

Response (Başarılı):
```json
{
  "status": "success",
  "qr_id": "b8f2e2a0-1234-4c56-9876-abcdef123456",
  "used": true
}
```

Response (Zaten kullanılmışsa):
```json
{
  "detail": "QR kod zaten kullanılmış"
}
```
6️⃣ Transaction Ekleme

Endpoint: /add_transaction
Method: POST
Açıklama: Kart ile yapılan işlemleri kaydeder.

Request (JSON):
```json
{
  "kart_id": "12345",
  "tutar": 2.0,
  "islem": "Cila programı kullanıldı"
}
```

Response (Başarılı):
```json
{
  "status": "success",
  "kart_id": "12345",
  "amount": 2.0,
  "operation": "Cila programı kullanıldı"
}
```