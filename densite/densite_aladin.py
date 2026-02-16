import pandas as pd
import numpy as np
import sys
import os
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


year_min = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
year_max = int(sys.argv[2]) if len(sys.argv) > 2 else 2022

file_path = 'ibtracs.NA.list.v04r01_1960-2024.csv'
output_dir = 'images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Chargement des données (skiprow=[1] pour sauter la ligne des unités)
print(f"Chargement des données de {year_min} à {year_max}...")
df = pd.read_csv(file_path, skiprows=[1], low_memory=False)

# 3. Prétraitement
# Conversion en numérique (les données manquantes deviennent NaN)
df['WMO_WIND'] = pd.to_numeric(df['WMO_WIND'], errors='coerce')
df['WMO_PRES'] = pd.to_numeric(df['WMO_PRES'], errors='coerce')
df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
df['SEASON'] = pd.to_numeric(df['SEASON'], errors='coerce')

# Conversion noeuds -> m/s (1 kt = 0.514444 m/s)
df['wind_ms'] = df['WMO_WIND'] * 0.514444

# Filtrage : Période + Vent > 17 m/s + Coordonnées valides
mask = (df['SEASON'] >= year_min) & \
       (df['SEASON'] <= year_max) & \
       (df['wind_ms'] > 17) & \
       (df.LAT.notnull()) & (df.LON.notnull())

df_filtered = df[mask]

if df_filtered.empty:
    print("Aucune donnée trouvée pour ces critères.")
    sys.exit()

x = df_filtered['LON'].values
y = df_filtered['LAT'].values

# 4. Calcul de la densité (KDE)
print(f"Calcul de la densité pour {len(x)} points...")
# Définition du domaine (Atlantique Nord)
lonmin, lonmax = -100, -10
latmin, latmax = 5, 50

k = gaussian_kde(np.vstack([x, y]))
xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]
zi = k(np.vstack([xi.flatten(), yi.flatten()])) 

# Normalisation pour l'affichage (ajustement selon ton script original)
zi = zi.reshape(xi.shape) * (len(x) / 100)

# 5. Plot
plt.figure(figsize=(12, 7))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

# Ajout des traits de côte et grille
ax.coastlines(resolution='50m', color='black', linewidth=1)
ax.stock_img() # Fond de carte optionnel

# Tracé de la densité
levels = np.linspace(0, zi.max(), 15)
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='YlOrRd', transform=ccrs.PlateCarree(), alpha=0.8)

plt.colorbar(cf, label='Densité d\'activité (Points > 17m/s)', orientation='vertical', shrink=0.7)

ax.set_title(f'Densité des Cyclones IBTrACS (WMO Wind > 17 m/s)\nPériode: {year_min} - {year_max}', fontsize=12)

# Formattage des axes
ax.set_xticks(np.arange(lonmin, lonmax+1, 20), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(latmin, latmax+1, 10), crs=ccrs.PlateCarree())
ax.xaxis.set_major_formatter(LongitudeFormatter())
ax.yaxis.set_major_formatter(LatitudeFormatter())

output_name = f'{output_dir}/density_{year_min}_{year_max}.png'
plt.savefig(output_name, dpi=200, bbox_inches='tight')
print(f"Carte sauvegardée : {output_name}")
plt.show()