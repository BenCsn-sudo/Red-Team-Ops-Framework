# 🛡️ Red Team Ops Framework (RTOF)

**Framework de Pentest Automatisé & Audit de Sécurité Offensive**

## ⚠️ Avertissement Légal

> **L'utilisation de ce programme ne doit se faire que dans le cadre légal d'un audit de sécurité consenti.**
> Ce framework est conçu à des fins éducatives et pour l'audit de systèmes dont l'utilisateur est propriétaire ou pour lesquels il dispose d'une autorisation écrite explicite. L'auteur décline toute responsabilité en cas d'utilisation malveillante ou de dommages causés aux systèmes cibles.

---

## 📋 Description du Projet

**RTOF (Red Team Ops Framework)** est un outil modulaire développé en Python, conçu pour automatiser les phases critiques d'un audit de sécurité (Pentest). Il se distingue par son approche hybride, combinant la rapidité des sockets natifs pour la découverte et la précision de la librairie **Scapy** pour la manipulation fine de paquets TCP/IP.

L'objectif est de fournir une chaîne d'outils ("Kill Chain") automatisée permettant la reconnaissance, l'analyse de vulnérabilités et le stress-test (fuzzing) des pare-feu et services.

---

## 📂 Architecture Technique

```text
RTOF/
│
├── main.py                 # Point d'entrée CLI (Command Line Interface)
├── config.py               # Configuration globale (Timeouts, Threading)
│
├── modules/                # Cœur fonctionnel
│   ├── __init__.py
│   ├── network_scanner.py  # Phase 1 : Découverte (Sockets + Threading)
│   ├── stealth_scanner.py  # Phase 2 : Evasion (Scapy Packet Crafting)
│   ├── service_recon.py    # Phase 3 : Intelligence (OSINT / Banners)
│   └── fuzzer.py           # Phase 4 : Offensive (Stress Test / Payload Injection)
│
├── utils/                  # Utilitaires transverses
│   ├── logger.py           # Gestion des logs et affichage console
│   └── reporter.py         # Phase 5 : Moteur de génération de rapports
│
└── requirements.txt        # Dépendances Python

```

---

## 🛠️ Détail des Modules & Mécanismes

Cette section détaille le fonctionnement interne de chaque module pour les développeurs et auditeurs.

---

### Phase 1 : Network Scanner (Cartographie & Découverte)

**Fichier :** `modules/network_scanner.py`

* **Objectif :** Développer un scanner de ports TCP haute performance capable de cartographier une cible en quelques secondes.
* **Concept :** Utilisation du **TCP Connect Scan**. Il s'agit de la méthode standard pour établir une connexion réseau fiable. Le module tente d'initier un "3-way handshake" complet sur chaque port ciblé.

**📚 Bibliothèques Clés :**
* **`socket`** (Standard) : Interface réseau bas niveau native de Python.
  * *Pourquoi ?* Elle offre une interaction directe avec le noyau pour créer des connexions TCP/IP légères et rapides, sans le surcoût (overhead) des protocoles de haut niveau comme HTTP.

* **`concurrent.futures`** (Standard) : Gestion moderne du Threading.
  * *Pourquoi ?* Elle permet de paralléliser les tentatives de connexion. Au lieu de tester les ports un par un (séquentiel), nous lançons 100 "ouvriers" simultanés, réduisant le temps de scan total de plusieurs minutes à quelques secondes.

**💻 Commande d'utilisation :**
> Syntaxe : python3 main.py <IP_CIBLE> --mode scan
```bash
python3 main.py 192.168.1.15 --mode scan
```

**Fonctionnement Technique :**
1. Le scanner envoie un paquet **SYN**.
2. Si le port est ouvert, le serveur répond **SYN-ACK**.
3. Le scanner répond **ACK** (connexion validée), puis envoie immédiatement un **RST** (Reset) pour libérer la ressource et fermer proprement la connexion.

**Optimisation :** Scanner séquentiellement 65 535 ports est trop lent. Le module implémente le **Multithreading** via `concurrent.futures`, lançant jusqu'à 100 threads simultanés. Pendant qu'un thread attend une réponse réseau (I/O bound), les 99 autres continuent de tester d'autres ports.

---

### Phase 2 : Stealth Scanner (Évasion & Firewall Testing)

**Fichier :** `modules/stealth_scanner.py`

* **Objectif :** Contourner la journalisation standard et tester la granularité des règles de filtrage (Firewall).
* **Concept :** Utilisation de la librairie **Scapy** pour forger des paquets "sur mesure" (Packet Crafting), contournant la pile réseau standard du système d'exploitation.

**📚 Bibliothèques Clés :**
* **`scapy`** (Tierce partie) : Manipulation interactive de paquets.
  * *Pourquoi ?* Contrairement au module `socket` qui laisse le noyau (Kernel) gérer la conversation TCP (et impose donc le handshake complet), Scapy nous donne le contrôle total bit par bit. C'est ce qui permet d'envoyer un paquet `SYN` et de refuser      de répondre `ACK` ensuite, ou de créer des combinaisons de drapeaux "illégales" (Xmas) que le système d'exploitation refuserait normalement de créer.

* **`logging`** (Standard) : Gestion des messages système.
  * *Pourquoi ?* Utilisé ici pour faire taire (suppress) les avertissements verbeux de Scapy au démarrage, garantissant que l'interface de notre outil reste propre (Mode silencieux).

**💻 Commande d'utilisation :**
> **Note :** Ce mode nécessite des privilèges **root** pour créer des sockets bruts (Raw Sockets).

> Syntaxe : sudo python3 main.py <IP_CIBLE> --mode stealth
```bash
sudo ./venv/bin/python3 main.py 192.168.1.15 --mode stealth

```

**Fonctionnement Technique :**
* **SYN Scan (Half-open) :** Le module envoie un **SYN**. À la réception du **SYN-ACK**, il n'envoie jamais le dernier **ACK** mais un **RST** (Reset).
  * *Intérêt :* La connexion n'étant jamais totalement établie, elle n'apparaît souvent pas dans les logs applicatifs du serveur cible.

* **Firewall Rules Testing :** Envoi de paquets avec des combinaisons de drapeaux illogiques (ex: FIN + URG + PUSH, connu sous le nom de *Xmas Scan*).
  * *Intérêt :* Si le pare-feu laisse passer ces paquets aberrants, cela indique une configuration "Stateless" ou permissive.

* **L'analyse se base sur la réponse du système cible à des paquets hors-normes** : un pare-feu 'Stateful' bloquera ces paquets (silence), tandis qu'une configuration permissive les laissera atteindre l'hôte (génération d'un RST).

---

### Phase 3 : Service Recon (Intelligence & Banner Grabbing)

**Fichier :** `modules/service_recon.py`

* **Objectif :** Identifier précisément le logiciel et la version qui écoute derrière un port ouvert.
* **Concept :** Le **Banner Grabbing**. La simple connaissance d'un port ouvert (ex: 80) est insuffisante ; l'auditeur doit savoir s'il s'agit d'Apache 2.4 ou Nginx 1.18.

**📚 Bibliothèques Clés :**
* **`socket`** (Standard) : Communication réseau complète.
  * *Pourquoi ?* Contrairement à la phase de scan furtif, nous avons ici besoin d'une connexion TCP stable et complète gérée par le système d'exploitation. Cela nous permet d'envoyer des données applicatives (requêtes HTTP, commandes SMTP) et de lire       les réponses textuelles renvoyées par le service.

* **💻 Commande d'utilisation :**
>  Syntaxe : python3 main.py <IP_CIBLE> --mode recon
```bash
python3 main.py 192.168.1.15 --mode recon

```

**Fonctionnement Technique :**
1. **Connexion :** Établissement d'une connexion socket complète (3-way handshake) sur les ports ouverts.
2. **Écoute Passive :** Lecture des premiers octets envoyés spontanément par le serveur (bannière de bienvenue). C'est efficace pour SSH, FTP ou SMTP (ex: `220 (vsFTPd 3.0.3)`).
3. **Sondage Actif (HTTP) :** Pour les services silencieux comme le Web, envoi proactif d'une requête légère (`HEAD / HTTP/1.1`) pour forcer le serveur à révéler son identité dans les en-têtes HTTP (`Server: Apache/2.4.49`).

**Utilité :** Permet la corrélation immédiate avec des bases de données de vulnérabilités (CVE) publiques pour identifier des failles connues sur les versions détectées. (pouvoir rechercher "faille Apache 2.4.49)

---

### Phase 4 : Fuzzer (Offensive & Stress Test)

**Fichier :** `modules/fuzzer.py`

* **Objectif :** Tester la stabilité et la robustesse des services découverts (Crash Test) via l'injection de données massives.
* **Concept :** Le **Fuzzing**. Technique consistant à envoyer des données aléatoires, mal formées ou volumineuses pour provoquer des erreurs de gestion de mémoire (Buffer Overflow) ou de traitement logique.

**📚 Bibliothèques Clés :**

* **`socket`** (Standard) : Envoi de données brutes.
  * *Pourquoi ?* Permet d'envoyer des chaînes de caractères (payloads) qui ne respectent pas les standards du protocole (ex: une requête HTTP de 5000 caractères sans espaces), ce qu'un navigateur ou un client classique refuserait de faire.
* **`time`** (Standard) : Gestion de la temporisation.
  * *Pourquoi ?* Introduit un délai (sleep) entre chaque injection de payload. Cela permet de distinguer un crash réel d'une simple congestion réseau, et laisse le temps au service cible de traiter (ou d'échouer sur) la donnée précédente.

* **💻 Commande d'utilisation :**
> **Note :** Ce mode cible un service unique. L'argument `--port` est obligatoire.

> Syntaxe : python3 main.py <IP_CIBLE> --mode fuzz --port <PORT>
```bash
python3 main.py 192.168.1.15 --mode fuzz --port 8080
```

* **Fonctionnement Technique :**
1. **Génération de Payloads :** Création de chaînes d'octets de taille croissante (ex: pattern de 100, 500, ... 5000 octets "A").
2. **Injection :** Envoi du payload via socket dans le service cible.
3. **Surveillance (Monitoring) :** Si le socket se ferme brutalement (RST inattendu) ou ne répond plus (Timeout) après l'envoi, une instabilité (Crash/DoS) est détectée. Cela indique souvent que le payload a écrasé une zone mémoire critique de l'application.

* **Risque :** Peut entraîner un Déni de Service (DoS) temporaire sur la cible, nécessitant un redémarrage manuel du service affecté.

---

### Phase 5 : Reporting (Livrables)

**Fichier :** `utils/reporter.py`

* **Objectif :** Transformer les données techniques brutes en informations exploitables et persistantes.
* **Concept :** Agrégation structurée des résultats pour l'analyse post-audit. Un pentester doit pouvoir prouver ses découvertes : le rapport est la preuve.

**📚 Bibliothèques Clés :**
* **`json`** (Standard) : Format d'échange de données.
  * *Pourquoi ?* Le JSON est universel. Contrairement à un fichier texte simple, un rapport JSON peut être réimporter dans d'autres outils d'analyse, des tableaux de bord (Dashboards) ou parser par des scripts tiers. C'est le standard de l'industrie       pour l'interopérabilité.

* **`datetime`** (Standard) : Gestion du temps.
  * *Pourquoi ?* En sécurité, l'horodatage (Timestamping) est critique. Il faut savoir exactement *quand* une vulnérabilité a été détectée pour comparer l'évolution de la sécurité dans le temps (Audit Trail).


* **💻 Commande d'utilisation :**
> **Note :** Le reporting est **automatique**. Il se déclenche à la fin des modes `scan`, `stealth` et `recon`.
*Exemple de sortie console :*
```text
[+] Rapport sauvegardé avec succès : report_192.168.1.15_20231027_1430.json
```
* **Fonctionnement Technique :**
1. **Collecte :** Récupération des données en mémoire vive (RAM) issues des modules précédents (Liste des ports ouverts, Bannières récupérées, Notes de vulnérabilité).
2. **Structuration :** Organisation des données dans un dictionnaire Python imbriqué.
3. **Sérialisation :** Conversion du dictionnaire en format JSON et écriture sur le disque avec un nom de fichier unique basé sur l'IP cible et l'heure exacte.


---

C'est une étape cruciale car tes commandes actuelles dans le brouillon (`--mode full`, `--module`) ne correspondent pas au code que nous avons écrit (`--mode scan`, `--mode stealth`, etc.).

Il faut corriger cela pour refléter **exactement** la réalité de ton script et l'usage de l'environnement virtuel (`venv`), surtout pour le `sudo`.

Voici la section **Installation & Utilisation** mise à jour et corrigée :

---

## 🚀 Installation & Utilisation

### Prérequis

* **Système :** Linux (recommandé : Debian/Kali/Ubuntu) ou macOS.
* **Python :** Version 3.8 ou supérieure.
* **Privilèges :** Droits administrateur (`root` ou `sudo`) requis pour le module Stealth (Scapy).

### Installation

Nous recommandons l'utilisation d'un environnement virtuel pour éviter les conflits de dépendances.

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/RTOF.git
cd RTOF

# 2. Créer l'environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt

```

### Exemples d'utilisation

**1. Scan de découverte rapide (TCP Connect)**
Ne nécessite pas de droits root. Scanne les ports communs définis dans `config.py`.

```bash
python3 main.py 192.168.1.15 --mode scan

```

**2. Scan Furtif / Stealth (SYN Scan)**
Nécessite les droits root pour forger les paquets.

> **Note importante :** Avec `sudo`, il faut pointer vers l'exécutable Python de l'environnement virtuel.

```bash
sudo ./venv/bin/python3 main.py 192.168.1.15 --mode stealth

```

**3. Reconnaissance de Service (Banner Grabbing)**
Récupère les versions des services sur les ports ouverts.

```bash
python3 main.py 192.168.1.15 --mode recon

```

**4. Offensive (Fuzzing / Stress Test)**
Cible un port spécifique pour tester sa stabilité.

> **⚠️ Attention :** Peut provoquer un crash du service cible via Buffer Overflow.

```bash
# Syntaxe : --mode fuzz --port <PORT_UNIQUE>
python3 main.py 192.168.1.15 --mode fuzz --port 8080

```

---

## 🤝 Contribution

Les contributions sont les bienvenues. Merci de suivre les étapes suivantes :

1. Forker le projet.
2. Créer une branche de fonctionnalité (`git checkout -b feature/AmazingFeature`).
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`).
4. Push vers la branche (`git push origin feature/AmazingFeature`).
5. Ouvrir une Pull Request.
