# M2 ANDROIDE : Mini-projet de l'UE "Coordination et Consensus Multi-Agents"

On considère (pour la visualisation, et pour donner un sens concret au coût de visite des diff´erents sites) un monde de cases, avec :
• un ensemble de robots
• un ensemble de tˆaches
• les robots disposent d’une visibilité identique d
• les cases à l’intersection entre i et j constituent la zone de négociation Z(i, j)
• l’ensemble constitue un graphe non-orienté que l’on suppose connexe
• on va se limiter à une topologie simple: 3 agents, pas de site à l’intersection de plus de 2 agents. (Donc ligne de 3 agents).
• Optionnel: plus de 3 agents (pose pas mal de problèmes...)

On suppose que chaque agent ne peut trouver un accord qu’avec un seul autre agent (cf. Network Exchange Theory, cours 2).
Si un agent i ne trouve pas d’accord avec j il devra ramasser tous les objets de la zone Z(i, j).
L’objectif est d’implémenter le processus de négociation en supposant :
• que chaque négociation est menée selon un Monotonic Concession Protocol (et n’est pas interrompue) bilatéral (pas plus de deux agents à la fois dans la négociation)
• mais en supposant comme dans Network Exchange Theory que les opportunités de recours constituent le point de conflit