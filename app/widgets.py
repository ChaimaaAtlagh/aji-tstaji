"""
widgets.py
BoutonModerne : bouton compact à coins arrondis, icône optionnelle et
effet de survol discret, dessiné avec un Canvas (ttk ne fait pas de coins arrondis).
"""

import tkinter as tk
from tkinter import font as tkfont

from app import theme

RAYON = 12
POLICE_BOUTON = (theme.POLICE, 10, "bold")


def _rectangle_arrondi(canvas, x1, y1, x2, y2, rayon, **options):
    """Dessine un rectangle à coins arrondis sur un Canvas."""
    points = [
        x1 + rayon, y1, x2 - rayon, y1, x2, y1, x2, y1 + rayon,
        x2, y2 - rayon, x2, y2, x2 - rayon, y2, x1 + rayon, y2,
        x1, y2, x1, y2 - rayon, x1, y1 + rayon, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **options)


class BoutonModerne(tk.Canvas):
    """Bouton compact à coins arrondis. Remplace ttk.Button pour un rendu premium."""

    def __init__(self, parent, texte, commande, style="principal", icone=None,
                 hauteur=36, fond_parent=None):
        fond_parent = fond_parent or theme.BLANC
        super().__init__(parent, height=hauteur, bg=fond_parent,
                         highlightthickness=0, cursor="hand2")
        self.commande = commande
        self.texte = texte
        self.icone = icone
        self.hauteur = hauteur
        self.survole = False

        if style == "principal":
            self.fond, self.fond_survol = theme.BLEU, theme.BLEU_FONCE
            self.couleur_texte, self.bordure = theme.BLANC, None
        elif style == "fantome":
            # Bouton discret, sans fond, juste un texte + icône (ex. "Voir le site")
            self.fond, self.fond_survol = fond_parent, theme.FOND
            self.couleur_texte, self.bordure = theme.TEXTE_CLAIR, None
        else:  # "secondaire"
            self.fond, self.fond_survol = theme.BLANC, theme.BLEU_CLAIR
            self.couleur_texte, self.bordure = theme.BLEU, theme.BLEU

        contenu = f"{icone}  {texte}" if icone else texte
        largeur_texte = tkfont.Font(font=POLICE_BOUTON).measure(contenu)
        self.largeur = largeur_texte + 34
        self.configure(width=self.largeur)

        self._dessiner()
        self.bind("<Enter>", self._entrer)
        self.bind("<Leave>", self._sortir)
        self.bind("<Button-1>", self._clic)

    def _dessiner(self):
        self.delete("all")
        couleur = self.fond_survol if self.survole else self.fond
        contour = {"outline": self.bordure, "width": 1.3} if self.bordure else {"outline": ""}
        _rectangle_arrondi(self, 1, 1, self.largeur - 1, self.hauteur - 1, RAYON,
                           fill=couleur, **contour)
        contenu = f"{self.icone}  {self.texte}" if self.icone else self.texte
        self.create_text(self.largeur / 2, self.hauteur / 2, text=contenu,
                         fill=self.couleur_texte, font=POLICE_BOUTON)

    def _entrer(self, evenement):
        self.survole = True
        self._dessiner()

    def _sortir(self, evenement):
        self.survole = False
        self._dessiner()

    def _clic(self, evenement):
        if self.commande:
            self.commande()