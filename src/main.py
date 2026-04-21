# main.py — Système de monitoring embarqué sous Linux
# Raspberry Pi
#
# Utilisation :
#   python3 main.py           -> affichage console uniquement
#   python3 main.py --http    -> console + serveur HTTP sur le port 5000
 
import time
import threading
import argparse
import datetime
from sensor import initialiser, lire_distance_cm, lire_temperature_c, nettoyer
from detector import DetecteurAnomalie
 
INTERVALLE_S = 1.0  # période d'acquisition en secondes
 
# Données partagées entre les threads (protégées par un verrou)
_verrou = threading.Lock()
_etat = {
    "distance_cm": 0.0,
    "temperature_c": 0.0,
    "anomalie": False,
    "horodatage": "",
}
 
 
def boucle_acquisition(detecteur: DetecteurAnomalie, stop: threading.Event):
    """Thread d'acquisition : lit les capteurs et met à jour l'état partagé."""
    initialiser()
    try:
        while not stop.is_set():
            distance = lire_distance_cm()
            temperature = lire_temperature_c()
            anomalie = detecteur.mise_a_jour(distance)
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
            with _verrou:
                _etat["distance_cm"] = distance
                _etat["temperature_c"] = temperature
                _etat["anomalie"] = anomalie
                _etat["horodatage"] = ts
 
            time.sleep(INTERVALLE_S)
    finally:
        nettoyer()
 
 
def boucle_affichage(stop: threading.Event):
    """Thread principal : affiche les mesures formatées dans le terminal."""
    while not stop.is_set():
        time.sleep(INTERVALLE_S)
        with _verrou:
            d = _etat["distance_cm"]
            t = _etat["temperature_c"]
            a = _etat["anomalie"]
            ts = _etat["horodatage"]
 
        statut = "ALERTE - objet trop proche" if a else "OK"
        print(f"[{ts}] Distance : {d:5.1f} cm | Temp : {t:.1f}°C | Statut : {statut}")
 
 
def demarrer_serveur_http():
    """Serveur Flask optionnel — expose /etat en JSON."""
    try:
        from flask import Flask, jsonify
        app = Flask(__name__)
 
        @app.route("/etat")
        def etat():
            with _verrou:
                return jsonify(_etat)
 
        t = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=5000),
            daemon=True
        )
        t.start()
        print("[HTTP] Serveur démarré sur http://0.0.0.0:5000/etat")
    except ImportError:
        print("[HTTP] Flask non installé — serveur HTTP désactivé")
 
 
def main():
    parser = argparse.ArgumentParser(description="Système de monitoring embarqué Linux")
    parser.add_argument("--http", action="store_true", help="Activer l'interface HTTP")
    args = parser.parse_args()
 
    detecteur = DetecteurAnomalie(seuil_bas=20.0, seuil_haut=150.0)
    stop = threading.Event()
 
    thread_acq = threading.Thread(
        target=boucle_acquisition, args=(detecteur, stop), daemon=True
    )
    thread_acq.start()
 
    if args.http:
        demarrer_serveur_http()
 
    print("Système de monitoring démarré — Ctrl+C pour arrêter\n")
    try:
        boucle_affichage(stop)
    except KeyboardInterrupt:
        print("\nArrêt en cours...")
        stop.set()
        thread_acq.join(timeout=2)
 
 
if __name__ == "__main__":
    main()
 
