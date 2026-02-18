import csv
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys

# --- 1. Paramètres et fonctions ---
def get_filename(argv):
    if len(argv) > 3 and argv[3] == 'ibtracs':
        return 'ibtracs_transformed_1960_2024.csv'
    return 'ALADIN_rel10_1960_2024.csv'

yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else 2022 
filename = get_filename(sys.argv)

lons = []
lats = []

# --- 2. Lecture manuelle du CSV (sans Pandas) ---
print(f"--- Extraction des points de cyclogenèse (step=1) dans {filename} ---")

with open(filename, mode='r', encoding='utf-8') as f:

    nbr = 0
    reader = csv.DictReader(f)
    for row in reader:
        # Extraction de l'année depuis la date (format attendu YYYY-MM-DD...)
        year = int(row['date'][:4])
        
        # Filtrage : Année ET Cyclogenèse (step=1)
        if yearmin <= year <= yearmax and row['step'] == '1':
            nbr += 1
            # On affiche la ligne correspondante
            print(f"Cyclone {nbr} | Step: {row['step']} | Date: {row['date']} | Lon: {row['lon']} | Lat: {row['lat']}")
            
            lons.append(float(row['lon']))
            lats.append(float(row['lat']))

# Conversion en arrays numpy pour les calculs
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

# Mise à l'échelle
zi = zi.reshape(xi.shape) * (len(x) / 4 * 25)

# --- 4. Plotting ---
proj = ccrs.PlateCarree()
projcl = ccrs.PlateCarree(central_longitude=-50)

fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection=projcl)

ax.set_title(f'Cyclogenesis Density (step=1) [{yearmin}-{yearmax}]', fontsize=12)
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
ax.coastlines(resolution='50m', color='black', linewidth=1)

# Tracé
levels = np.linspace(0, zi.max(), 25)
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='max')
plt.colorbar(cf, orientation='horizontal', pad=0.1, label='Density Scale')

plt.tight_layout()
plt.show()