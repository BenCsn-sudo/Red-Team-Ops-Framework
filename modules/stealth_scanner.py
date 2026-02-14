import logging
# On fait taire Scapy qui est très bavard au démarrage
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from scapy.all import IP, TCP, sr1, send
from config import Colors

def stealth_scan_port(target, port):
    try:
        # 1. Forger le paquet SYN (l'enveloppe)
        # IP() : On définit la destination
        # TCP() : On définit le port et le drapeau "S" (SYN)
        packet = IP(dst=target)/TCP(dport=port, flags="S")

        # 2. Envoyer et attendre UNE seule réponse (sr1)
        # timeout=1 : On attend 1 seconde max
        # verbose=0 : On ne veut pas de blabla dans le terminal
        response = sr1(packet, timeout=1, verbose=0)

        if response:
            # 3. Analyser la réponse
            if response.haslayer(TCP):
                # On regarde les drapeaux de la réponse (Flags)
                # 0x12 correspond à SYN+ACK (Le port est ouvert)
                if response.getlayer(TCP).flags == 0x12:

                    # 4. L'Astuce Stealth : On envoie un RST (Reset)
                    # On coupe la connexion avant qu'elle ne soit "officielle"
                    rst_packet = IP(dst=target)/TCP(dport=port, flags="R")
                    send(rst_packet, verbose=0)

                    return True

                # Si on reçoit RST+ACK (0x14), le port est fermé.
        return False

    except PermissionError:
        # Scapy a besoin d'être root pour créer des paquets bruts
        return None
    except Exception:
        return False

def run_stealth_scan(target, ports):
    print(f"{Colors.BLUE}[*] Démarrage du Scan Furtif (SYN) sur {target}...{Colors.ENDC}")
    open_ports = []

    # Pour le stealth, on évite le multithreading massif pour ne pas alerter les IPS
    # On scanne un par un (c'est plus lent mais plus discret)
    for port in ports:
        result = stealth_scan_port(target, port)

        if result is None:
            print(f"{Colors.FAIL}[!] Erreur : Droits root requis (sudo) pour le mode stealth.{Colors.ENDC}")
            return []

        if result:
            print(f"    {Colors.GREEN}[+] Port {port} : OUVERT (Stealth){Colors.ENDC}")
            open_ports.append(port)

    if not open_ports:
        print(f"{Colors.FAIL}[-] Aucun port ouvert trouvé.{Colors.ENDC}")

    return open_ports
