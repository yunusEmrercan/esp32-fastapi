# Kart & QR API Dökümantasyonu

**Base URL:** `http://<sunucu-ip>:8000`

API, **kart bakiyesi sorgulama**, **program kullanımı** ve **QR kod doğrulama** işlemleri için iki ana endpoint sağlar.

---

## 1. Kart Endpoint

### URL

`POST /kart`

### Açıklama

* Sadece `kart_id` gönderildiğinde → kartın bakiyesini döner.
* `kart_id` + `program` gönderildiğinde → kart bakiyesinden program fiyatını düşer ve program süresini döner.

### Request

```json
{
  "kart_id": 1235,
  "program": "cila"    // opsiyonel
}
```

### Response

#### Sadece bakiye sorgu:

```json
{
  "status": true,
  "bakiye": 93.0
}
```

#### Program kullanımı:

```json
{
  "status": true,
  "bakiye": 91.0,
  "time": 30
}
```

#### Hatalı durumlar:

```json
{
  "status": false,
  "message": "1" // Yetersiz Bakiye
}

{
  "status": false,
  "message": "2" // Kart Bulunamadı
}

{
  "status": false,
  "message": "3" // Program Bulunamadı
}
```

---

## 2. QR Endpoint

### URL

`POST /qr`

### Açıklama

* QR verisi (`veri` alanı) gönderildiğinde, QR kontrol edilir.
* Kullanılmamış ise QR kullanılır ve program adı + süresi döner.
* Kullanılmış veya geçersiz QR’lar hata mesajı döner.

### Request

```json
{
  "qr_id": "benzersizid1.cila.20251016_2130"
}
```

### Response

#### Başarılı kullanım:

```json
{
  "status": true,
  "program": "cila",
  "time": 30
}
```

#### Hatalı durumlar:

```json
{
  "status": false,
  "message": "4" // QR Bulunamadı
}

{
  "status": false,
  "message": "5" // QR kod zaten kullanılmış
}
```

---

## 3. Database Yapısı

### Customers

```json
{
  "kart_id": 1235,
  "bakiye": 100
}
```

### Pricing

```json
{
  "program": "cila",
  "price": 2,
  "active": true
}
```

### Times

```json
{
  "program": "cila",
  "time": 30
}
```

### QR Codes

```json
{
  "qr_id": "benzersizid1.cila.20251016_2130",
  "veri": "benzersizid1.cila.20251016_2130",
  "tip": "cila",
  "tarih": "2025-10-16 22:05:00",
  "kullanildi": false
}
```

> **Not:** Tüm veriler küçük harf olmalıdır.



---

## 4. Örnek Kullanım (Python + requests)

```python
import requests

BASE_URL = "http://<sunucu-ip>:8000"

# 1. Kart bakiye sorgu
r = requests.post(f"{BASE_URL}/kart", json={"kart_id": 1235})
print(r.json())

# 2. Program kullanımı
r = requests.post(f"{BASE_URL}/kart", json={"kart_id": 1235, "program": "cila"})
print(r.json())

# 3. QR sorgu
r = requests.post(f"{BASE_URL}/qr", json={"qr_id": "benzersizid1.cila.20251016_2130"})
print(r.json())
```
