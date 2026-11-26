import sys

from complia.agents.graph import build_graph

question = " ".join(sys.argv[1:]) or (
    "Nous développons un logiciel qui trie automatiquement les CV "
    "des candidats pour une entreprise de recrutement."
)

graph = build_graph()
resultat = {}
for etape in graph.stream({"question": question}):
    for agent, maj in etape.items():
        infos = {k: v for k, v in maj.items() if k not in ("documents", "reponse")}
        if "documents" in maj:
            infos["nb_documents"] = len(maj["documents"])
        print(f"-> {agent} {infos}")
        resultat.update(maj)

print("\n" + resultat["reponse"])