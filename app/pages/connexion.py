"""
connexion.py
Page d'authentification AJI TSTAJI (connexion + création de compte).
Design : panneau gauche illustré avec photo circulaire de Marrakech,
panneau droit pour la connexion ou l'inscription.
"""

import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from app import theme
from src.utils.authentification import inscrire, verifier
from src.database.base_donnees import (
    initialiser_base,
    obtenir_profil_utilisateur,
    enregistrer_profil_utilisateur,
) 

try:
    from PIL import Image, ImageDraw, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False


# ------------------------------------------------------------ Chemins
RACINE = Path(__file__).resolve().parents[1]
IMAGE_MARRAKECH = RACINE / "assets" / "koutoubia.png"
LOGO = RACINE / "assets" / "logo.png"

EMAIL_RE = re.compile(r"^[\w.+\-]+@[\w\-]+(\.[\w\-]+)+$")
ROUGE_ERREUR = "#DC2626"
GRIS_TEXTE = "#64748B"
BLEU_CLAIR = "#EAF5FF"
BLEU_PALE = "#D7EBFF"
BLEU = "#1769E8"
BLEU_FONCE = "#123D73"
BLANC = "#FFFFFF"


# ------------------------------------------------------ Visuel Marrakech
def _recadrer(img, largeur, hauteur):
    """Recadre une image pour remplir une zone sans l'étirer."""
    echelle = max(largeur / img.width, hauteur / img.height)
    taille = (max(1, int(img.width * echelle)),
              max(1, int(img.height * echelle)))
    img = img.resize(taille, Image.Resampling.LANCZOS)
    gauche = (img.width - largeur) // 2
    haut = (img.height - hauteur) // 2
    return img.crop((gauche, haut, gauche + largeur, haut + hauteur))



def construire_visuel(largeur, hauteur):
    """Panneau gauche moderne avec bord courbe et photo circulaire."""
    from PIL import ImageFont, ImageDraw, Image

    largeur = max(largeur, 300)
    hauteur = max(hauteur, 400)

    image = Image.new("RGB", (largeur, hauteur), "#F5FAFF")
    dessin = ImageDraw.Draw(image)

    # Fond bleu clair avec une grande courbe sur le côté droit
    dessin.rectangle(
        (0, 0, int(largeur * 0.65), hauteur),
        fill="#EAF5FF"
    )
    dessin.ellipse(
        (int(largeur * 0.12), -int(hauteur * 0.28),
         int(largeur * 1.04), int(hauteur * 1.10)),
        fill="#C7E3FF"
    )
    dessin.ellipse(
        (int(largeur * 0.07), -int(hauteur * 0.28),
         int(largeur * 0.97), int(hauteur * 1.06)),
        fill="#EFF7FF"
    )

    # Vague douce en bas
    dessin.ellipse(
        (-int(largeur * 0.35), int(hauteur * 0.78),
         int(largeur * 0.95), int(hauteur * 1.50)),
        fill="#D8EBFF"
    )
    dessin.ellipse(
        (-int(largeur * 0.38), int(hauteur * 0.76),
         int(largeur * 0.88), int(hauteur * 1.43)),
        fill="#F2F8FF"
    )

    # Polices
    try:
        police_grande = ImageFont.truetype(
            "arial.ttf", max(24, int(largeur * 0.064))
        )
        police_moyenne = ImageFont.truetype(
            "arial.ttf", max(12, int(largeur * 0.026))
        )
        police_petite = ImageFont.truetype(
            "arial.ttf", max(11, int(largeur * 0.022))
        )
    except OSError:
        police_grande = ImageFont.load_default()
        police_moyenne = ImageFont.load_default()
        police_petite = ImageFont.load_default()

    marge = int(largeur * 0.07)
    haut_logo = int(hauteur * 0.07)

    # Logo
    logo_img = None
    if LOGO.exists():
        try:
            logo_img = Image.open(LOGO).convert("RGBA")
            logo_img.thumbnail(
                (int(largeur * 0.20), int(hauteur * 0.17)),
                Image.Resampling.LANCZOS
            )
        except Exception:
            logo_img = None

    if logo_img:
        image.paste(logo_img, (marge, haut_logo), logo_img)
        texte_x = marge + logo_img.width + int(largeur * 0.025)
        dessin.line(
            (texte_x - 8, haut_logo + 3,
             texte_x - 8, haut_logo + logo_img.height - 3),
            fill="#1769E8", width=2
        )
    else:
        texte_x = marge
        tour_x = marge + 24
        dessin.rectangle(
            (tour_x - 9, haut_logo + 12,
             tour_x + 9, haut_logo + 76),
            outline="#0877C9", width=3
        )
        dessin.line(
            (tour_x - 5, haut_logo + 12,
             tour_x - 5, haut_logo + 2),
            fill="#0877C9", width=3
        )
        dessin.line(
            (tour_x + 5, haut_logo + 12,
             tour_x + 5, haut_logo + 2),
            fill="#0877C9", width=3
        )
        dessin.arc(
            (marge - 4, haut_logo + 30,
             marge + 42, haut_logo + 78),
            190, 330, fill="#0877C9", width=3
        )
        texte_x = marge + 60

    dessin.text(
        (texte_x, haut_logo + 2),
        "AJI TSTAJI", fill="#123D73", font=police_grande
    )
    dessin.text(
        (texte_x, haut_logo + int(hauteur * 0.095)),
        "Trouvez votre prochaine opportunité",
        fill="#315F98", font=police_moyenne
    )
    dessin.text(
        (texte_x, haut_logo + int(hauteur * 0.135)),
        "professionnelle à Marrakech",
        fill="#315F98", font=police_moyenne
    )

    # Photo circulaire
    diametre = min(int(largeur * 0.80), int(hauteur * 0.50))
    centre_x = int(largeur * 0.46)
    centre_y = int(hauteur * 0.52)
    gauche = centre_x - diametre // 2
    haut = centre_y - diametre // 2

    # Image de la Koutoubia uniquement
    if IMAGE_MARRAKECH.exists():
        try:
            photo = Image.open(IMAGE_MARRAKECH).convert("RGB")
            photo = _recadrer(photo, diametre, diametre)
        except Exception:
            photo = Image.new("RGB", (diametre, diametre), "#D3E8FA")
    else:
        photo = Image.new("RGB", (diametre, diametre), "#D3E8FA")

    masque = Image.new("L", (diametre, diametre), 0)
    ImageDraw.Draw(masque).ellipse(
        (0, 0, diametre - 1, diametre - 1), fill=255
    )
    image.paste(photo, (gauche, haut), masque)

    # Slogan sous la photo
    trait_y = min(hauteur - 75, haut + diametre + int(hauteur * 0.035))
    dessin.rounded_rectangle(
        (centre_x - 22, trait_y,
         centre_x + 22, trait_y + 5),
        radius=3, fill="#0877F9"
    )
    dessin.text(
        (centre_x, trait_y + 17),
        "Trouvez les opportunités",
        fill="#315F98", font=police_petite, anchor="mt"
    )
    dessin.text(
        (centre_x, trait_y + 17 + max(17, int(hauteur * 0.03))),
        "qui correspondent à votre avenir",
        fill="#315F98", font=police_petite, anchor="mt"
    )

    return image


# -------------------------------------------------------------- Connexion
class Connexion(tk.Frame):

    def __init__(self, parent, app, on_succes=None):
        super().__init__(parent, bg=BLANC)
        self.app = app
        self.on_succes = on_succes
        self.mode = "connexion"
        self._photo = None
        self._tache = None
        self._last_size = (0, 0)
        self._inscription_conteneur = None
        self._show_password = False

        self.canvas = tk.Canvas(
            self, bg=BLEU_CLAIR, highlightthickness=0, bd=0
        )
        self.canvas.place(relx=0, rely=0, relwidth=0.53, relheight=1)
        self.canvas.bind("<Configure>", self._planifier_dessin)

        self.droite = tk.Frame(self, bg=BLANC)
        self.droite.place(relx=0.53, rely=0, relwidth=0.47, relheight=1)
        self.zone_formulaire = tk.Frame(self.droite, bg=BLANC)
        self.zone_formulaire.place(
            relx=0.5, rely=0.5, anchor="center",
            relwidth=0.82
        )

        tk.Label(
            self.droite, text="© AJI TSTAJI",
            font=(theme.POLICE, 9), fg=GRIS_TEXTE, bg=BLANC
        ).place(relx=0.5, rely=1.0, anchor="s", y=-12)

        self._afficher_connexion()

    # ------------------------------------------------------ Panneau gauche
    def _planifier_dessin(self, event):
        taille = (event.width, event.height)
        if taille == self._last_size:
            return
        self._last_size = taille
        if self._tache:
            try:
                self.after_cancel(self._tache)
            except tk.TclError:
                pass
        self._tache = self.after(
            70, lambda w=event.width, h=event.height: self._dessiner(w, h)
        )

    def _dessiner(self, largeur, hauteur):
        self._tache = None
        if largeur < 100 or hauteur < 150:
            return
        self.canvas.delete("all")
        if PIL_OK:
            try:
                visuel = construire_visuel(largeur, hauteur)
                self._photo = ImageTk.PhotoImage(visuel)
                self.canvas.create_image(0, 0, image=self._photo, anchor="nw")
                return
            except Exception:
                pass
        self.canvas.create_rectangle(
            0, 0, largeur, hauteur, fill=BLEU_CLAIR, outline=""
        )
        self.canvas.create_text(
            largeur // 2, hauteur // 3, text="AJI TSTAJI",
            fill=BLEU_FONCE, font=(theme.POLICE, 28, "bold")
        )
        self.canvas.create_text(
            largeur // 2, hauteur // 3 + 45,
            text="Trouvez votre prochaine opportunité\nprofessionnelle à Marrakech",
            fill="#315F98", font=(theme.POLICE, 12), justify="center"
        )

    # ------------------------------------------------------ Helpers formulaire
    def _vider(self):
        for widget in self.zone_formulaire.winfo_children():
            widget.destroy()
        if self._inscription_conteneur is not None:
            try:
                self._inscription_conteneur.destroy()
            except tk.TclError:
                pass
            self._inscription_conteneur = None

    def _titre(self, titre, sous_titre):
        tk.Label(
            self.zone_formulaire, text=titre,
            font=(theme.POLICE, 25, "bold"),
            fg=BLEU_FONCE, bg=BLANC
        ).pack(anchor="w", pady=(0, 5))
        tk.Label(
            self.zone_formulaire, text=sous_titre,
            font=(theme.POLICE, 10),
            fg=GRIS_TEXTE, bg=BLANC
        ).pack(anchor="w", pady=(0, 23))

    def _champ(self, parent, label, password=False, largeur=420):
        cadre = tk.Frame(parent, bg=BLANC)
        cadre.pack(fill="x", pady=8)

        tk.Label(
            cadre, text=label,
            font=(theme.POLICE, 10, "bold"),
            fg=BLEU_FONCE, bg=BLANC
        ).pack(anchor="w", pady=(0, 7))

        variable = tk.StringVar()
        enveloppe = tk.Frame(
            cadre, bg=BLANC, highlightthickness=1,
            highlightbackground="#C6D5EA", highlightcolor=BLEU
        )
        enveloppe.pack(fill="x")

        entree = tk.Entry(
            enveloppe, textvariable=variable,
            font=(theme.POLICE, 11), bg=BLANC, fg="#1F2937",
            relief="flat", bd=0, insertbackground=BLEU,
            show="*" if password else ""
        )
        entree.pack(side="left", fill="x", expand=True, ipady=10, padx=(12, 8))

        if password:
            bouton_voir = tk.Label(
                enveloppe, text="Afficher",
                font=(theme.POLICE, 9), fg=BLEU, bg=BLANC,
                cursor="hand2", padx=10
            )
            bouton_voir.pack(side="right")
            bouton_voir.bind(
                "<Button-1>",
                lambda event, e=entree, b=bouton_voir:
                    self._basculer_mot_de_passe(e, b)
            )

        return variable

    def _basculer_mot_de_passe(self, entree, bouton):
        self._show_password = not self._show_password
        entree.config(show="" if self._show_password else "*")
        bouton.config(text="Masquer" if self._show_password else "Afficher")

    def _bouton(self, parent, texte, commande, principal=True):
        couleur = BLEU if principal else BLANC
        texte_couleur = BLANC if principal else BLEU
        cadre = tk.Frame(
            parent, bg=couleur,
            highlightthickness=0 if principal else 1,
            highlightbackground=BLEU
        )
        cadre.pack(fill="x", pady=(12, 4))
        bouton = tk.Label(
            cadre, text=texte, font=(theme.POLICE, 11, "bold"),
            bg=couleur, fg=texte_couleur, cursor="hand2",
            padx=12, pady=12
        )
        bouton.pack(fill="both", expand=True)
        for element in (cadre, bouton):
            element.bind("<Button-1>", lambda event: commande())
            element.bind(
                "<Enter>",
                lambda event, b=bouton, p=principal:
                    b.config(bg="#0F5BD3" if p else "#F1F7FF")
            )
            element.bind(
                "<Leave>",
                lambda event, b=bouton, p=principal:
                    b.config(bg=BLEU if p else BLANC)
            )
        return bouton

    def _zone_erreur(self, parent):
        self.lbl_erreur = tk.Label(
            parent, text="", font=(theme.POLICE, 9),
            fg=ROUGE_ERREUR, bg=BLANC, wraplength=430,
            justify="left", anchor="w"
        )
        self.lbl_erreur.pack(fill="x", pady=(3, 2))

    def _erreur(self, message):
        if hasattr(self, "lbl_erreur"):
            self.lbl_erreur.config(text=message)

    # ------------------------------------------------------ Connexion
    def _afficher_connexion(self):
        self.mode = "connexion"
        self._vider()
        formulaire = self.zone_formulaire
        self._titre(
            "Connexion",
            "Accédez à votre espace personnel"
        )

        self.email_var = self._champ(formulaire, "Adresse e-mail")
        self.mdp_var = self._champ(formulaire, "Mot de passe", password=True)

        tk.Label(
            formulaire, text="Mot de passe oublié ?",
            font=(theme.POLICE, 9), fg=BLEU, bg=BLANC, cursor="hand2"
        ).pack(anchor="e", pady=(2, 6))

        self._zone_erreur(formulaire)
        self._bouton(formulaire, "Se connecter  →", self._valider)

        separateur = tk.Frame(formulaire, bg=BLANC)
        separateur.pack(fill="x", pady=(12, 5))
        tk.Frame(separateur, bg="#D8E1ED", height=1).pack(
            side="left", fill="x", expand=True, pady=8
        )
        tk.Label(
            separateur, text="ou", font=(theme.POLICE, 9),
            fg=GRIS_TEXTE, bg=BLANC, padx=12
        ).pack(side="left")
        tk.Frame(separateur, bg="#D8E1ED", height=1).pack(
            side="left", fill="x", expand=True, pady=8
        )

        self._bouton(
            formulaire, "Créer un compte",
            self._afficher_inscription, principal=False
        )

    # ------------------------------------------------------ Inscription scrollable
    def _creer_formulaire_scrollable(self):
        conteneur = tk.Frame(self.droite, bg=BLANC)
        conteneur.place(
            relx=0.5, rely=0.03, anchor="n",
            relwidth=0.84, relheight=0.90
        )
        canvas = tk.Canvas(
            conteneur, bg=BLANC, highlightthickness=0, bd=0
        )
        scrollbar = ttk.Scrollbar(
            conteneur, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        formulaire = tk.Frame(canvas, bg=BLANC)
        fenetre = canvas.create_window(
            (0, 0), window=formulaire, anchor="nw"
        )

        formulaire.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(fenetre, width=event.width)
        )

        def molette(event):
            canvas.yview_scroll(int(-event.delta / 120), "units")

        canvas.bind("<Enter>", lambda event: canvas.bind_all("<MouseWheel>", molette))
        canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))
        return conteneur, formulaire

    def _afficher_inscription(self):
        self.mode = "inscription"
        self._vider()
        conteneur, formulaire = self._creer_formulaire_scrollable()
        self._inscription_conteneur = conteneur
        self.zone_formulaire.place_forget()

        tk.Label(
            formulaire, text="Créer un compte",
            font=(theme.POLICE, 24, "bold"), fg=BLEU_FONCE, bg=BLANC
        ).pack(anchor="w", pady=(8, 4))
        tk.Label(
            formulaire,
            text="Complétez vos informations pour personnaliser votre espace.",
            font=(theme.POLICE, 10), fg=GRIS_TEXTE, bg=BLANC,
            wraplength=470, justify="left"
        ).pack(anchor="w", pady=(0, 16))

        self.nom_var = self._champ(formulaire, "Nom complet")
        self.email_var = self._champ(formulaire, "Adresse e-mail")
        self.telephone_var = self._champ(formulaire, "Téléphone")
        self.ville_var = self._champ(formulaire, "Ville")
        self.etablissement_var = self._champ(formulaire, "Établissement")
        self.filiere_var = self._champ(formulaire, "Filière / domaine")
        self.diplome_var = self._champ(formulaire, "Diplôme préparé")

        cadre = tk.Frame(formulaire, bg=BLANC)
        cadre.pack(fill="x", pady=8)
        tk.Label(
            cadre, text="Type d'opportunité recherchée",
            font=(theme.POLICE, 10, "bold"), fg=BLEU_FONCE, bg=BLANC
        ).pack(anchor="w", pady=(0, 7))
        self.recherche_var = tk.StringVar(value="Stage")
        ttk.Combobox(
            cadre, textvariable=self.recherche_var,
            values=["Stage", "Stage de fin d'études (PFE)", "Emploi", "Alternance"],
            state="readonly", font=(theme.POLICE, 10)
        ).pack(fill="x", ipady=5)

        self.mdp_var = self._champ(formulaire, "Mot de passe", password=True)
        self.confirm_var = self._champ(
            formulaire, "Confirmer le mot de passe", password=True
        )

        self._zone_erreur(formulaire)
        self._bouton(formulaire, "Créer mon compte", self._valider)
        self._bouton(
            formulaire, "Retour à la connexion",
            self._retour_connexion, principal=False
        )

    def _retour_connexion(self):
        if self._inscription_conteneur is not None:
            self._inscription_conteneur.destroy()
            self._inscription_conteneur = None
        self.zone_formulaire.place(
            relx=0.5, rely=0.5, anchor="center", relwidth=0.82
        )
        self._afficher_connexion()

    # ------------------------------------------------------ Validation
    def _valider(self):
        email = self.email_var.get().strip().lower()
        mdp = self.mdp_var.get()

        if not email or not mdp:
            self._erreur("Veuillez remplir les champs obligatoires.")
            return
        if not EMAIL_RE.match(email):
            self._erreur("Veuillez saisir une adresse e-mail valide.")
            return

        if self.mode == "connexion":
            try:
                ok, message, nom = verifier(email, mdp)
            except Exception as erreur:
                self._erreur(f"Erreur de connexion : {erreur}")
                return

            if not ok:
                self._erreur(message)
                return

            try:
                initialiser_base()
                profil = obtenir_profil_utilisateur(email)
                if not profil:
                    enregistrer_profil_utilisateur(
                        email,
                        {
                            "prenom": nom.strip(),
                            "nom": "",
                            "ville": "Marrakech",
                            "email": email,
                        }
                    )
            except Exception as erreur:
                self._erreur(f"Erreur lors du chargement du profil : {erreur}")
                return

            self._terminer(email, nom)
            return

        nom = self.nom_var.get().strip()
        confirmation = self.confirm_var.get()
        informations = {
            "telephone": self.telephone_var.get().strip(),
            "ville": self.ville_var.get().strip() or "Marrakech",
            "etablissement": self.etablissement_var.get().strip(),
            "secteur": self.filiere_var.get().strip(),
            "diplome": self.diplome_var.get().strip(),
            "recherche": self.recherche_var.get(),
        }

        if not nom:
            self._erreur("Veuillez saisir votre nom complet.")
            return

        champs_obligatoires = {
            "Téléphone": informations["telephone"],
            "Établissement": informations["etablissement"],
            "Filière": informations["secteur"],
            "Diplôme préparé": informations["diplome"],
        }
        for label, valeur in champs_obligatoires.items():
            if not valeur:
                self._erreur(f"Veuillez renseigner : {label}.")
                return

        if len(mdp) < 6:
            self._erreur("Le mot de passe doit contenir au moins 6 caractères.")
            return
        if mdp != confirmation:
            self._erreur("Les mots de passe ne correspondent pas.")
            return

        try:
            ok, message = inscrire(nom, email, mdp, informations)
            if not ok:
                self._erreur(message)
                return

            initialiser_base()
            parties_nom = nom.split(maxsplit=1)
            profil = {
                "prenom": parties_nom[0],
                "nom": parties_nom[1] if len(parties_nom) > 1 else "",
                "email": email,
                "telephone": informations["telephone"],
                "ville": informations["ville"],
                "etablissement": informations["etablissement"],
                "secteur": informations["secteur"],
                "diplome": informations["diplome"],
                "recherche": informations["recherche"],
            }
            enregistrer_profil_utilisateur(email, profil)
        except Exception as erreur:
            self._erreur(f"Erreur lors de la création du compte : {erreur}")
            return

        self._terminer(email, nom)

    def _terminer(self, email, nom):
        """Appelée après une connexion ou une inscription réussie."""
        if self.on_succes:
            self.on_succes(email, nom)
        else:
            messagebox.showinfo("Connexion réussie", f"Bonjour {nom} !")
