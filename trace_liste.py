import matplotlib.pyplot as plt
import numpy as np

val_indices = [907,
    907,
    894,
    848,
    821,
    747,
    708,
    687,
    670,
    654,
    651,
    649,
    661,
    683,
    743,
    796,
    935]

val_vorti = [1,
10,
15,
25,
30,
40,
45,
50,
55,
60,
62.5,
65,
67.5,
70,
80,
90,
100]

print(val_indices)

plt.plot(val_vorti, val_indices)
plt.title("Différence d'intensité cyclogénèse (ALADIN - IBTRACS) selon seuil vorticité sur ALADIN")
plt.xlabel('seuil vorticité')
plt.ylabel('\Delta intensité cyclogénèse')
plt.show()