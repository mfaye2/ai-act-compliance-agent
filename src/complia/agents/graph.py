from langgraph.graph import END, START, StateGraph

from complia.agents.nodes import (aiguilleur, analyste, chercheur, classifieur,
                                  reponse_simple, verificateur)
from complia.agents.state import ComplianceState

MAX_TENTATIVES = 2  # 1 rapport + 1 seule reprise


def apres_aiguilleur(state: ComplianceState) -> str:
    return "reponse_simple" if state["type_demande"] == "question" else "classifieur"


def apres_verificateur(state: ComplianceState) -> str:
    if state["verdict"] == "a_refaire" and state["tentatives"] < MAX_TENTATIVES:
        return "chercheur"
    return END


def build_graph():
    g = StateGraph(ComplianceState)

    g.add_node("aiguilleur", aiguilleur)
    g.add_node("reponse_simple", reponse_simple)
    g.add_node("classifieur", classifieur)
    g.add_node("chercheur", chercheur)
    g.add_node("analyste", analyste)
    g.add_node("verificateur", verificateur)

    g.add_edge(START, "aiguilleur")
    g.add_conditional_edges("aiguilleur", apres_aiguilleur, ["reponse_simple", "classifieur"])
    g.add_edge("reponse_simple", END)
    g.add_edge("classifieur", "chercheur")
    g.add_edge("chercheur", "analyste")
    g.add_edge("analyste", "verificateur")
    g.add_conditional_edges("verificateur", apres_verificateur, ["chercheur", END])

    return g.compile()