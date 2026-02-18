import csv
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys
from func import fichier_source, indice_global_cyclogenese

    



filename = fichier_source(sys.argv)

yearmin = int(sys.argv[2]) if len(sys.argv) > 2 else 2018
yearmax = int(sys.argv[3]) if len(sys.argv) > 3 else 2022 

lons = []
lats = []

# --- 2. Lecture manuelle du CSV ---
print(f"--- Extraction des points de cyclogenèse (step=1) dans {filename} ---")

with open(filename, mode='r', encoding='utf-8') as f:
    nbr = 0
    reader = csv.DictReader(f)
    for row in reader:
        year = int(row['date'][:4])
        if yearmin <= year <= yearmax and row['step'] == '1':
            nbr += 1
            lons.append(float(row['lon']))
            lats.append(float(row['lat']))

x = np.array(lons)
y = np.array(lats)

if len(x) < 10:
    print("Erreur : Pas assez de points trouvés.")
    sys.exit()

# --- 3. Calcul de la densité (KDE) ---
lonmin, lonmax = -105, 5
latmin, latmax = 5, 35

xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]
coords = np.vstack([xi.flatten(), yi.flatten()])

k = gaussian_kde(np.vstack([x, y]))
zi = k(coords)
zi = zi.reshape(xi.shape) * (len(x) / 4 * 25)

indice = indice_global_cyclogenese(zi, lonmin, lonmax, latmin, latmax)
print(f"Indice global de cyclogenèse (step=1) pour {filename} : {indice:.2f} (nombre de points : {len(x)})")


# --- 4. Plotting ---
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