import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.ticker as mticker # <-- Nouvel import indispensable
import sys
from func import fichier_source, indice_global_cyclogenese, get_density_cyclogenese_aladin, get_density_cyclogenese_ibtracs

AN_MIN = 1960
AN_MAX = 2023
SVORT = 0 
SVENT = 26
SPRESS = 1005

file = 'ALADIN-NoRadDust'

## fichiers source & args
filename = 'ALADIN-NoRadDust-rel10_1960_2000.csv' #'ibtracs_transformed_1960_2024.csv' # #  'ALADIN_rel10_1960_2024.csv'
# #fichier_source(sys.argv, file)

print(filename)

yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else AN_MIN
yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else AN_MAX
seuil_press = int(sys.argv[3]) if len(sys.argv) > 3 else SPRESS ###########" pas pris en compte apres"
seuil_vent = float(sys.argv[4]) if len(sys.argv) > 4 else SVENT #seuil de vort 
seuil_vort = float(sys.argv[5]) if len(sys.argv) > 5 else SVORT #seuil de vort 

#calcul
lonmin, lonmax = -105, 5
latmin, latmax = 5, 30

if filename == 'ALADIN_rel10_1960_2024.csv' or filename == 'ALADIN-NoRadDust-rel10_1960_2000.csv':
    zi, x,y, xi, yi, npts = get_density_cyclogenese_aladin(filename, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vent, seuil_press)
elif filename == 'ibtracs_transformed_1960_2024.csv':
    zi, x,y, xi, yi, npts = get_density_cyclogenese_ibtracs(filename, yearmin, yearmax, lonmin, lonmax, latmin, latmax)
else:
    print(f"Fichier source non reconnu : {filename}. Utilisez 'aladin' ou 'ibtracs' en argument.")


indice = indice_global_cyclogenese(zi, lonmin, lonmax, latmin, latmax)
print(f"Indice global de cyclogenèse pour {filename} : {indice:.2f} (nombre de points : {npts})")
print(f"Années couvertes : {yearmin} à {yearmax}")


# plot
proj = ccrs.PlateCarree()
projcl = ccrs.PlateCarree(central_longitude=-50)

fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection=projcl)

ax.set_title(f'Densité de cyclogénèse {file} [{yearmin}-{yearmax}]', fontsize=21)
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
ax.coastlines(resolution='50m', color='black', linewidth=1)


gl = ax.gridlines(crs=proj, draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False    # Désactive les labels en haut
gl.right_labels = False  # Désactive les labels à droite

# Définition des pas (20 pour lon, 5 pour lat)
gl.xlocator = mticker.MultipleLocator(20)
gl.ylocator = mticker.MultipleLocator(5)

# Taille de la police à 22
gl.xlabel_style = {'size': 22}
gl.ylabel_style = {'size': 22}
# ---------------------------------------------------

# Tracé densité
levels = np.linspace(0, 5, 21)
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='max', alpha=0.8)

cs = ax.contour(xi, yi, zi, levels=levels, colors='black', linewidths=0.5, alpha=0.7, transform=ccrs.PlateCarree())
ax.clabel(cs, inline=False, fontsize=10, fmt='%1.1f')

# Pts de cyclogenèse (prems de chaque cyclone)
ax.scatter(x, y, color='black', marker='o', s=8, transform=proj, 
           edgecolor='white', linewidth=0.2, zorder=5, label='Cyclogenesis points')

# colorbar
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40)
cbar.set_label('Nombre de cyclogénèse par carré de 5 degrés par an', size=20)
cbar.ax.tick_params(labelsize=20)

plt.tight_layout()
plt.show()