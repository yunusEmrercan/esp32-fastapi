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





# # Kullanım Örneği

📌 API Endpoints
1. Kart Bakiyesi Sorgulama

POST /bakiye
Request Body:
```json
{
  "kart_id": 1135
}
```

Response:
```json
{
  "kart_id": 1135,
  "bakiye": 150.0,
  "bulundu": true
}
```

2. QR Kod Bilgisi Sorgulama

POST /qr
Request Body:
```json
{
  "qr_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

Response:
```json
{
  "qr_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "hizmet_tipi": "yikama",
  "kullanildi": false
}
```