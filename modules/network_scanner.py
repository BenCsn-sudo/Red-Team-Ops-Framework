import socket
from concurrent.futures import ThreadPoolExecutor
from config import Colors, DEFAULT_TIMEOUT, MAX_THREADS

def scan_port(target_ip, port):
    try:
        # CORRECTION ICI : On utilise socket.AF_INET et non socket.socket.AF_INET
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(DEFAULT_TIMEOUT)
            result = s.connect_ex((target_ip, port))
            if result == 0:
                return port
    except Exception as e:
        # On garde le debug au cas où, mais ça ne devrait plus planter
        # print(f"Erreur port {port}: {e}")
        pass
    return None

def run_network_scan(target, ports):
    print(f"{Colors.BLUE}[*] Démarrage du scan TCP rapide sur {target}...{Colors.ENDC}")
    open_ports = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = executor.map(lambda p: scan_port(target, p), ports)

        for port in results:
            if port:
                print(f"    {Colors.GREEN}[+] Port {port} : OUVERT{Colors.ENDC}")
                open_ports.append(port)

    if not open_ports:
        print(f"{Colors.FAIL}[-] Aucun port ouvert trouvé (ou pare-feu actif).{Colors.ENDC}")

    return open_ports
