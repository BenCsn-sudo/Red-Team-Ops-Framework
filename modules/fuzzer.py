import socket
import time
from config import Colors, DEFAULT_TIMEOUT

def fuzz_service(target, port):
    print(f"{Colors.BLUE}[*] Démarrage du Fuzzer sur {target}:{port}{Colors.ENDC}")

    # On prépare des payloads de taille croissante
    # Une liste de buffers remplis de "A" (0x41)
    buffers = [
        "A" * 100,
        "A" * 500,
        "A" * 1000,
        "A" * 2000,
        "A" * 5000
    ]

    for payload in buffers:
        try:
            print(f"    Sending payload length: {len(payload)} bytes...")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(DEFAULT_TIMEOUT)
            s.connect((target, int(port)))

            # Envoi du payload
            s.send((payload + "\r\n").encode())

            # On lit la réponse (si le serveur répond, c'est qu'il est vivant)
            response = s.recv(1024)
            s.close()

            # Petite pause pour ne pas saturer le réseau
            time.sleep(0.5)

        except Exception as e:
            print(f"{Colors.FAIL}[!] Le service a cessé de répondre après {len(payload)} bytes !{Colors.ENDC}")
            print(f"{Colors.FAIL}[!] Crash potentiel ou protection active : {e}{Colors.ENDC}")
            return

    print(f"{Colors.GREEN}[*] Test terminé. Le service semble robuste.{Colors.ENDC}")

# Wrapper pour garder la même structure que les autres modules
# Mais ici on s'attend à recevoir un port unique via l'argument --port qu'on va ajouter
def run_fuzzer(target, port):
    if not port:
        print(f"{Colors.FAIL}[!] Erreur : Vous devez spécifier un port avec --port pour le fuzzing.{Colors.ENDC}")
        return
    fuzz_service(target, port)
