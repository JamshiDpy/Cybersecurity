import socket
import threading
open_ports = []
def scan_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((ip, port))
        print(f"Port {port} is open")
        open_ports.append(port)
    except:
        pass
    finally:
        sock.close()

def scan_ports_fast(ip, port_list):
    threads = []
    for port in port_list:
        thread = threading.Thread(target=scan_port, args=(ip, port))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()



if __name__ == "__main__":
    target_ip = "192.168.x.x" # change this
    ports_to_scan = range(1, 10000)

    scan_ports_fast(target_ip, ports_to_scan)

    max_port = max(open_ports)
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((target_ip, max_port))
    connection.send("giv me flag".encode())
    flag = connection.recv(1024).decode()
    print(flag)
