# config.py

# Configuration du Scanner
DEFAULT_TIMEOUT = 1.0       # Temps d'attente max par port (secondes)
MAX_THREADS = 100           # Nombre de threads simultanés (vitesse du scan)

# Ports communs à scanner par défaut si aucun n'est spécifié
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 3306, 3389, 8080]

# Couleurs pour le terminal (Code ANSI)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
