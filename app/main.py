"""
main.py
Fenêtre principale de l'application AJI TSTAJI : page de connexion, barre de
navigation et changement de page.

Lancement (depuis la racine du projet) :
    python app/main.py
"""

import sys
import tkinter as tk
from pathlib import Path
import customtkinter as ctk
RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from app.chatbot_page import ChatbotPage, creer_icone_robot
from app import theme
from app.pages.page_vide import PageVide
from app.pages.connexion import Connexion
from app.pages.accueil import Accueil
from app.pages.entreprises import Entreprises
from app.pages.opportunites import Opportunites
from app.pages.mon_profil import MonProfil
from app.pages.candidature import Candidature
from app.pages.mes_candidatures import MesCandidatures
from app.pages.analyse import Analyse
from src.utils.charger_donnees import charger_entreprises

from src.utils.authentification import obtenir_informations
from src.database.base_donnees import (
    initialiser_base,
    obtenir_profil_utilisateur,
    enregistrer_profil_utilisateur,
)


PAGES_MENU = [
    "Accueil",
    "Entreprises",
    "Opportunités",
    "Mes candidatures",
    "Analyse",
    "Candidature",
]
PAGE_PROFIL = "Mon profil"

PAGES_REELLES = {
    "Accueil": Accueil,
    "Entreprises": Entreprises,
    "Opportunités": Opportunites,
    "Mon profil": MonProfil,
    "Candidature": Candidature,
    "Mes candidatures": MesCandidatures,
    "Analyse": Analyse,
}


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AJI TSTAJI")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        try:
            self.state("zoomed")
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)   # Linux
            except tk.TclError:
                pass
        theme.appliquer_style(self)

        self.donnees = charger_entreprises()
        self.recherche = {"texte": "", "quartier": ""}
        self.entreprise_choisie = None

        # utilisateur connecté (disponible pour toutes les pages via app.utilisateur)
        self.utilisateur = None          # e-mail
        self.nom_utilisateur = ""

        self.pages = {}
        self.liens = {}
        self.traits = {}
        self.page_active = None
        self.page_precedente = "Accueil"
        self.bouton_ia = None
        self.image_robot = None
        self.panneau_chatbot = None      # chatbot en demi-page (à droite)
        self._widgets_session = []       # barre + zone des pages (détruits à la déconnexion)

        self._afficher_connexion()

    # ------------------------------------------------------------ connexion
    def _afficher_connexion(self):
        self.connexion = Connexion(self, self, on_succes=self._apres_connexion)
        self.connexion.pack(fill="both", expand=True)

    def _apres_connexion(self, email, nom):
        self.utilisateur = email.strip().lower()
        self.nom_utilisateur = nom

        # Préparer la base sans supprimer les données existantes
        initialiser_base()

        # Importer les informations du compte si le profil n'existe pas
        profil = obtenir_profil_utilisateur(self.utilisateur)

        if not profil:
            informations = obtenir_informations(self.utilisateur)

            donnees_profil = {
                "nom": nom,
                "telephone": informations.get("telephone", ""),
                "ville": informations.get("ville", "Marrakech"),
                "etablissement": informations.get("etablissement", ""),
                "secteur": informations.get("secteur", ""),
                "diplome": informations.get("diplome", ""),
                "recherche": informations.get("recherche", "Stage"),
            }

            enregistrer_profil_utilisateur(self.utilisateur, donnees_profil)

        try:
            self.connexion.destroy()
            self._creer_barre()
            self._creer_pages()
            self.afficher_page("Accueil")
            self._creer_bouton_ia()
            self.focus_set()

        except Exception:
            import traceback
            from tkinter import messagebox

            erreur = traceback.format_exc()
            print(erreur)
            messagebox.showerror("Erreur AJI TSTAJI", erreur)

    # --------------------------------------------------------- bouton robot IA
    def _creer_bouton_ia(self):
        """Petit bouton robot rond en bas à droite (sans texte)."""
        self.image_robot = ctk.CTkImage(
            creer_icone_robot(120, rayon=0.5), size=(60, 60))
        self.bouton_ia = ctk.CTkButton(
            self,
            text="",
            image=self.image_robot,
            fg_color="transparent",
            hover_color=theme.FOND,
            border_width=0,
            corner_radius=30,
            width=60,
            height=60,
            command=self.ouvrir_chatbot,
        )
        self._mettre_a_jour_bouton_ia()

    def _mettre_a_jour_bouton_ia(self):
        """Le bouton robot est visible, sauf quand le panneau chatbot est ouvert."""
        if self.bouton_ia is None:
            return
        if self.panneau_chatbot is not None and self.panneau_chatbot.winfo_ismapped():
            self.bouton_ia.place_forget()
        else:
            self.bouton_ia.place(relx=0.98, rely=0.96, anchor="se")
            self.bouton_ia.lift()

    def ouvrir_chatbot(self):
        """Ouvre le chatbot en demi-page à droite, par-dessus la page en cours."""
        if self.utilisateur is None or self.panneau_chatbot is None:
            return
        self.panneau_chatbot.place(relx=0.5, rely=0.1, relwidth=0.5, relheight=0.88)
        self.panneau_chatbot.lift()
        self._mettre_a_jour_bouton_ia()

    def fermer_chatbot(self):
        if self.panneau_chatbot is not None:
            self.panneau_chatbot.place_forget()
        self._mettre_a_jour_bouton_ia()

    def basculer_chatbot(self):
        if self.panneau_chatbot is not None and self.panneau_chatbot.winfo_ismapped():
            self.fermer_chatbot()
        else:
            self.ouvrir_chatbot()

    # ancien nom conservé pour ne rien casser si une autre page l'utilise
    _basculer_chatbot = ouvrir_chatbot

    def deconnecter(self):
        """Ferme la session et revient à la connexion."""
        for widget in self._widgets_session:
            widget.destroy()

        if self.bouton_ia is not None:
            self.bouton_ia.destroy()
            self.bouton_ia = None

        if self.panneau_chatbot is not None:
            self.panneau_chatbot.destroy()
            self.panneau_chatbot = None

        self._widgets_session = []
        self.pages, self.liens, self.traits = {}, {}, {}
        self.page_active = None
        self.page_precedente = "Accueil"
        self.utilisateur = None
        self.nom_utilisateur = ""
        self.recherche = {"texte": "", "quartier": ""}
        self.entreprise_choisie = None
        self._afficher_connexion()

    # -------------------------------------------------------------- barre
    def _creer_barre(self):
        barre = tk.Frame(self, bg=theme.BLANC, height=70)
        barre.pack(fill="x")
        barre.pack_propagate(False)
        separateur = tk.Frame(self, bg=theme.BORDURE, height=1)
        separateur.pack(fill="x")
        self._widgets_session += [barre, separateur]

        logo = tk.Frame(barre, bg=theme.BLANC, cursor="hand2")
        logo.pack(side="left", padx=(40, 30))
        police_logo = (theme.POLICE, 20, "bold")
        for texte_partie, couleur in (("AJI ", theme.MARINE), ("TSTAJI", theme.BLEU)):
            etiquette = tk.Label(logo, text=texte_partie, font=police_logo, fg=couleur,
                                 bg=theme.BLANC)
            etiquette.pack(side="left")
            etiquette.bind("<Button-1>", lambda e: self.afficher_page("Accueil"))

        # lien « Déconnexion » tout à droite
        deconnexion = tk.Label(barre, text="Déconnexion", font=theme.NORMAL,
                               fg=theme.TEXTE, bg=theme.BLANC, cursor="hand2")
        deconnexion.pack(side="right", padx=(10, 40))
        deconnexion.bind("<Button-1>", lambda e: self.deconnecter())
        deconnexion.bind("<Enter>", lambda e: deconnexion.config(fg=theme.BLEU))
        deconnexion.bind("<Leave>", lambda e: deconnexion.config(fg=theme.TEXTE))

        self._creer_lien(barre, PAGE_PROFIL, "right", marge=(10, 10))

        for nom in PAGES_MENU:
            self._creer_lien(barre, nom, "left", marge=(12, 12))

    def _creer_lien(self, parent, nom, cote, marge):
        cellule = tk.Frame(parent, bg=theme.BLANC)
        cellule.pack(side=cote, fill="y", padx=marge)

        trait = tk.Frame(cellule, bg=theme.BLANC, height=3)
        trait.pack(side="bottom", fill="x")

        lien = tk.Label(cellule, text=nom, font=theme.NORMAL, fg=theme.TEXTE,
                        bg=theme.BLANC, cursor="hand2")
        lien.pack(expand=True)

        lien.bind("<Button-1>", lambda e: self.afficher_page(nom))
        lien.bind("<Enter>", lambda e: self._survol(nom, True))
        lien.bind("<Leave>", lambda e: self._survol(nom, False))

        self.liens[nom] = lien
        self.traits[nom] = trait

    def _survol(self, nom, entre):
        if nom != self.page_active:
            self.liens[nom].config(fg=theme.BLEU if entre else theme.TEXTE)

    # -------------------------------------------------------------- pages
    def _creer_pages(self):
        self.zone_pages = tk.Frame(self, bg=theme.FOND)
        self.zone_pages.pack(fill="both", expand=True)
        self._widgets_session.append(self.zone_pages)
        for nom in PAGES_MENU + [PAGE_PROFIL]:
            if nom in PAGES_REELLES:
                self.pages[nom] = PAGES_REELLES[nom](self.zone_pages, self)
            else:
                self.pages[nom] = PageVide(self.zone_pages, self, nom)

        # chatbot : panneau créé une fois, affiché en demi-page avec place()
        self.panneau_chatbot = ChatbotPage(self, app=self, fermer=self.fermer_chatbot)

    def afficher_page(self, nom):
        self.page_active = nom
        self.page_precedente = nom
        for page in self.pages.values():
            page.pack_forget()
        self.pages[nom].pack(fill="both", expand=True)

        if hasattr(self.pages[nom], "actualiser"):
            self.pages[nom].actualiser()

        for n in self.liens:
            actif = (n == nom)
            self.liens[n].config(fg=theme.BLEU if actif else theme.TEXTE)
            self.traits[n].config(bg=theme.BLEU if actif else theme.BLANC)

        # garder le chatbot et le bouton robot au-dessus de la nouvelle page
        if self.panneau_chatbot is not None and self.panneau_chatbot.winfo_ismapped():
            self.panneau_chatbot.lift()
        self._mettre_a_jour_bouton_ia()


if __name__ == "__main__":
    app = Application()
    app.mainloop()