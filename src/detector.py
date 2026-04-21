# detector.py — Détection d'anomalies par fenêtre glissante

from collections import deque


class DetecteurAnomalie:
    """
    Déclenche une anomalie quand une valeur dépasse un seuil
    pendant K lectures consécutives dans une fenêtre de taille N.

    Ça évite les faux positifs sur des pics isolés dus au bruit capteur.
    """

    def __init__(self, seuil_bas=20.0, seuil_haut=200.0,
                 taille_fenetre=5, consecutifs_requis=3):
        self.seuil_bas = seuil_bas
        self.seuil_haut = seuil_haut
        self.taille_fenetre = taille_fenetre
        self.consecutifs_requis = consecutifs_requis
        self._fenetre = deque(maxlen=taille_fenetre)

    def mise_a_jour(self, valeur: float) -> bool:
        """
        Ajoute une nouvelle mesure.
        Retourne True si une anomalie est détectée.
        """
        if valeur < 0:
            return False  # Erreur capteur, on ignore

        self._fenetre.append(valeur)

        if len(self._fenetre) < self.consecutifs_requis:
            return False

        recents = list(self._fenetre)[-self.consecutifs_requis:]
        return all(
            v < self.seuil_bas or v > self.seuil_haut
            for v in recents
        )

    def reinitialiser(self):
        self._fenetre.clear()
