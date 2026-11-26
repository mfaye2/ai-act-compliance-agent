from typing import TypedDict, Literal
from langchain_core.documents import Document


class ComplianceState(TypedDict, total=False):
    question: str                                  # ce que l'utilisateur a écrit
    type_demande: Literal["question", "analyse"]   # décidé par l'aiguilleur
    categorie_risque: str                          # "interdit", "haut risque", "risque limité", "minimal"
    donnees_perso: bool                            # le système traite-t-il des données personnelles ?
    justification: str                             # pourquoi le classifieur a choisi ce niveau de risque
    documents: list[Document]                      # extraits AI Act / RGPD / CNIL retrouvés
    reponse: str                                   # brouillon, puis réponse finale
    verdict: Literal["ok", "a_refaire"]            # décision du vérificateur
    tentatives: int                                # évite une boucle infinie