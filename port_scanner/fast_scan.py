import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from typing import List

# Ochilgan portlarni saqlash uchun ro'yxat
open_ports = []

# Thread-safe lock for open_ports
lock = threading.Lock()

def scan_port(ip: str, port: int) -> None:
    """
    Berilgan IP va portni skanerlaydi.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)  # Tezroq skanerlash uchun timeout qisqa
    try:
        result = sock.connect_ex((ip, port))
        if result == 0:  # Agar port ochiq bo'lsa
            with lock:
                open_ports.append(port)
    except Exception:
        pass  # Xatolarni jim ushlash
    finally:
        sock.close()

def scan_ports_fast(ip: str, port_list: List[int]) -> None:
    """
    Portlarni parallel ravishda skanerlaydi, CPU yadrolariga qarab moslashadi.
    """
    max_workers = multiprocessing.cpu_count() * 2  # Optimal ishlash uchun
    print(f"Scanning {len(port_list)} ports with {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scan_port, ip, port) for port in port_list]
        # Barcha vazifalar tugashini kutamiz
        for future in futures:
            future.result()

def get_ports_from_input(port_input: str) -> List[int]:
    """
    Foydalanuvchi kiritgan port ma'lumotlarini tahlil qiladi.
    """
    if port_input.lower() == 'a':
        return list(range(1, 65536))  # Barcha portlar (1-65535)
    elif ',' in port_input:
        try:
            return [int(port.strip()) for port in port_input.split(',') if port.strip().isdigit()]
        except ValueError:
            print("Invalid port list format. Using default range (1-10000).")
            return list(range(1, 10001))
    else:
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                return [port]
            else:
                print("Port must be between 1 and 65535. Using default range (1-10000).")
                return list(range(1, 10001))
        except ValueError:
            print("Invalid port input. Using default range (1-10000).")
            return list(range(1, 10001))

if __name__ == "__main__":
    # IP manzilni kiritish
    target_ip = input("Enter target IP address: ").strip()
    
    # IP formatini tekshirish (oddiy tekshirish)
    if not all(part.isdigit() and 0 <= int(part) <= 255 for part in target_ip.split('.') if len(target_ip.split('.')) == 4):
        print("Invalid IP address format. Exiting.")
        exit(1)

    # Port ma'lumotlarini kiritish
    port_input = input("Enter port(s) to scan (e.g., '80', '80,443,8080', or 'a' for all ports): ").strip()
    ports_to_scan = get_ports_from_input(port_input)

    scan_ports_fast(target_ip, ports_to_scan)

    # Barcha ochiq portlarni tartiblangan holda chop etish
    if open_ports:
        print("\nOpen ports found:")
        for port in sorted(open_ports):
            print(f"Port {port} is open")
    else:
        print("\nNo open ports found.")
