"""Passerelle MCP — expose l'API REST de RITA à un client LLM.

MCP (*Model Context Protocol*) est un protocole standard qui décrit des **outils**
à un modèle de langage : leur nom, leurs entrées, leurs sorties et leurs erreurs.
Le modèle décide **quand** appeler un outil ; ce code décide **comment** il s'exécute.

⚠️ Le paquet ne s'appelle pas `mcp` : ce nom est celui du SDK installé, et il serait
masqué par un paquet local du même nom.
"""
