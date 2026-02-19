import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import os
import csv
import sys
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

'''
1er arg -> année début, defaut : 2020
2eme arg -> annee fin, defaut : 2022
3eme arg -> seuil pression maximale dans plot, defaut : 1000
'''


###
#appliquer seuil sur vorticité sur traj relaxés rel10
#impacts SAL sur cyclogenese  => c quoi cyclogenese sur aladin (reel vmax>17m/s), seuil sur vorticité ?
# carte densité cyclogenese, trouver seuil vorticité
# comparer densité ibtracks & aladin
# run de controle :forcé par era5 avec effets aerosols
# sans effet : nora dust, 
###

data = 'aladin'
yearmin = 1962
yearmax = 2024
seuil_p = 1010


# --- Gestion des args ---
if len(sys.argv) > 1 and sys.argv[1] == 'aladin':
    filename = "/home/florent/Documents/CNRM/git/etude_dust_cyclones/ALADIN_rel10_1960_2024.csv" 
elif len(sys.argv) > 1 and sys.argv[1] == 'ibtracks':
    filename = "/home/florent/Documents/CNRM/git/etude_dust_cyclones/ibtracs_transformed_1960_2024.csv" 
elif data == 'aladin':
    filename = "/home/florent/Documents/CNRM/git/etude_dust_cyclones/ALADIN_rel10_1960_2024_old.csv"
elif data == 'ibtracks':
    filename = "/home/florent/Documents/CNRM/git/etude_dust_cyclones/ibtracs_transformed_1960_2024.csv"
else:
    print("data aladin par défaut")
    filename = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/ALADIN_rel10_1960_2024.csv' # Valeur par défaut

annee_debut = int(sys.argv[2]) if len(sys.argv) > 2 else yearmin

# Si len(sys.argv) > 2, on prend l'argument 2, sinon on met 1961 par défaut
annee_fin = int(sys.argv[3]) if len(sys.argv) > 3 else yearmax

seuil_p = int(sys.argv[4]) if len(sys.argv) > 4 else seuil_p

# Zone Atlantique Nord pour le filtrage (activable au besoin)
ATLANTIC_LON_MIN, ATLANTIC_LON_MAX = -88.0, -27.0
ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX = 8.0, 35.0

def is_in_atlantic(lon, lat):
    # Pour activer le filtre, décommente la ligne ci-dessous
    # return (ATLANTIC_LON_MIN <= lon <= ATLANTIC_LON_MAX and ATLANTIC_LAT_MIN <= lat <= ATLANTIC_LAT_MAX)
    return True

tracks = {}

# --- Lecture du CSV ---
if not os.path.exists(filename):
    print(f"Erreur : Le fichier '{filename}' est introuvable.")
    sys.exit()

print(f"Lecture de {filename} pour la période {annee_debut}-{annee_fin}...")

with open(filename, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # On récupère l'année de la ligne (nom de colonne à adapter si différent, ex: 'year')
        # Si ton CSV n'a pas de colonne 'year', retire cette condition de filtrage
        try:
            row_year = int(float(row.get('year', row.get('date', annee_debut)[:4]))) 
        except:
            row_year = annee_debut # Fallback

        if not (annee_debut <= row_year <= annee_fin):
            continue

        pmin = float(row['pmin'])
        if pmin > seuil_p:
            continue

        # Création d'un ID unique par système
        track_id = f"{row_year}_{row['numtc']}"
        
        if track_id not in tracks:
            tracks[track_id] = {'lat': [], 'lon': [], 'press': []}
        
        lon_val = float(row['lon'])
        if lon_val > 180: lon_val -= 360 
        
        tracks[track_id]['lon'].append(lon_val)
        tracks[track_id]['lat'].append(float(row['lat']))
        tracks[track_id]['press'].append(pmin)

# --- Filtrage des trajectoires vides ou hors zone ---
final_tracks = {tid: data for tid, data in tracks.items() 
                if len(data['lon']) > 1 and is_in_atlantic(data['lon'][0], data['lat'][0])}

print(f"Nombre de trajectoires à afficher : {len(final_tracks)}")

if not final_tracks:
    print("Aucune donnée ne correspond aux critères.")
    sys.exit()

# --- Création de la carte ---
fig = plt.figure(figsize=(15, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([-100, 10, 0, 45], crs=ccrs.PlateCarree()) 

ax.stock_img()
ax.coastlines(resolution='50m', color='black', linewidth=1)

gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.3)
gl.top_labels = False 
gl.right_labels = False
gl.xformatter = LongitudeFormatter()
gl.yformatter = LatitudeFormatter()

# --- Tracé des trajectoires ---
# Normalisation des couleurs basée sur la pression min/max trouvée
all_pressures = [p for t in final_tracks.values() for p in t['press']]
norm = plt.Normalize(min(all_pressures), max(all_pressures))

for tid, data in final_tracks.items():
    x = np.array(data['lon'])
    y = np.array(data['lat'])
    p = np.array(data['press'])

    # Transformation pour LineCollection (segments de couleurs)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    lc = LineCollection(segments, cmap='jet_r', norm=norm, transform=ccrs.PlateCarree())
    lc.set_array(p[:-1])
    lc.set_linewidth(1.5)
    lc.set_alpha(0.7)
    ax.add_collection(lc)

# Barre de couleur
sm = plt.cm.ScalarMappable(cmap='jet_r', norm=norm)
cb = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, aspect=30, shrink=0.8)
cb.set_label('Pression centrale (hPa)')

plt.title(f"Trajectoires {annee_debut}-{annee_fin} (Pmin < {seuil_p} hPa)\nSource: {os.path.basename(filename)}")

# Sauvegarde
output_name = f"plot_trajs_{annee_debut}_{annee_fin}.png"
plt.savefig(output_name, dpi=200, bbox_inches='tight')
print(f"Graphique sauvegardé sous : {output_name}")
plt.show()