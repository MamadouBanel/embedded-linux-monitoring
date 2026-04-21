# embedded-linux-monitoring
Système de monitoring embarqué sous Linux
Acquisition de données capteurs et détection d'anomalies sur Raspberry Pi.
Description
Le système lit en continu les données d'un capteur ultrason (distance) et d'un capteur de température, applique une détection d'anomalies par fenêtre glissante, et affiche les résultats en temps réel. Une interface HTTP optionnelle permet de consulter l'état depuis un navigateur ou un autre système.
Le code est structuré en trois modules indépendants : acquisition, traitement, affichage. C'est le même principe qu'un système d'acquisition industriel — chaque couche a une seule responsabilité.
Matériel utilisé

Raspberry Pi4
Capteur ultrason HC-SR04
Capteur température/humidité DHT11
Câblage GPIO (diviseur de tension 1kΩ sur la pin ECHO)

Stack logiciel

Python
RPi.GPIO
Flask 
Bash

Structure du projet
embedded-linux-monitoring/
├── src/
│   ├── main.py        # Boucle principale, gestion des threads
│   ├── sensor.py      # Pilotes GPIO (HC-SR04, DHT11)
│   └── detector.py    # Détection d'anomalies (fenêtre glissante)
├── scripts/
│   └── start.sh       # Lancement en arrière-plan
└── README.md
Installation
bashgit clone https://github.com/MamadouBanel/embedded-linux-monitoring
cd embedded-linux-monitoring
pip3 install -r requirements.txt
Câblage HC-SR04 :

VCC → 5V (pin 2)
GND → GND (pin 6)
TRIG → GPIO 23 (pin 16)
ECHO → GPIO 24 (pin 18) via diviseur de tension

Utilisation
bashpython3 src/main.py           # Affichage console
python3 src/main.py --http    # Console + serveur HTTP sur le port 5000
Exemple de sortie
[2025-04-21 09:14:02] Distance : 43.2 cm | Temp : 22.1°C | Statut : OK
[2025-04-21 09:14:03] Distance : 18.7 cm | Temp : 22.1°C | Statut : ALERTE - objet trop proche
[2025-04-21 09:14:05] Distance : 55.0 cm | Temp : 22.2°C | Statut : OK
Points techniques
Pilote capteur (sensor.py) :
Mesure de l'impulsion écho du HC-SR04 avec time.perf_counter() pour la précision. Conversion durée → distance : d = t × 34300 / 2.
Détection d'anomalies (detector.py) :
Fenêtre glissante sur les N derniers échantillons. L'anomalie est déclenchée si K lectures consécutives dépassent le seuil — ça évite les faux positifs sur des pics isolés.
Concurrence :
L'acquisition tourne dans un thread séparé (threading.Thread). Un verrou (threading.Lock) protège les données partagées.
Améliorations possibles

Journalisation dans une base SQLite
Publication via MQTT vers un broker distant
Détection ML (isolation forest)
Dashboard web (Flask + Chart.js)

Auteur
Mamadou Banel — mamadoubanel2@gmail.com
