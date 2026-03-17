import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import os
import csv
import sys
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# --- Configuration et Seuils ---
data = 'aladin'
yearmin = 2018
yearmax = 2022
seuil_p = 1005

ATLANTIC_LON_MIN, ATLANTIC_LON_MAX = -95.0, -10.0
ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX = 5.0, 30.0

# --- Gestion des arguments CLI ---
if len(sys.argv) > 1 and sys.argv[1] == 'aladin':
    filename = "ALADIN_rel10_1960_2024.csv" 
elif len(sys.argv) > 1 and sys.argv[1] == 'ibtracs':
    filename = "ibtracs_transformed_1960_2024.csv" 
else:
    filename = "ibtracs_transformed_1960_2024.csv" if data == 'ibtracs' else "ALADIN_rel10_1960_2024.csv"

annee_debut = int(sys.argv[2]) if len(sys.argv) > 2 else yearmin
annee_fin = int(sys.argv[3]) if len(sys.argv) > 3 else yearmax
seuil_p = int(sys.argv[4]) if len(sys.argv) > 4 else seuil_p

tracks_raw = {}

# --- Lecture du CSV ---
if not os.path.exists(filename):
    print(f"Erreur : Le fichier '{filename}' est introuvable.")
    sys.exit()

print(f"Lecture de {filename}...")

with open(filename, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            row_year = int(float(row.get('year', row.get('date', annee_debut)[:4]))) 
        except:
            row_year = annee_debut

        if not (annee_debut <= row_year <= annee_fin):
            continue

        pmin = float(row['pmin'])
        if pmin > seuil_p:
            continue

        track_id = f"{row_year}_{row['numtc']}"
        if track_id not in tracks_raw:
            tracks_raw[track_id] = {'lat': [], 'lon': [], 'press': []}
        
        lon_val = float(row['lon'])
        if lon_val > 180: lon_val -= 360 
        
        tracks_raw[track_id]['lon'].append(lon_val)
        tracks_raw[track_id]['lat'].append(float(row['lat']))
        tracks_raw[track_id]['press'].append(pmin)

# --- Filtrage STRICT par zone (Point par Point) ---
final_tracks = {}
total_points_in_zone = 0

for tid, tdata in tracks_raw.items():
    filtered_lon = []
    filtered_lat = []
    filtered_press = []
    
    for i in range(len(tdata['lon'])):
        ln, lt, pr = tdata['lon'][i], tdata['lat'][i], tdata['press'][i]
        
        # Vérification si le point est dans le rectangle
        if (ATLANTIC_LON_MIN <= ln <= ATLANTIC_LON_MAX) and (ATLANTIC_LAT_MIN <= lt <= ATLANTIC_LAT_MAX):
            filtered_lon.append(ln)
            filtered_lat.append(lt)
            filtered_press.append(pr)
            
    # On ne garde la trajectoire que si elle possède au moins 2 points dans la zone (pour tracer une ligne)
    if len(filtered_lon) >= 2:
        final_tracks[tid] = {
            'lon': filtered_lon,
            'lat': filtered_lat,
            'press': filtered_press
        }
        total_points_in_zone += len(filtered_lon)

# --- Calcul des statistiques ---
num_trajs = len(final_tracks)
avg_pts = total_points_in_zone / num_trajs if num_trajs > 0 else 0

print(f"Nombre de trajectoires impactant la zone : {num_trajs}")
print(f"Nombre moyen de points par trajectoire dans le domaine : {avg_pts:.2f}")

if not final_tracks:
    print("Aucune donnée dans la zone avec les seuils actuels.")
    sys.exit()

# --- Création de la carte ---
fig = plt.figure(figsize=(15, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([ATLANTIC_LON_MIN, ATLANTIC_LON_MAX, ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX], crs=ccrs.PlateCarree()) 

ax.stock_img()
ax.coastlines(resolution='50m', color='black', linewidth=1)

gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.3)
gl.top_labels = False 
gl.right_labels = False
gl.xformatter = LongitudeFormatter()
gl.yformatter = LatitudeFormatter()

# Normalisation
all_pressures = [p for t in final_tracks.values() for p in t['press']]
norm = plt.Normalize(min(all_pressures), max(all_pressures))

# --- Tracé ---
for tid, data in final_tracks.items():
    x = np.array(data['lon'])
    y = np.array(data['lat'])
    p = np.array(data['press'])

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    lc = LineCollection(segments, cmap='jet_r', norm=norm, transform=ccrs.PlateCarree())
    lc.set_array(p[:-1])
    lc.set_linewidth(1.5)
    lc.set_alpha(0.8)
    ax.add_collection(lc)

# Barre de couleur
sm = plt.cm.ScalarMappable(cmap='jet_r', norm=norm)
cb = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, aspect=30, shrink=0.8)
cb.set_label('Pression centrale (hPa)')

plt.title(f"Trajectoires {annee_debut}-{annee_fin} (Uniquement points dans le domaine)\n"
          f"Moyenne : {avg_pts:.1f} pts/traj | Source: {os.path.basename(filename)}")

# Sauvegarde
output_name = f"plot_trajs_filtered_{annee_debut}_{annee_fin}.png"
plt.savefig(output_name, dpi=200, bbox_inches='tight')
print(f"Graphique sauvegardé : {output_name}")
plt.show()