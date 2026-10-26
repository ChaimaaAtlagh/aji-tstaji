"""
entreprises.py
Page « Entreprises » : cartes d'entreprises (2 colonnes) avec recherche, filtres et tri.
Le dataset (app.donnees) est lu, jamais modifié.
"""

import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

import pandas as pd

from app import theme
from app.widgets import BoutonModerne

VIDE = "-"
VALEURS_VIDES = {"", "Non renseigné", "A_CONFIRMER"}
TOUS_DOMAINES = "Tous les domaines"
TOUS_QUARTIERS = "Tous les quartiers"
POLICE_EMOJI = "Segoe UI Emoji"

COLONNES_RECHERCHE = ["Nom_Entreprise", "Domaine", "Sous_Domaine", "Adresse", "Quartier"]

TRIS = {
    "Meilleur rating": (["Rating", "Nb_Avis"], [False, False]),
    "Plus d'avis": (["Nb_Avis", "Rating"], [False, False]),
    "Nom (A-Z)": (["Nom_Entreprise"], [True]),
}

NB_COLONNES = 2


def texte(valeur):
    """Remplace une valeur vide/non renseignée par '-', sans toucher au dataset."""
    if pd.isna(valeur) or str(valeur).strip() in VALEURS_VIDES:
        return VIDE
    return str(valeur)


def texte_quartier(valeur):
    """Le quartier 'A_CONFIRMER' s'affiche 'Non confirmé' (affichage seulement)."""
    if pd.isna(valeur) or str(valeur).strip() in ("", "A_CONFIRMER"):
        return "Non confirmé"
    return str(valeur)


class Entreprises(tk.Frame):
    """Page Entreprises : filtres en haut, cartes en dessous, sur 2 colonnes."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=theme.FOND)
        self.app = app

        self._creer_titre()
        self._creer_filtres()
        self.compteur = tk.Label(self, text="", font=theme.PETIT,
                                 fg=theme.TEXTE_CLAIR, bg=theme.FOND)
        self.compteur.pack(anchor="w", padx=50, pady=(0, 10))
        self._creer_zone_cartes()

    # ---------- CONSTRUCTION ----------
    def _creer_titre(self):
        tk.Label(self, text="Entreprises", font=theme.TITRE, fg=theme.MARINE,
                 bg=theme.FOND).pack(anchor="w", padx=50, pady=(25, 0))
        tk.Label(self, text="Recherche, filtre et postule directement depuis une carte.",
                 font=theme.NORMAL, fg=theme.TEXTE_CLAIR,
                 bg=theme.FOND).pack(anchor="w", padx=50, pady=(0, 14))

    def _creer_filtres(self):
        carte = tk.Frame(self, bg=theme.BLANC,
                         highlightbackground=theme.BORDURE, highlightthickness=1)
        carte.pack(fill="x", padx=50, pady=(0, 10))
        ligne = tk.Frame(carte, bg=theme.BLANC)
        ligne.pack(fill="x", padx=14, pady=12)

        donnees = self.app.donnees
        domaines = sorted(donnees["Domaine"].dropna().unique())
        quartiers = sorted(q for q in donnees["Quartier"].dropna().unique()
                           if q != "A_CONFIRMER")

        tk.Label(ligne, text="Recherche", font=theme.PETIT, fg=theme.TEXTE_CLAIR,
                 bg=theme.BLANC).grid(row=0, column=0, sticky="w")
        self.champ_texte = tk.Entry(ligne, width=32, font=theme.NORMAL,
                                    relief="solid", bd=1)
        self.champ_texte.grid(row=1, column=0, padx=(0, 14), ipady=4)
        self.champ_texte.bind("<KeyRelease>", lambda e: self.appliquer_filtres())

        self.choix_domaine = self._liste(ligne, 1, "Domaine", [TOUS_DOMAINES] + domaines, 20)
        self.choix_quartier = self._liste(ligne, 2, "Quartier", [TOUS_QUARTIERS] + quartiers, 20)
        self.choix_tri = self._liste(ligne, 3, "Trier par", list(TRIS), 18)

        BoutonModerne(ligne, texte="Réinitialiser", commande=self.reinitialiser,
                     style="secondaire", icone="↺", fond_parent=theme.BLANC,
                     hauteur=32).grid(row=1, column=4, padx=(6, 0))

    def _liste(self, parent, colonne, titre, valeurs, largeur):
        """Crée une liste déroulante avec son titre ; le changement relance le filtre."""
        tk.Label(parent, text=titre, font=theme.PETIT, fg=theme.TEXTE_CLAIR,
                 bg=theme.BLANC).grid(row=0, column=colonne, sticky="w")
        liste = ttk.Combobox(parent, values=valeurs, state="readonly",
                             width=largeur, font=theme.NORMAL)
        liste.current(0)
        liste.grid(row=1, column=colonne, padx=(0, 14))
        liste.bind("<<ComboboxSelected>>", lambda e: self.appliquer_filtres())
        return liste

    # ---------- ZONE DÉFILANTE DES CARTES ----------
    def _creer_zone_cartes(self):
        cadre = tk.Frame(self, bg=theme.FOND)
        cadre.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.canvas = tk.Canvas(cadre, bg=theme.FOND, highlightthickness=0,
                                yscrollincrement=30)
        barre = ttk.Scrollbar(cadre, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grille = tk.Frame(self.canvas, bg=theme.FOND)
        fenetre = self.canvas.create_window((0, 0), window=self.grille, anchor="nw")
        self.grille.columnconfigure(0, weight=1, uniform="carte")
        self.grille.columnconfigure(1, weight=1, uniform="carte")

        self.grille.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(fenetre, width=e.width))
        self.bind_all("<MouseWheel>", self._molette, add="+")

    def _molette(self, evenement):
        if self.winfo_ismapped():
            self.canvas.yview_scroll(int(-evenement.delta / 120), "units")

    # ---------- FILTRES (pandas) ----------
    def actualiser(self):
        """Appelée par la fenêtre principale à chaque affichage de la page."""
        recherche = self.app.recherche
        if recherche["texte"] or recherche["quartier"]:
            self.champ_texte.delete(0, "end")
            self.champ_texte.insert(0, recherche["texte"])
            self.choix_domaine.set(TOUS_DOMAINES)
            self.choix_quartier.set(recherche["quartier"] or TOUS_QUARTIERS)
            self.app.recherche = {"texte": "", "quartier": ""}
        self.appliquer_filtres()

    def reinitialiser(self):
        self.champ_texte.delete(0, "end")
        self.choix_domaine.current(0)
        self.choix_quartier.current(0)
        self.choix_tri.current(0)
        self.appliquer_filtres()

    def appliquer_filtres(self):
        """Filtre et trie une COPIE du dataset, puis reconstruit les cartes."""
        df = self.app.donnees

        recherche = self.champ_texte.get().strip().lower()
        if recherche:
            masque = pd.Series(False, index=df.index)
            for colonne in COLONNES_RECHERCHE:
                masque |= df[colonne].astype(str).str.lower().str.contains(recherche, regex=False)
            df = df[masque]

        if self.choix_domaine.get() != TOUS_DOMAINES:
            df = df[df["Domaine"] == self.choix_domaine.get()]
        if self.choix_quartier.get() != TOUS_QUARTIERS:
            df = df[df["Quartier"] == self.choix_quartier.get()]

        colonnes_tri, ordre = TRIS[self.choix_tri.get()]
        df = df.sort_values(by=colonnes_tri, ascending=ordre)

        self.compteur.config(
            text=f"{len(df)} entreprises affichées sur {len(self.app.donnees)}")
        self._remplir_cartes(df)

    # ---------- CONSTRUCTION DES CARTES ----------
    def _remplir_cartes(self, df):
        for enfant in self.grille.winfo_children():
            enfant.destroy()

        if df.empty:
            tk.Label(self.grille, text="Aucune entreprise ne correspond à ta recherche.",
                     font=theme.NORMAL, fg=theme.TEXTE_CLAIR, bg=theme.FOND).grid(
                row=0, column=0, columnspan=NB_COLONNES, pady=40)
            return

        for rang, (indice, ligne) in enumerate(df.iterrows()):
            self._creer_carte(ligne, rang // NB_COLONNES, rang % NB_COLONNES)

    def _creer_carte(self, ligne, rangee, colonne):
        carte = tk.Frame(self.grille, bg=theme.BLANC,
                         highlightbackground=theme.BORDURE, highlightthickness=1)
        carte.grid(row=rangee, column=colonne, sticky="nsew", padx=10, pady=10)

        contenu = tk.Frame(carte, bg=theme.BLANC)
        contenu.pack(fill="both", expand=True, padx=22, pady=20)

        # --- Nom de l'entreprise, bien détaché du reste ---
        tk.Label(contenu, text=texte(ligne["Nom_Entreprise"]), font=(theme.POLICE, 14, "bold"),
                 fg=theme.MARINE, bg=theme.BLANC, anchor="w", justify="left",
                 wraplength=340).pack(anchor="w", pady=(0, 10))

        # --- Badges domaine / quartier ---
        badges = tk.Frame(contenu, bg=theme.BLANC)
        badges.pack(anchor="w", pady=(0, 14))
        self._badge(badges, texte(ligne["Domaine"]), theme.BLEU, theme.BLEU_CLAIR)
        self._badge(badges, texte_quartier(ligne["Quartier"]), theme.ORANGE, theme.ORANGE_PASTEL)

        # --- Adresse et téléphone, groupés avec une icône ---
        infos = tk.Frame(contenu, bg=theme.BLANC)
        infos.pack(anchor="w", fill="x", pady=(0, 16))
        self._ligne_info(infos, "📍", texte(ligne["Adresse"]))
        self._ligne_info(infos, "📞", texte(ligne["Telephone"]))

        # --- Séparateur discret avant le bas de carte ---
        tk.Frame(contenu, bg=theme.BORDURE, height=1).pack(fill="x", pady=(0, 14))

        # --- Rating à gauche, boutons à droite ---
        bas = tk.Frame(contenu, bg=theme.BLANC)
        bas.pack(fill="x")
        self._bloc_rating(bas, ligne)

        boutons = tk.Frame(bas, bg=theme.BLANC)
        boutons.pack(side="right")
        BoutonModerne(boutons, texte="Voir le site", icone="🔗", style="fantome",
                     commande=lambda l=ligne: self.ouvrir_site(l), fond_parent=theme.BLANC,
                     hauteur=34).pack(side="left", padx=(0, 10))
        BoutonModerne(boutons, texte="Postuler", icone="✓", style="principal",
                     commande=lambda l=ligne: self.postuler(l), fond_parent=theme.BLANC,
                     hauteur=34).pack(side="left")

    def _ligne_info(self, parent, emoji, valeur):
        """Une ligne icône + texte (adresse, téléphone), alignée proprement."""
        ligne = tk.Frame(parent, bg=theme.BLANC)
        ligne.pack(anchor="w", fill="x", pady=2)
        tk.Label(ligne, text=emoji, font=(POLICE_EMOJI, 10), bg=theme.BLANC,
                 width=2).pack(side="left")
        tk.Label(ligne, text=valeur, font=theme.PETIT, fg=theme.TEXTE, bg=theme.BLANC,
                 anchor="w", justify="left", wraplength=300).pack(side="left")

    def _bloc_rating(self, parent, ligne):
        """Étoile + note en évidence, nombre d'avis en gris discret séparé."""
        bloc = tk.Frame(parent, bg=theme.BLANC)
        bloc.pack(side="left")

        rating = f"{float(ligne['Rating']):.1f}" if not pd.isna(ligne["Rating"]) else VIDE
        avis = int(ligne["Nb_Avis"]) if not pd.isna(ligne["Nb_Avis"]) else 0

        ligne_note = tk.Frame(bloc, bg=theme.BLANC)
        ligne_note.pack(anchor="w")
        tk.Label(ligne_note, text="★", font=(POLICE_EMOJI, 13), fg="#F5A623",
                 bg=theme.BLANC).pack(side="left")
        tk.Label(ligne_note, text=rating, font=(theme.POLICE, 13, "bold"),
                 fg=theme.MARINE, bg=theme.BLANC).pack(side="left", padx=(3, 0))

        tk.Label(bloc, text=f"{avis} avis", font=(theme.POLICE, 9),
                 fg=theme.TEXTE_CLAIR, bg=theme.BLANC).pack(anchor="w")

    def _badge(self, parent, texte_badge, couleur_texte, couleur_fond):
        """Petite étiquette colorée (domaine, quartier)."""
        tk.Label(parent, text=texte_badge, font=(theme.POLICE, 9, "bold"),
                 fg=couleur_texte, bg=couleur_fond, padx=11, pady=4).pack(side="left", padx=(0, 8))

    # ---------- ACTIONS ----------
    def ouvrir_site(self, ligne):
        site = str(ligne["Site_Web"])
        if site.startswith("http"):
            webbrowser.open(site)
        else:
            messagebox.showinfo("AJI TSTAJI", "Cette entreprise n'a pas de site web renseigné.")

    def postuler(self, ligne):
     """Mémorise l'entreprise choisie et ouvre la page Candidature."""
     self.app.entreprise_choisie = ligne.to_dict()
     self.app.afficher_page("Candidature")