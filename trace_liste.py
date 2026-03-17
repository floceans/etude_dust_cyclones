import matplotlib.pyplot as plt
import numpy as np

# Données
labels = ['Aladin 3s/4s', 'Aladin 3s/merra', 'Aladin 4s/merra']
tt_domaine = [0.014, 0.045, 0.046]
MDR = [0.02, 0.053, 0.057]
box_sahara = [0.031, 0.101, 0.0884]

x = np.arange(len(labels))  # Position des étiquettes
width = 0.25  # Largeur des barres

fig, ax = plt.subplots(figsize=(10, 6))

# Création des barres
rects1 = ax.bar(x - width, tt_domaine, width, label='tt_domaine', color='#3498db')
rects2 = ax.bar(x, MDR, width, label='MDR', color='#e67e22')
rects3 = ax.bar(x + width, box_sahara, width, label='box_sahara', color='#2ecc71')

# Ajout des textes, titres et légendes
ax.set_ylabel('Valeurs')
ax.set_title('Comparaison des domaines par configuration Aladin')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Optionnel : ajouter les valeurs au-dessus des barres
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.bar_label(rects3, padding=3)

fig.tight_layout()

plt.show()