from typing import Literal

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from complia.agents.state import ComplianceState
from complia.rag.answer import answer_question, format_context
from complia.rag.reranker import rerank
from complia.rag.retriever import multilingual_search

llm = ChatOpenAI(model="gpt-5-mini")


# ---------- 1. Aiguilleur ----------
class Aiguillage(BaseModel):
    type_demande: Literal["question", "analyse"] = Field(
        description="'question' = question générale sur les textes ; "
        "'analyse' = l'utilisateur décrit un système d'IA à évaluer"
    )


def aiguilleur(state: ComplianceState) -> dict:
    res = llm.with_structured_output(Aiguillage).invoke(
        f"Classe cette demande :\n{state['question']}"
    )
    return {"type_demande": res.type_demande, "tentatives": 0}


# ---------- Raccourci : simple question -> ton RAG actuel ----------
def reponse_simple(state: ComplianceState) -> dict:
    reponse, docs = answer_question(state["question"])
    return {"reponse": reponse, "documents": docs}


# ---------- 2. Classifieur ----------
class Classification(BaseModel):
    categorie_risque: Literal["interdit", "haut risque", "risque limité", "minimal"]
    donnees_perso: bool = Field(description="Le système traite-t-il des données personnelles ?")
    justification: str = Field(description="2-3 phrases, en français")


def classifieur(state: ComplianceState) -> dict:
    res = llm.with_structured_output(Classification).invoke(
        "Tu es expert de l'AI Act européen. Classe ce système d'IA selon les 4 niveaux "
        "de risque de l'AI Act (pratiques interdites art. 5, haut risque art. 6 et annexe III, "
        "risque limité art. 50, minimal) et indique s'il traite des données personnelles.\n\n"
        f"Système : {state['question']}"
    )
    return res.model_dump()


# ---------- 3. Chercheur ----------
def chercheur(state: ComplianceState) -> dict:
    requetes = [
        state["question"],
        f"obligations des systèmes d'IA {state['categorie_risque']} AI Act",
    ]
    if state.get("donnees_perso"):
        requetes.append("RGPD base légale analyse d'impact AIPD droits des personnes")

    k = 6 if state.get("verdict") == "a_refaire" else 4  # 2e passage : on cherche plus large
    docs = []
    for r in requetes:
        _, trouves = multilingual_search(r, k=k)
        docs.extend(trouves)

    uniques = list({d.page_content: d for d in docs}.values())  # enlève les doublons
    return {"documents": rerank(state["question"], uniques, top_n=8)}


# ---------- 4. Analyste ----------
def analyste(state: ComplianceState) -> dict:
    contexte = format_context(state["documents"])
    prompt = f"""Tu es consultant en conformité AI Act et RGPD.

Système décrit : {state['question']}
Niveau de risque proposé : {state['categorie_risque']} ({state['justification']})
Données personnelles : {"oui" if state.get("donnees_perso") else "non"}

Extraits numérotés des textes officiels :
{contexte}

Rédige en français un rapport avec 4 parties :
1. Niveau de risque AI Act et pourquoi
2. Obligations AI Act applicables
3. Obligations RGPD (seulement si données personnelles)
4. Prochaines étapes concrètes

Règles : chaque affirmation se termine par sa source [n].
N'utilise QUE les extraits fournis. Si une information manque, dis-le."""
    return {"reponse": llm.invoke(prompt).content}


# ---------- 5. Vérificateur ----------
class Verification(BaseModel):
    verdict: Literal["ok", "a_refaire"]
    probleme: str = Field(description="Ce qui ne va pas, ou 'rien'")


def verificateur(state: ComplianceState) -> dict:
    res = llm.with_structured_output(Verification).invoke(
        "Vérifie ce rapport de conformité. Réponds 'a_refaire' si une affirmation "
        "importante n'a pas de citation [n], ou si une citation ne correspond pas "
        "à l'extrait cité. Sinon 'ok'.\n\n"
        f"Extraits :\n{format_context(state['documents'])}\n\nRapport :\n{state['reponse']}"
    )
    return {"verdict": res.verdict, "tentatives": state.get("tentatives", 0) + 1}