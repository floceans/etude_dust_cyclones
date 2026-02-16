import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import os
import pandas as pd
import sys
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# --- Gestion des arguments ---
# Usage: python traj_ibtracks.py 2005 2005
annee_debut = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
annee_fin = int(sys.argv[2]) if len(sys.argv) > 2 else 2022
seuil_vitesse = 17 # m/s (seuil tempête tropicale)

file_path = '../ibtracs.NA.list.v04r01_1960-2024.csv'

# --- Chargement des données ---
print(f"Chargement des trajectoires IBTrACS de {annee_debut} à {annee_fin}...")
# Skiprow=[1] car IBTrACS a une ligne d'unités après l'en-tête
df = pd.read_csv(file_path, skiprows=[1], low_memory=False)

# Conversion des types
cols = ['SEASON', 'LAT', 'LON', 'WMO_WIND', 'WMO_PRES']
for col in cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Conversion vent nœuds -> m/s
df['wind_ms'] = df['WMO_WIND'] * 0.514444

# --- Filtrage ---
mask = (df['SEASON'] >= annee_debut) & (df['SEASON'] <= annee_fin)
df_filtered = df[mask].copy()

if df_filtered.empty:
    print("Aucune donnée trouvée pour cette période.")
    sys.exit()

# --- Reconstruction des trajectoires ---
# On groupe par SID (identifiant unique de la tempête)
final_tracks = {}
for sid, group in df_filtered.groupby('SID'):
    # On trie par temps si nécessaire (IBTrACS est déjà trié par défaut)
    group = group.dropna(subset=['LAT', 'LON', 'WMO_PRES'])
    
    if len(group) > 2:
        final_tracks[sid] = {
            'lon': group['LON'].values,
            'lat': group['LAT'].values,
            'press': group['WMO_PRES'].values,
            'name': group['NAME'].iloc[0]
        }

print(f"Nombre de trajectoires trouvées : {len(final_tracks)}")

# --- Création de la carte ---
fig = plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-100, -10, 5, 35], crs=ccrs.PlateCarree())

ax.coastlines(resolution='50m', color='black', linewidth=1.2)
ax.stock_img() # Ajoute un fond relief/océan

# --- Tracé des trajectoires ---
# On récupère toutes les pressions pour l'échelle de couleur
all_pressures = [p for t in final_tracks.values() for p in t['press']]
norm = plt.Normalize(min(all_pressures), max(all_pressures))
cmap = plt.get_cmap('jet_r') # _r pour avoir le rouge (basse pression) en bas

for sid, data in final_tracks.items():
    x = data['lon']
    y = data['lat']
    p = data['press']

    # Création des segments pour LineCollection
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    lc = LineCollection(segments, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
    lc.set_array(p)
    lc.set_linewidth(2)
    ax.add_collection(lc)

# --- Esthétique et Labels ---
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.7, pad=0.02)
cbar.set_label('Pression au centre (hPa)')

ax.set_title(f'Trajectoires IBTrACS (Atlantique Nord)\nPériode : {annee_debut} - {annee_fin}', 
             fontsize=15, fontweight='bold')

# Grille et axes
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.3)
gl.top_labels = False
gl.right_labels = False

output_name = f'tracks_{annee_debut}_{annee_fin}.png'
plt.savefig(output_name, dpi=200, bbox_inches='tight')
print(f"Carte sauvegardée : {output_name}")
plt.show()