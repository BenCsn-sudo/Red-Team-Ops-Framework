import socket
from concurrent.futures import ThreadPoolExecutor
from config import Colors, DEFAULT_TIMEOUT, MAX_THREADS

def scan_port(target_ip, port):
    """
    Tente de se connecter à un port spécifique sur une IP.
    Renvoie le numéro du port si ça fonctionne, sinon None.
    """
    try:
        # 1. Création du "téléphone" (le socket)
        # socket.AF_INET = On utilise IPv4 (ex: 192.168.1.1)
        # socket.SOCK_STREAM = On utilise le protocole TCP (fiable, connecté)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            # 2. Définition de la patience
            # Si le port ne répond pas après X secondes (DEFAULT_TIMEOUT), on abandonne.
            # C'est crucial pour ne pas bloquer le script indéfiniment.
            s.settimeout(DEFAULT_TIMEOUT)

            # 3. Tentative de connexion (le cœur du scan)
            # connect_ex est différent de connect().
            # connect() lève une erreur si ça échoue (pas pratique ici).
            # connect_ex() renvoie un code : 0 = Succès, autre chose = Échec.
            result = s.connect_ex((target_ip, port))

            if result == 0:
                return port  # Le port est ouvert !
    except Exception as e:
        pass  # En cas d'erreur imprévue, on ignore pour continuer le scan

    return None  # Le port est fermé ou filtré

def run_network_scan(target, ports):
    print(f"{Colors.BLUE}[*] Démarrage du scan TCP rapide sur {target}...{Colors.ENDC}")
    open_ports = []

    # 4. Gestion du parallélisme (Multi-threading)
    # ThreadPoolExecutor crée une "piscine" de travailleurs (threads).
    # Si MAX_THREADS = 50, on teste 50 ports simultanément au lieu d'un par un.
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        # 5. Distribution du travail
        # executor.map applique la fonction scan_port à chaque élément de la liste 'ports'.
        # L'usage de 'lambda p: ...' est une astuce pour passer l'argument 'target'
        # qui reste fixe, alors que 'p' change pour chaque port.
        results = executor.map(lambda p: scan_port(target, p), ports)

        # 6. Récupération des résultats
        # On boucle sur les réponses au fur et à mesure qu'elles arrivent.
        for port in results:
            if port:  # Si port n'est pas None (donc ouvert)
                print(f"    {Colors.GREEN}[+] Port {port} : OUVERT{Colors.ENDC}")
                open_ports.append(port)

    # Petit rapport final si rien n'est trouvé
    if not open_ports:
        print(f"{Colors.FAIL}[-] Aucun port ouvert trouvé (ou pare-feu actif).{Colors.ENDC}")

    return open_ports
