import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

# 1. Lecture du fichier sans pandas
vent = []
press = []
#vort = []
rmse = []

with open('resultats_cyclogenese.txt', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Sauter l'en-tête
    for row in reader:
        #vort.append(float(row[0]))
        press.append(float(row[0]))
        vent.append(float(row[1]))
        rmse.append(float(row[2]))


# Conversion en tableaux numpy
x = np.array(vent)
y = np.array(press)
z = np.array(rmse)/(200*200)

# 2. Création d'une grille régulière pour le lissage (interpolation)
xi = np.linspace(x.min(), x.max(), 100)
yi = np.linspace(y.min(), y.max(), 100)
xi, yi = np.meshgrid(xi, yi)

# Interpolation des valeurs de RMSE sur la grille
zi = griddata((x, y), z, (xi, yi), method='cubic')

# 3. Tracé
plt.figure(figsize=(12, 8))

# Création des contours remplis (la "chaleur")
# 'viridis_r' ou 'plasma_r' sont bien car le RMSE est "mieux" quand il est bas
cp = plt.contourf(xi, yi, zi, levels=20, cmap='turbo')
plt.colorbar(cp, label='RMSE')

# Ajout des lignes de contour pour plus de lisibilité
contours = plt.contour(xi, yi, zi, levels=10, colors='white', alpha=0.3)
plt.clabel(contours, inline=True, fontsize=8)

# Affichage des points de mesure réels
plt.scatter(x, y, c='red', s=20, edgecolors='black', label='Points testés')

# Identification du point minimum (le meilleur réglage)
idx_min = np.argmin(z)
plt.plot(x[idx_min], y[idx_min], 'r*', markersize=15, label=f'Minimum (RMSE: {z[idx_min]:.2f} pour vort={y[idx_min]:.1f}, vent={x[idx_min]:.1f})')

plt.xlabel('Seuil Vent ($m.s^{-1}$)')
plt.ylabel('Seuil Pression ($hPa$)')
plt.title('Surface d\'erreur (RMSE) en fonction des seuils de détection')
plt.legend()
plt.grid(alpha=0.2)

plt.gca().invert_yaxis()

plt.show()