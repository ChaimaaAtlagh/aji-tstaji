"""Classification des entreprises par domaine/sous-domaine et détection du quartier."""

DOMAINES = {
    "Développement": {
        "Web": ["site web", "développement web", "agence web", "web design", "création site"],
        "Web & mobile": ["application mobile", "app mobile", "développement mobile"],
        "Logiciels sur mesure": ["logiciel sur mesure", "software", "développement logiciel", "erp"],
    },
    "Services IT": {
        "Conseil & support IT": ["conseil it", "support informatique", "maintenance informatique", "infogérance"],
    },
    "IA": {
        "IA & automatisation": ["intelligence artificielle", "machine learning", "ia ", "automatisation"],
    },
    "Cybersécurité": {
        "Cybersécurité": ["cybersécurité", "sécurité informatique", "pentest"],
    },
    "Réseaux": {
        "Réseaux & infrastructure": ["réseau", "infrastructure informatique", "câblage"],
    },
    "Cloud": {
        "Hébergement & cloud": ["hébergement", "cloud", "serveur"],
    },
}

QUARTIERS_CONNUS = [
    "Guéliz", "Sidi Ghanem", "Al Massar", "Mabrouka", "Ménara",
    "M'hamid", "Massira", "Semlalia", "Daoudiate", "Hivernage",
    "Medina", "Targa", "Route de Safi", "Route de Casablanca",
]


def classifier_domaine(texte: str) -> tuple[str, str]:
    """Retourne (Domaine, Sous_Domaine) en cherchant des mots-clés dans le texte (nom + type Google)."""
    texte_lower = texte.lower()
    for domaine, sous_domaines in DOMAINES.items():
        for sous_domaine, mots_cles in sous_domaines.items():
            if any(mot in texte_lower for mot in mots_cles):
                return domaine, sous_domaine
    return "Développement", "Web"  # valeur par défaut, comme dans ton dataset actuel


def detecter_quartier(adresse: str) -> tuple[str, str]:
    """Retourne (Quartier, Fiabilite_Quartier)."""
    for quartier in QUARTIERS_CONNUS:
        if quartier.lower() in adresse.lower():
            return quartier, "Explicite"
    return "A_CONFIRMER", "A_CONFIRMER"
MOTS_CLES_IT_GENERIQUES = [
    "informatique", "digital", "numérique", "technologie", "logiciel",
    "site web", "application", "développement", "it ", " it", "tech",
    "cloud", "réseau", "cybersécurité", "intelligence artificielle",
    "data", "système d'information", "web", "mobile",
]


def est_pertinent_it(texte: str) -> bool:
    """Vérifie si le nom/type de l'entreprise correspond bien au domaine IT."""
    texte_lower = texte.lower()
    return any(mot in texte_lower for mot in MOTS_CLES_IT_GENERIQUES)