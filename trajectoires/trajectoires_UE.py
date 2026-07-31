import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
import numpy as np
import os
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt

#filename_global = '/home/florent/Documents/ENM_3A/Aladin/modele_forceur/suiamip_g359_concatene.rel200'
filename_local = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/trajectoires_1/fichiers_traj/autres/suiERA5_evaluation_1960-1961.vor5_res17_1_-2_5.rel200'
filename_D10 = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/trajectoires_1/fichiers_traj/autres/suiERA5_evaluation_1960-1961.vor5_res17_1_-2_5.rel200'
filename_F10 = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/trajectoires_1/fichiers_traj/autres/suiERA5_evaluation_1960-1961.vor5_res17_1_-2_5.rel200'

filename = filename_F10

tracks = {}
current_track_id = None
total_segments = 0
atlantic_tracks_count = 0 # <-- NOUVEAU COMPTEUR ATLANTIQUE

# Définition de la zone de l'Atlantique Nord (approximative)
# Lon: -98°W à 10°E
# Lat: 5°N à 60°N
ATLANTIC_LON_MIN = -88.0
ATLANTIC_LON_MAX = -27.0
ATLANTIC_LAT_MIN = 8.0
ATLANTIC_LAT_MAX = 30.0

def is_in_atlantic(lon, lat):
    """Vérifie si le point est dans la zone Atlantique Nord définie."""
    return True
    return (lon >= ATLANTIC_LON_MIN and lon <= ATLANTIC_LON_MAX and
            lat >= ATLANTIC_LAT_MIN and lat <= ATLANTIC_LAT_MAX)


# --- 1. Lecture des données (Modifié pour le comptage Atlantique) ---
if not os.path.exists(filename):
    print(f"Erreur : Le fichier '{filename}' est introuvable.")
    exit()

with open(filename, 'r') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        if '[' in line: line = line.split(']', 1)[1].strip()
        parts = line.split()
        
        if len(parts) > 0 and len(parts) < 5:
            # Fin de la lecture de la trajectoire précédente. 
            # On stocke l'ID et on prépare le dictionnaire pour la nouvelle.
            current_track_id = parts[0]
            tracks[current_track_id] = {'lat': [], 'lon': [], 'press': []}
            continue

        if len(parts) >= 5 and current_track_id:
            try:
                lon_val = float(parts[1])
                lat_val = float(parts[2])
                pressure_val = float(parts[-1])
                
                if lon_val > 180: lon_val -= 360
                
                # Enregistrement des données
                tracks[current_track_id]['lon'].append(lon_val)
                tracks[current_track_id]['lat'].append(lat_val)
                tracks[current_track_id]['press'].append(pressure_val)
            except ValueError:
                continue

# --- Filtrage et Comptage des trajectoires Atlantique (Nouvelle étape) ---
# On va maintenant vérifier le premier point de chaque trajectoire
final_tracks_to_plot = {}
for track_id, data in tracks.items():
    if data['lon']:
        first_lon = data['lon'][0]
        first_lat = data['lat'][0]
        
        if is_in_atlantic(first_lon, first_lat):
            atlantic_tracks_count += 1
            final_tracks_to_plot[track_id] = data # Garder seulement celles dans l'Atlantique
        # Si on voulait tracer toutes les trajectoires, on ferait juste: final_tracks_to_plot[track_id] = data 

tracks = final_tracks_to_plot # Utiliser uniquement les trajectoires filtrées pour le tracé

# --- 2. Configuration de la carte avec Cartopy (Identique) ---
request_tiler = cimgt.OSM()

plt.figure(figsize=(12, 10))
ax = plt.axes(projection=request_tiler.crs)

# Calcul des limites de la carte pour centrer sur les données (Optionnel: on pourrait centrer uniquement sur l'Atlantique)
all_lons = [lon for t in tracks.values() for lon in t['lon']]
all_lats = [lat for t in tracks.values() for lat in t['lat']]

if all_lons and all_lats:
    margin = 5
    # Utilisation des limites des données si elles existent
    ax.set_extent([min(all_lons)-margin, max(all_lons)+margin, 
                   min(all_lats)-margin, max(all_lats)+margin], 
                  crs=ccrs.PlateCarree())
else:
    # Si aucune trajectoire n'est dans la zone, on centre sur l'Atlantique
    ax.set_extent([ATLANTIC_LON_MIN, ATLANTIC_LON_MAX, ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX], 
                  crs=ccrs.PlateCarree())


# Ajout du fond de carte OSM (Zoom level 4 est un bon compromis)
ax.add_image(request_tiler, 4)

# --- 3. Tracé des lignes colorées (Utilise tracks filtrées) ---
all_pressures = [p for t in tracks.values() for p in t['press']]
# S'assurer que norm est défini même si all_pressures est vide
if all_pressures:
    norm = plt.Normalize(min(all_pressures), max(all_pressures))
else:
    norm = plt.Normalize(900, 1020) # Norme par défaut

for track_id, data in tracks.items():
    if len(data['lon']) < 2: continue

    x = np.array(data['lon'])
    y = np.array(data['lat'])
    p = np.array(data['press'])

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Mise à jour du compteur de segments
    total_segments += len(segments)

    lc = LineCollection(segments, cmap='jet_r', norm=norm, 
                        transform=ccrs.PlateCarree())
    
    lc.set_array(p[:-1])
    lc.set_linewidth(2)
    ax.add_collection(lc)

# --- 4. Finalisation ---
# Barre de couleur (affichée uniquement si des données sont présentes)
if all_pressures:
    sm = plt.cm.ScalarMappable(cmap='jet_r', norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label('Pression (hPa)')

# Grille
gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
gl.top_labels = False
gl.right_labels = False

# Mise à jour du titre pour inclure les deux compteurs
plt.title(f"Trajectoires sur fond OpenStreetMap\n({atlantic_tracks_count} trajectoires Atlantique, {total_segments} segments tracés)")
plt.show()