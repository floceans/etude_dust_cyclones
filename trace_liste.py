import matplotlib.pyplot as plt
import numpy as np

# Données
labels = ['Aladin 3s/4s', 'Aladin 3s/merra', 'Aladin 4s/merra']
tt_domaine = [0.014, 0.045, 0.046]
MDR = [0.02, 0.053, 0.057]
box_sahara = [0.031, 0.101, 0.0884]

tt_domaine_jjaso = [0.021, 0.046, 0.045]
MDR_jjaso = [0.019, 0.026, 0.042]
box_sahara_jjaso = [0.036, 0.091, 0.077]

MDR_jjaso_ATL = [0.023, 0.029, 0.048]
MDR_jjaso_CAR = [0.006, 0.02, 0.026]
box_sahara_new = [0.034, 0.103, 0.088]

x = np.arange(len(labels))  # Position des étiquettes
width = 0.20  # Largeur des barres

fig, ax = plt.subplots(figsize=(10, 6))

# Création des barres
rects1 = ax.bar(x - width*3/2, tt_domaine_jjaso, width, label='Grand_domaine', color='#3498db')
rects2 = ax.bar(x + width*3/2, MDR_jjaso_ATL, width, label='MDR Atlantique', color='#e67e22')
rects3 = ax.bar(x - width/2, box_sahara_jjaso, width, label='Box_sahara', color='#2ecc71')
rects4 = ax.bar(x + width/2, MDR_jjaso_CAR, width, label='MDR Caraïbes', color="#E72195")

# Ajout des textes, titres et légendes
ax.set_ylabel('RMSE AOD')
ax.set_title('RMSE spaciaux sur moyennes temporelles, par data et domaine, JJASO')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# Optionnel : ajouter les valeurs au-dessus des barres
ax.bar_label(rects1, padding=3)
ax.bar_label(rects2, padding=3)
ax.bar_label(rects3, padding=3)
ax.bar_label(rects4, padding=4)

fig.tight_layout()

plt.show()