import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
import numpy as np
import os
import csv
import sys
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# --- Configuration et Seuils ---
data = 'aladin'
data_n = data
yearmin = 1985
yearmax = 1990
seuil_p = 2005
seuil_v = 0
FONT_SIZE = 28  # On définit la variable ici pour plus de clarté

ATLANTIC_LON_MIN, ATLANTIC_LON_MAX = -100, 5
ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX = 5.0, 30

# --- Gestion des arguments CLI ---
if len(sys.argv) > 1 and sys.argv[1] == 'aladin':
    filename = "ALADIN_rel10_1960_2024.csv" 
elif len(sys.argv) > 1 and sys.argv[1] == 'ibtracs':
    filename = "ibtracs_transformed_1960_2024.csv" 
elif len(sys.argv) > 1 and sys.argv[1] =='aladin_norad' or data == 'aladin_norad':
    filename = 'ALADIN-NoRadDust-rel10_1960_2000.csv'
    print('data aladin_norad')
else:
    filename = "'/cnrm/mosca/USERS/puyf/stage/data/tracks/ibtracs_transformed_1960_2024.csv" if data == 'ibtracs' else "/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv"

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
            row_year = int(float(row.get('year', row.get('date', str(annee_debut))[:4]))) 
        except:
            row_year = annee_debut

        if not (annee_debut <= row_year <= annee_fin):
            continue

        pmin = float(row['pmin'])
        if pmin > seuil_p:
            continue

        vmax = float(row['vmax'])
        if vmax < seuil_v:
            continue

        track_id = f"{row_year}_{row['numtc']}"
        if track_id not in tracks_raw:
            tracks_raw[track_id] = {'lat': [], 'lon': [], 'press': [], 'vmax': []}
        
        lon_val = float(row['lon'])
        if lon_val > 180: lon_val -= 360 
        
        tracks_raw[track_id]['lon'].append(lon_val)
        tracks_raw[track_id]['lat'].append(float(row['lat']))
        tracks_raw[track_id]['press'].append(pmin)
        tracks_raw[track_id]['vmax'].append(vmax)


seuil_cyclogenese = 26.0 

# --- Filtrage STRICT par zone et par VENT (> 26 m/s) ---
final_tracks = {}
total_points_in_zone = 0

for tid, tdata in tracks_raw.items():
    filtered_lon = []
    filtered_lat = []
    filtered_press = []
    filtered_vmax = []
    
    for i in range(len(tdata['lon'])):
        ln, lt, pr, vm = tdata['lon'][i], tdata['lat'][i], tdata['press'][i], tdata['vmax'][i]
        
        # Le point doit être dans la zone ET au-dessus de 26 m/s
        if (ATLANTIC_LON_MIN <= ln <= ATLANTIC_LON_MAX) and (ATLANTIC_LAT_MIN <= lt <= ATLANTIC_LAT_MAX):
            if vm >= seuil_cyclogenese:
                filtered_lon.append(ln)
                filtered_lat.append(lt)
                filtered_press.append(pr)
                filtered_vmax.append(vm)
            
    # Il faut au moins 2 points pour dessiner un segment de trajectoire
    if len(filtered_lon) >= 2:
        final_tracks[tid] = {
            'lon': filtered_lon,
            'lat': filtered_lat,
            'press': filtered_press,
            'vmax': filtered_vmax
        }
        total_points_in_zone += len(filtered_lon)

# --- Statistiques ---
num_trajs = len(final_tracks)
avg_pts = total_points_in_zone / num_trajs if num_trajs > 0 else 0

if not final_tracks:
    print("Aucune donnée ne dépasse 26 m/s dans cette zone avec les seuils actuels.")
    sys.exit()

# --- Création de la carte ---
fig = plt.figure(figsize=(15, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([ATLANTIC_LON_MIN, ATLANTIC_LON_MAX, ATLANTIC_LAT_MIN, ATLANTIC_LAT_MAX], crs=ccrs.PlateCarree()) 

ax.stock_img()
ax.coastlines(resolution='50m', color='black', linewidth=1)

# Coordonnées (Long/Lat)
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.3)
gl.top_labels = False 
gl.right_labels = False
gl.xformatter = LongitudeFormatter()
gl.yformatter = LatitudeFormatter()
gl.xlabel_style = {'size': FONT_SIZE}
gl.ylabel_style = {'size': FONT_SIZE}


bounds = [0, 17, 33, 43, 50, 58, 70, 120]


colors_ss = ['#00bfff', '#00ff00', '#ffff00', '#ffae42', '#ff0000', "#ae00ff", "#000000"]
cmap_ss = mcolors.ListedColormap(colors_ss)
norm_ss = mcolors.BoundaryNorm(bounds, cmap_ss.N)

# Listes pour stocker les coordonnées des points de cyclogénèse (>26 m/s)
genesis_lons = []
genesis_lats = []

# --- Tracé ---
for tid, tdata in final_tracks.items():
    x = np.array(tdata['lon'])
    y = np.array(tdata['lat'])
    v = np.array(tdata['vmax'])

    # On enregistre le premier point valide (index 0) comme point de cyclogenèse
    genesis_lons.append(x[0])
    genesis_lats.append(y[0])

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    lc = LineCollection(segments, cmap=cmap_ss, norm=norm_ss, transform=ccrs.PlateCarree())
    lc.set_array(v[:-1])
    lc.set_linewidth(1.5)
    lc.set_alpha=0.8
    ax.add_collection(lc)

# --- AJOUT DES GROS POINTS DE CYCLOGÉNÈSE ---
ax.scatter(genesis_lons, genesis_lats, color='black', marker='o', s=90, 
           edgecolor='white', linewidth=0.8, zorder=10, label='Cyclogenesis (>= 26 m/s)')

# --- Colorbar ---
sm = plt.cm.ScalarMappable(cmap=cmap_ss, norm=norm_ss)
cb = plt.colorbar(sm, ax=ax, orientation='horizontal', pad=0.1, aspect=20, shrink=0.6)

tick_locs = [(bounds[i] + bounds[i+1]) / 2 for i in range(len(bounds)-1)]
cb.set_ticks(tick_locs)
cb.set_ticklabels(['TD', 'TS', 'C1', 'C2', 'C3', 'C4', 'C5'])
cb.set_label('Catégorie Saffir-Simpson', fontsize=FONT_SIZE)
cb.ax.tick_params(labelsize=FONT_SIZE)

# Titre
#plt.title(f"Trajectoires {annee_debut}-{annee_fin} (Vents >= 26 m/s)\n"
 #         f"Moyenne : {avg_pts:.1f} pts/traj | Source: {data_n}", 
 #         fontsize=FONT_SIZE)

# Sauvegarde
output_name = f"plot_trajs_filtered_26ms_{annee_debut}_{annee_fin}.png"
plt.savefig(output_name, dpi=200, bbox_inches='tight')
print(f"Graphique sauvegardé : {output_name}")
plt.show()