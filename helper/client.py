import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # FastAPI çalışıyorsa

# -------------------- 1. Fiyatları Çek --------------------
print("\n--- /pricing ---")
resp = requests.get(f"{BASE_URL}/pricing")
print(resp.status_code)
print(json.dumps(resp.json(), indent=4))

# -------------------- 2. Kart Bakiyesi Sorgula --------------------
print("\n--- /balance ---")
balance_data = {"kart_id": "12345"}  # Örnek kart ID
resp = requests.post(f"{BASE_URL}/balance", json=balance_data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=4))

# -------------------- 3. QR Kod Durumu --------------------
print("\n--- /qr_status ---")
qr_status_data = {"qr_id": "örnek-qr-id"}  # Örnek QR ID
resp = requests.post(f"{BASE_URL}/qr_status", json=qr_status_data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=4))

# -------------------- 4. Kart Bakiyesinden Para Düş --------------------
print("\n--- /deduct_balance ---")
deduct_data = {
    "kart_id": "12345",
    "qr_id": "örnek-qr-id"
}
resp = requests.post(f"{BASE_URL}/deduct_balance", json=deduct_data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=4))

# -------------------- 5. Transaction Kaydı Ekle --------------------
print("\n--- /add_transaction ---")
transaction_data = {
    "kart_id": "12345",
    "tutar": 5.0,
    "islem": "Test ödeme"
}
resp = requests.post(f"{BASE_URL}/add_transaction", json=transaction_data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=4))

# -------------------- 6. QR Kod Kullanıldı Olarak İşaretle --------------------
print("\n--- /mark_qr_used ---")
mark_qr_data = {
    "kart_id": "12345",
    "qr_id": "örnek-qr-id"
}
resp = requests.post(f"{BASE_URL}/mark_qr_used", json=mark_qr_data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=4))
