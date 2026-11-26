from mcp.server.fastmcp import FastMCP

from complia.agents.graph import build_graph
from complia.rag.answer import answer_question, format_context
from complia.rag.retriever import multilingual_search

mcp = FastMCP("complia")
graph = build_graph()


@mcp.tool()
def rechercher_textes(requete: str, k: int = 4) -> str:
    """Cherche des extraits dans l'AI Act, le RGPD et les guides CNIL.
    Renvoie les extraits numérotés avec leur source."""
    _, docs = multilingual_search(requete, k=k)
    return format_context(docs)


@mcp.tool()
def poser_question(question: str) -> str:
    """Répond en français à une question sur l'AI Act ou le RGPD, avec citations [n]."""
    reponse, _ = answer_question(question)
    return reponse


@mcp.tool()
def analyser_systeme(description: str) -> str:
    """Évalue la conformité d'un système d'IA décrit par l'utilisateur :
    niveau de risque AI Act, données personnelles, obligations AI Act et RGPD."""
    res = graph.invoke({"question": description})
    entete = (
        f"Niveau de risque : {res.get('categorie_risque', 'non déterminé')}\n"
        f"Données personnelles : {'oui' if res.get('donnees_perso') else 'non'}\n\n"
    )
    return entete + res["reponse"]


if __name__ == "__main__":
    mcp.run()