import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

val_indices_tt_domaine = [907,907,894,848,821,747,708,687,670,654,651,649,661,683,743,796,935]

val_vorti_tt_domaine = [1,10,15,25,30,40,45,50,55,60,62.5,65,67.5,70,80,90,100]


val_vorti_mdr = [0,10,15,20,25,35,45,55,65,67.5,70,72.5,75,80,85,95,100]

val_indice_mdr = [801,801,810,814,835,831,792,783,771,767,757,762,765,771,791,796,796]

plt.plot(val_vorti_tt_domaine, val_indices_tt_domaine, label = 'Tout domaine')
plt.plot(val_vorti_mdr, val_indice_mdr, label = 'Domaine MDR')
plt.title("Différence d'intensité cyclogénèse (ALADIN - IBTRACS) selon seuil vorticité sur ALADIN")
plt.xlabel('seuil vorticité')
plt.ylabel('\Delta intensité cyclogénèse')
plt.legend()
plt.show()

