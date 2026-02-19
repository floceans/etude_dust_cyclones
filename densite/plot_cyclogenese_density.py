import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys
from func import fichier_source, indice_global_cyclogenese, get_density_cyclogenese_aladin, get_density_cyclogenese_ibtracs


AN_MIN = 1961
AN_MAX = 1961
SVORT = 1 #10,25, 100 à tester selon Fabrice

## fichiers source & args
filename = fichier_source(sys.argv, default='aladin')

yearmin = int(sys.argv[2]) if len(sys.argv) > 2 else AN_MIN
yearmax = int(sys.argv[3]) if len(sys.argv) > 3 else AN_MAX 

seuil_vort = int(sys.argv[4]) if len(sys.argv) > 4 else SVORT #seuil de vorticité pour définir la cyclogenèse (ex: 1e-5 s^-1)

#calcul
lonmin, lonmax = -105, 5
latmin, latmax = 5, 35

if filename == 'ALADIN_rel10_1960_2024.csv':
    zi, x,y, xi, yi, npts = get_density_cyclogenese_aladin(filename, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vort)
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

ax.set_title(f'Cyclogenesis Density (step=1) [{yearmin}-{yearmax}]', fontsize=12)
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
ax.coastlines(resolution='50m', color='black', linewidth=1)

# Tracé densité
levels = np.linspace(0, zi.max(), 25)
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='max', alpha=0.8)

cs = ax.contour(xi, yi, zi, levels=levels, colors='black', linewidths=0.5, alpha=0.4, transform=ccrs.PlateCarree())
ax.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')

# Pts de cyclogenèse (prems de chaque cyclone)
ax.scatter(x, y, color='black', marker='o', s=8, transform=proj, 
           edgecolor='white', linewidth=0.2, zorder=5, label='Cyclogenesis points')

plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40, label='Density Scale')

plt.tight_layout()
plt.show()