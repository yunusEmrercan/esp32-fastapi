# client.py
import requests
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://127.0.0.1:8000"

def print_success(msg):
    print(Fore.GREEN + msg)

def print_error(msg):
    print(Fore.RED + msg)

def print_info(msg):
    print(Fore.CYAN + msg)

# ------------------ Kart Endpoint ------------------
def check_balance(kart_id):
    print_info(f"\n[Kart sorgulama] kart_id={kart_id}")
    response = requests.post(f"{BASE_URL}/kart", json={"kart_id": kart_id})
    data = response.json()
    if data.get("status"):
        print(data)

        print_success(f"Bakiye: {data.get('bakiye')} TL")
    else:
        print(data)

        print_error(f"Hata: {data.get('message')}")

def use_program(kart_id, program):
    print_info(f"\n[Program kullanımı] kart_id={kart_id}, program={program}")
    response = requests.post(f"{BASE_URL}/kart", json={"kart_id": kart_id, "program": program})
    data = response.json()
    if data.get("status"):
        print(data)

        print_success(f"Kalan bakiye: {data.get('bakiye')} TL, Program süresi: {data.get('time')} sn")
    else:
        print(data)

        print_error(f"Hata: {data.get('message')}")

# ------------------ QR Endpoint ------------------
def check_qr(qr_verisi):
    print_info(f"\n[QR sorgulama] qr={qr_verisi}")
    response = requests.post(f"{BASE_URL}/qr", json={"qr_id": qr_verisi})
    data = response.json()
    if data.get("status"):
        print(data)
        print_success(f"Program: {data.get('program')}, Süre: {data.get('time')} sn")
    else:
        print(data)
        print_error(f"Hata: {data.get('message')}")

# ------------------ Örnek Kullanım ------------------
if __name__ == "__main__":
    # Örnek kart ve program testleri
    check_balance(1235)
    use_program(1235, "cila")
    check_balance(13235)

    # Örnek QR testleri
    check_qr("qr001.cila.20251016_2205")
    check_qr("benzersizID2.cila.20251016_2140")
