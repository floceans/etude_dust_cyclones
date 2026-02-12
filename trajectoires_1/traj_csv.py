import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import os
import csv
import sys
import cartopy.crs as ccrs

# --- Gestion des args ---


annee_debut = int(sys.argv[1]) if len(sys.argv) > 1 else 2020

# Si len(sys.argv) > 2, on prend l'argument 2, sinon on met 1961 par défaut
annee_fin = int(sys.argv[2]) if len(sys.argv) > 2 else 2022


# Zone Atlantique Nord pour le filtrage ###############"" filtrage spacial, mais déjà pas de data lat>30, why ??
ATLANTIC_LON_MIN, ATLANTIC_LON_MAX = -88.0, -27.0
ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX = 8.0, 70.0

def is_in_atlantic(lon, lat):
    #Filtre sur premier point de la trajectoire
    # return (lon >= ATLANTIC_LON_MIN and lon <= ATLANTIC_LON_MAX and 
    #         lat >= ATLANTIC_LAT_MIN and lat <= ATLANTIC_LAT_MAX)
    return True

tracks = {}

# --- Lecture CSV ---
for year in range(annee_debut, annee_fin):
    #filename = f"/home/florent/Documents/CNRM/git/etude_dust_cyclones/trajectoires_1/fichiers_traj/suiERA5_evaluation_{year}-{year+1}.vor5_res17_1_-2_5.rel200.csv"
    filename = f"fichiers_traj/suiERA5_evaluation_{year}-{year+1}.vor5_res17_1_-2_5.rel200.csv"

    if not os.path.exists(filename):
        print(f"Attention : Le fichier '{filename}' est introuvable. Passage au suivant.")
        continue

    print(f"Lecture de {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        # Utilisation de DictReader pour mapper automatiquement les colonnes [cite: 10]
        reader = csv.DictReader(f)
        for row in reader:
            # Création d'un ID unique (année + numtc) pour éviter les collisions entre fichiers
            track_id = f"{year}_{row['numtc']}" 
            
            if track_id not in tracks:
                tracks[track_id] = {'lat': [], 'lon': [], 'press': []}
            
            lon_val = float(row['lon'])
            if lon_val > 180: lon_val -= 360 
            
            tracks[track_id]['lon'].append(lon_val)
            tracks[track_id]['lat'].append(float(row['lat']))
            tracks[track_id]['press'].append(float(row['pmin'])) # Pression centrale [cite: 10]




# --- Filtrage --- 
final_tracks = {tid: data for tid, data in tracks.items() 
                if data['lon'] and is_in_atlantic(data['lon'][0], data['lat'][0])}

print(f"Nombre total de trajectoires chargées : {len(final_tracks)}")

if not final_tracks:
    print("Aucune donnée à afficher.")
    sys.exit()


# --- Création de la carte ---
fig = plt.figure(figsize=(15, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([-100, 10, 0, 65], crs=ccrs.PlateCarree()) # cadre du canva ploté 
ax.coastlines(resolution='50m', color='black', linewidth=1.5)
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl.top_labels = False # pr plot label juste une fois en bas et à gauche
gl.right_labels = False



# --- Tracé plot plot plot ---
all_pressures = [p for t in final_tracks.values() for p in t['press']]
norm = plt.Normalize(min(all_pressures), max(all_pressures))

for track_id, data in final_tracks.items():
    if len(data['lon']) < 2: continue

    x = np.array(data['lon'])
    y = np.array(data['lat'])
    p = np.array(data['press'])

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    lc = LineCollection(segments, cmap='jet_r', norm=norm, transform=ccrs.PlateCarree())
    lc.set_array(p[:-1])
    lc.set_linewidth(3)
    lc.set_alpha(0.6)
    ax.add_collection(lc)


sm = plt.cm.ScalarMappable(cmap='jet_r', norm=norm)
cb = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, aspect=30, shrink=0.75)
cb.set_label('Pression au centre (hPa) [pmin]')

plt.title(f"Trajectoires ERA5 : {annee_debut} à {annee_fin} ({len(final_tracks)} systèmes)")
plt.show()