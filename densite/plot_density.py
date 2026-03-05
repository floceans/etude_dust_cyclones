import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import sys
from func import fichier_source, indice_global_cyclogenese, get_density



file = 'aladin'
yearmin = 1960
yearmax = 2024

filename = fichier_source(sys.argv if len(sys.argv)>0 else None, file)

print(filename)


yearmin = int(sys.argv[2]) if len(sys.argv) > 2 else yearmin
yearmax = int(sys.argv[3]) if len(sys.argv) > 3 else yearmax


lonmin, lonmax, latmin, latmax = -105, 5, 5, 35
xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]

zi, x, y, long_x = get_density(filename, yearmin, yearmax, xi, yi)


indice = indice_global_cyclogenese(zi, lonmin, lonmax, latmin, latmax)
print(f"Indice global de cyclogenèse (step=1) pour {filename} : {indice:.2f} (nombre de points : {long_x})")


# --- 3. Plotting ---
proj = ccrs.PlateCarree()
# On centre la carte sur la zone d'intérêt
clon = -50 
projcl = ccrs.PlateCarree(central_longitude=clon)

fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection=projcl)

ax.set_title(f'Track Density {file} [{yearmin}-{yearmax}]', fontsize=12, pad=15)
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)

# Ajout des côtes et grille
ax.coastlines(resolution='50m', color='black', linewidth=1)

# Tracé de la densité avec la colormap 'turbo'
levels = np.linspace(0, 150, 16) ###################" changer pour mm echelle"
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='max')

cs = ax.contour(xi, yi, zi, levels=levels, colors='black', linewidths=0.5, alpha=0.4, transform=ccrs.PlateCarree())
ax.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')

# Barre d'échelle
cbar = plt.colorbar(cf, ax=ax, orientation='horizontal', pad=0.1, aspect=40)
cbar.set_label('Relative Density Scale')

plt.tight_layout()
plt.show()