import os

import gradio as gr

from complia.agents.graph import build_graph
from complia.rag.answer import answer_question

graph = build_graph()

NOMS_ETAPES = {
    "aiguilleur": "Aiguilleur : type de demande identifié",
    "reponse_simple": "Réponse directe à partir des textes",
    "classifieur": "Classifieur : niveau de risque déterminé",
    "chercheur": "Chercheur : extraits trouvés dans les textes",
    "analyste": "Analyste : rapport rédigé",
    "verificateur": "Vérificateur : citations contrôlées",
}


def formater_sources(docs) -> str:
    if not docs:
        return ""
    lignes = []
    for i, d in enumerate(docs, start=1):
        fichier = os.path.basename(d.metadata.get("source", "source inconnue"))
        page = d.metadata.get("page")
        ref = f"{fichier}, p. {page + 1}" if isinstance(page, int) else fichier
        extrait = d.page_content[:300].replace("\n", " ")
        lignes.append(f"**[{i}]** {ref}\n> {extrait}…")
    return "\n\n".join(lignes)


def analyser(description: str):
    if not description.strip():
        yield "Décris d'abord ton système d'IA.", "", ""
        return

    etapes, resultat = [], {}
    for etape in graph.stream({"question": description}):
        for agent, maj in etape.items():
            resultat.update(maj)
            texte = NOMS_ETAPES.get(agent, agent)
            if agent == "classifieur":
                perso = "oui" if maj["donnees_perso"] else "non"
                texte += f" → **{maj['categorie_risque']}**, données personnelles : {perso}"
            if agent == "verificateur":
                texte += f" → {maj['verdict']}"
            etapes.append(f"✅ {texte}")
            yield "\n\n".join(etapes), "", ""

    yield "\n\n".join(etapes), resultat.get("reponse", ""), formater_sources(resultat.get("documents"))


def questionner(question: str):
    if not question.strip():
        return "Pose d'abord une question.", ""
    reponse, docs = answer_question(question)
    return reponse, formater_sources(docs)


with gr.Blocks(title="ComplIA") as demo:
    gr.Markdown(
        "# ComplIA — Copilote de conformité AI Act & RGPD\n"
        "Analyse fondée sur l'AI Act, le RGPD et des guides de la CNIL, avec citations. "
        "*Outil d'aide, pas un avis juridique.*"
    )

    with gr.Tab("Analyser un système d'IA"):
        entree = gr.Textbox(label="Décris ton système d'IA", lines=4)
        bouton = gr.Button("Analyser", variant="primary")
        gr.Examples(
            [
                "Un logiciel qui trie automatiquement les CV des candidats pour une entreprise de recrutement.",
                "Un chatbot qui répond aux questions des clients d'un site e-commerce.",
                "Un système municipal qui note les habitants selon leur comportement social.",
                "Un filtre anti-spam pour une messagerie d'entreprise.",
            ],
            inputs=entree,
        )
        etapes = gr.Markdown()
        rapport = gr.Markdown()
        with gr.Accordion("Sources citées", open=False):
            sources = gr.Markdown()
        bouton.click(analyser, inputs=entree, outputs=[etapes, rapport, sources])

    with gr.Tab("Poser une question"):
        question = gr.Textbox(label="Ta question", lines=2)
        bouton_q = gr.Button("Demander", variant="primary")
        gr.Examples(
            [
                "Que dit l'article 5 de l'AI Act ?",
                "Quand faut-il faire une analyse d'impact (AIPD) ?",
                "Quelles obligations de transparence pour un chatbot ?",
            ],
            inputs=question,
        )
        reponse_q = gr.Markdown()
        with gr.Accordion("Sources citées", open=False):
            sources_q = gr.Markdown()
        bouton_q.click(questionner, inputs=question, outputs=[reponse_q, sources_q])


if __name__ == "__main__":
    demo.launch()