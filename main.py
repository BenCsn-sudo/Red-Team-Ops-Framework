# main.py
import sys
import argparse
from config import Colors
from modules.network_scanner import run_network_scan
from config import Colors, COMMON_PORTS
from modules.stealth_scanner import run_stealth_scan
from modules.service_recon import run_service_recon
from modules.fuzzer import run_fuzzer
from utils.reporter import save_report

def print_banner():
    banner = rf"""{Colors.BOLD}{Colors.FAIL}
    ____  ______ ____  ______
   / __ \/_  __// __ \/ ____/
  / /_/ / / /  / / / / /_
 / _, _/ / /  / /_/ / __/
/_/ |_| /_/   \____/_/
    Red Team Ops Framework
    {Colors.ENDC}"""
    print(banner)
    print(f"{Colors.BLUE}[*] Initialisation du Framework...{Colors.ENDC}")

def main():
    print_banner()

    # Configuration des arguments ligne de commande (CLI)
    parser = argparse.ArgumentParser(description="Outil de Pentest Automatisé")
    parser.add_argument("target", help="Adresse IP cible (ex: 192.168.1.1)")
    parser.add_argument("--mode", help="Mode de scan", choices=["scan", "stealth", "recon", "fuzz"], default="scan")
    parser.add_argument("--port", help="Port spécifique pour le scan ou le fuzzing (ex: 8080)")

    args = parser.parse_args()

    print(f"{Colors.GREEN}[+] Cible verrouillée : {args.target}{Colors.ENDC}")
    print(f"{Colors.GREEN}[+] Mode sélectionné : {args.mode}{Colors.ENDC}")

    # ... (le début du fichier ne change pas)

    # Variables pour stocker les résultats du rapport
    scanned_ports = []
    banners = {}

    # Logique de routage
    if args.mode == "scan":
        print(f"{Colors.BLUE}[*] Mode : Découverte (TCP Connect Scan){Colors.ENDC}")
        scanned_ports = run_network_scan(args.target, COMMON_PORTS)
        # On sauvegarde le rapport immédiatement après un scan
        save_report(args.target, scanned_ports)

    elif args.mode == "stealth":
        print(f"{Colors.BLUE}[*] Mode : Évasion & Stealth (Scapy SYN Scan){Colors.ENDC}")
        scanned_ports = run_stealth_scan(args.target, COMMON_PORTS)
        save_report(args.target, scanned_ports, vuln_notes=["Stealth scan performed"])

    elif args.mode == "recon":
        print(f"{Colors.BLUE}[*] Mode : Reconnaissance de Service (Banner Grabbing){Colors.ENDC}")
        # On assume qu'on scanne les ports communs pour l'exemple
        banners = run_service_recon(args.target, COMMON_PORTS)
        # On extrait juste les ports qui ont répondu pour la liste "open_ports"
        scanned_ports = list(banners.keys())
        save_report(args.target, scanned_ports, banners=banners)

    elif args.mode == "fuzz":
        print(f"{Colors.BLUE}[*] Mode : Offensive (Fuzzing / Stress Test){Colors.ENDC}")
        run_fuzzer(args.target, args.port)
        # Le fuzzing ne génère pas de rapport JSON pour l'instant (c'est du live testing)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Interruption utilisateur. Arrêt.")
        sys.exit()
