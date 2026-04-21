# sensor.py — Pilotes GPIO pour HC-SR04 (ultrason) et DHT11 (température)
# Raspberry Pi / Linux

import time
import threading

try:
    import RPi.GPIO as GPIO
    SIMULATION = False
except ImportError:
    # Permet de tester le code sur un PC sans Raspberry Pi
    SIMULATION = True
    print("[capteur] RPi.GPIO introuvable — mode simulation activé")

BROCHE_TRIG = 23
BROCHE_ECHO = 24
VITESSE_SON_CM_S = 34300  # à ~20°C


def initialiser():
    if SIMULATION:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BROCHE_TRIG, GPIO.OUT)
    GPIO.setup(BROCHE_ECHO, GPIO.IN)
    GPIO.output(BROCHE_TRIG, False)
    time.sleep(0.05)


def lire_distance_cm() -> float:
    """
    Mesure la distance avec le capteur ultrason HC-SR04.
    Retourne la distance en centimètres, ou -1.0 en cas de timeout.
    """
    if SIMULATION:
        import random
        return round(random.uniform(10.0, 80.0), 1)

    # Impulsion trigger de 10 µs
    GPIO.output(BROCHE_TRIG, True)
    time.sleep(0.00001)
    GPIO.output(BROCHE_TRIG, False)

    # Attente front montant de l'écho (timeout 0.1 s)
    timeout = time.perf_counter() + 0.1
    while GPIO.input(BROCHE_ECHO) == 0:
        debut_impulsion = time.perf_counter()
        if debut_impulsion > timeout:
            return -1.0

    # Attente front descendant de l'écho
    timeout = time.perf_counter() + 0.1
    while GPIO.input(BROCHE_ECHO) == 1:
        fin_impulsion = time.perf_counter()
        if fin_impulsion > timeout:
            return -1.0

    duree = fin_impulsion - debut_impulsion
    distance = (duree * VITESSE_SON_CM_S) / 2
    return round(distance, 1)


def lire_temperature_c() -> float:
    """
    Lecture température DHT11.
    En production : utiliser la bibliothèque adafruit_dht.
    """
    if SIMULATION:
        import random
        return round(random.uniform(20.0, 28.0), 1)
    return 0.0


def nettoyer():
    if not SIMULATION:
        GPIO.cleanup()
