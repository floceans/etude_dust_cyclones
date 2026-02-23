import matplotlib.pyplot as plt
import numpy as np
import os
import csv
import sys
from scipy.stats import gaussian_kde
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# --- 1. Gestion des arguments ---

year_min = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
year_max = int(sys.argv[2]) if len(sys.argv) > 2 else 2022

dir_path = 'trac_3/' # Dossier contenant les fichiers .csv
output_dir = 'images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- 2. Lecture des fichiers ERA5 ---
all_lons = []
all_lats = []

print(f"Analyse des fichiers ERA5 pour la période {year_min}-{year_max}...")

# Liste tous les fichiers qui commencent par 'suiERA5' et finissent par '.csv'
files = [f for f in os.listdir(dir_path) if f.startswith('suiERA5') and f.endswith('.csv')]

for filename in files:
    # On vérifie si l'année du fichier est dans la plage [year_min, year_max]
    # Les fichiers ont souvent l'année au début (ex: 1960-1961)
    try:
        # Extraction simplifiée de l'année dans le nom du fichier pour le filtrage
        file_years = [int(s) for s in filename.split('_') if '-' in s and s.split('-')[0].isdigit()]
        if file_years:
            start_f = int(filename.split('_')[2].split('-')[0])
            if start_f < year_min or start_f > year_max:
                continue
    except:
        pass # Au cas où le format du nom varie, on peut aussi tout lire et filtrer par la colonne 'date'

    file_path = os.path.join(dir_path, filename)
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f) # Utilisation de DictReader pour éviter les erreurs d'index
        for row in reader:
            try:
                # Filtrage optionnel par la date dans le fichier si nécessaire
                year_row = int(row['date'].split('-')[0])
                if year_min <= year_row <= year_max:
                    lon = float(row['lon'])
                    lat = float(row['lat'])
                    
                    if lon > 180: lon -= 360
                    all_lons.append(lon)
                    all_lats.append(lat)
            except (ValueError, KeyError):
                continue

if not all_lons:
    print("Aucune donnée trouvée.")
    sys.exit()

x = np.array(all_lons)
y = np.array(all_lats)

# --- 3. Calcul de la densité (KDE) ---
lonmin, lonmax = -100, -10
latmin, latmax = 5, 35

xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]
positions = np.vstack([xi.flatten(), yi.flatten()])
values = np.vstack([x, y])

kernel = gaussian_kde(values)
zi = kernel(positions)
zi = zi.reshape(xi.shape) * (len(x) / 100)

# --- 4. Plot (Style demandé) ---
plt.figure(figsize=(14, 9))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

ax.stock_img()
ax.coastlines(resolution='50m', color='black', linewidth=1)
ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5)

# Densité Turbo
levels = np.linspace(0, zi.max(), 15)
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=ccrs.PlateCarree(), alpha=0.8)

# Isolignes + Labels
cs = ax.contour(xi, yi, zi, levels=levels, colors='black', linewidths=0.5, alpha=0.4, transform=ccrs.PlateCarree())
ax.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')

cbar = plt.colorbar(cf, orientation='horizontal', pad=0.08, shrink=0.6)
cbar.set_label('Densité de trajectoires Aladin/ERA5')

ax.set_title(f'Densité Aladin/ERA5 : {year_min} - {year_max}', fontsize=14, fontweight='bold')

# Formatting axes
ax.set_xticks(np.arange(lonmin, lonmax+1, 20), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(latmin, latmax+1, 10), crs=ccrs.PlateCarree())
ax.xaxis.set_major_formatter(LongitudeFormatter())
ax.yaxis.set_major_formatter(LatitudeFormatter())

plt.savefig(f'{output_dir}/density_ERA5_only_{year_min}_{year_max}.png', dpi=200)
plt.show()