import json
import os
from datetime import datetime
from config import Colors

def save_report(target, scanned_ports, banners=None, vuln_notes=None):
    """
    Génère un rapport JSON structuré.
    """
    report_data = {
        "target": target,
        "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "open_ports": scanned_ports,
        "banners": banners if banners else {},
        "notes": vuln_notes if vuln_notes else []
    }

    # Création du nom de fichier unique
    filename = f"report_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=4)

        print(f"\n{Colors.BOLD}{Colors.GREEN}[+] Rapport sauvegardé avec succès : {filename}{Colors.ENDC}")
        print(f"{Colors.BLUE}[i] Contenu JSON :{Colors.ENDC}")
        print(json.dumps(report_data, indent=4))

    except Exception as e:
        print(f"{Colors.FAIL}[!] Erreur lors de la sauvegarde du rapport : {e}{Colors.ENDC}")
