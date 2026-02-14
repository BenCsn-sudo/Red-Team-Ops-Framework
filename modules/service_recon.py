import socket
from config import Colors, DEFAULT_TIMEOUT

def get_banner(target, port):
    try:
        # On établit une vraie connexion pour discuter
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2) # Un peu plus long pour laisser le temps au serveur de répondre
        s.connect((target, port))

        # Cas spécifique pour le Web (HTTP)
        # Les serveurs web ne parlent pas en premier, il faut leur demander
        if port in [80, 443, 8080, 8000]:
            # On envoie une requête HEAD (juste les en-têtes)
            payload = b"HEAD / HTTP/1.1\r\nHost: " + target.encode() + b"\r\n\r\n"
            s.send(payload)

        # On écoute la réponse (max 1024 octets)
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        s.close()
        return banner

    except Exception:
        return None

def run_service_recon(target, ports):
    print(f"{Colors.BLUE}[*] Démarrage de la reconnaissance de services (Fingerprinting)...{Colors.ENDC}")

    results = {} # Dictionnaire pour stocker les résultats

    for port in ports:
        banner = get_banner(target, port)

        if banner:
            clean_banner = banner.split('\n')[0]
            print(f"    {Colors.GREEN}[+] Port {port} : {clean_banner}{Colors.ENDC}")
            results[port] = clean_banner # On stocke
        else:
            print(f"    {Colors.WARNING}[?] Port {port} : Pas de bannière détectée{Colors.ENDC}")
            results[port] = "Unknown"

    return results # IMPORTANT : On retourne le dictionnaire
