import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature
import numpy as np

# --- 1. Lecture des données par trajectoire ---
file_path = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/trajectoires_1/fichiers_traj/autres/suiERA5_evaluation_1960-1961.vor5_res17_1_-2_5.rel10' 

# Liste principale qui contiendra les trajectoires. Chaque élément sera un dictionnaire:
# {'lon': [...], 'lat': [...], 'pression': [...]}
trajectories = []
current_trajectory = {'lon': [], 'lat': [], 'pression': []}

try:
    with open(file_path, 'r') as f:
        # On utilise un itérateur pour sauter la première ligne si on est sûr qu'elle est toujours un entête globale
        # Pour être plus robuste, on traite toutes les lignes et on se base sur la détection ci-dessous.
        
        for line in f:
            # Nettoyer la ligne et la diviser par des espaces
            parts = line.strip().split()

            # --- DÉTECTION DU CHANGEMENT DE TRAJECTOIRE ---
            # Une ligne est considérée comme une ligne de données si elle a au moins 6 colonnes et que 
            # ses 6 colonnes peuvent être converties en float (vérifié dans le try/except).
            is_data_line = len(parts) >= 6
            
            if is_data_line:
                try:
                    # Tenter d'extraire et de convertir les données
                    # Longitude : Index 1, Latitude : Index 2, Pression : Index -1
                    lon = float(parts[1])
                    lat = float(parts[2])
                    pressure = float(parts[-1])
                    
                    # Ajouter les points à la trajectoire courante
                    current_trajectory['lon'].append(lon)
                    current_trajectory['lat'].append(lat)
                    current_trajectory['pression'].append(pressure)
                    
                except ValueError:
                    # Si la conversion échoue (probablement une ligne d'entête)
                    is_data_line = False
            
            # Si on détecte une ligne d'entête (non-data)
            if not is_data_line:
                # Si la trajectoire courante n'est pas vide (i.e., on a lu des points)
                if current_trajectory['lon']:
                    # Enregistrer la trajectoire précédente
                    trajectories.append(current_trajectory)
                
                # Réinitialiser pour la nouvelle trajectoire
                current_trajectory = {'lon': [], 'lat': [], 'pression': []}
                
        # --- FIN DE FICHIER ---
        # Ajouter la dernière trajectoire si elle n'est pas vide
        if current_trajectory['lon']:
            trajectories.append(current_trajectory)
                    
except Exception as e:
    print(f"Une erreur s'est produite lors de la lecture ou du traitement : {e}")
    exit()

# Compteur de trajectoires
nombre_trajectoires = len(trajectories)
print(f"✅ {nombre_trajectoires} trajectoire(s) détectée(s) et extraite(s) du fichier.")


if nombre_trajectoires == 0:
    print("Aucune trajectoire valide n'a pu être extraite du fichier.")
    exit()

# --- 2. Préparation pour le tracé ---

# Agréger tous les points pour la Colorbar et l'étendue de la carte
all_lon = np.concatenate([t['lon'] for t in trajectories])
all_lat = np.concatenate([t['lat'] for t in trajectories])
all_pression = np.concatenate([t['pression'] for t in trajectories])

# --- 3. Création du graphique avec Cartopy ---

plt.figure(figsize=(12, 10))
ax = plt.axes(projection=ccrs.PlateCarree()) 

## Ajoutez les éléments de fond de carte
ax.coastlines(resolution='50m', color='black', linewidth=1)
ax.add_feature(cartopy.feature.BORDERS, linestyle=':', alpha=0.5)
ax.add_feature(cartopy.feature.LAND, facecolor='lightgray', edgecolor='none')
ax.add_feature(cartopy.feature.OCEAN, facecolor='lightblue')
ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='-')

# Définir l'étendue de la carte
lon_min, lon_max = all_lon.min() - 5, all_lon.max() + 5
lat_min, lat_max = all_lat.min() - 5, all_lat.max() + 5
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

# --- TRACÉ DES LIGNES ET DES POINTS ---

# Tracer tous les points pour la Colorbar (nécessite un objet scatter global)
# Créer un scatter "proxy" invisible pour définir l'échelle de la Colorbar
scatter_proxy = ax.scatter(
    all_lon, 
    all_lat, 
    c=all_pression, 
    cmap='viridis', 
    s=1, 
    alpha=0.0, # Rendre les points transparents
    transform=ccrs.PlateCarree()
)

# Normalisation globale pour que les couleurs soient cohérentes sur toutes les trajectoires
norm = plt.Normalize(vmin=all_pression.min(), vmax=all_pression.max())

# Un drapeau pour s'assurer que l'étiquette de la ligne n'apparaît qu'une fois dans la légende
line_label_added = False

for trajectory in trajectories:
    lon_t = trajectory['lon']
    lat_t = trajectory['lat']
    pression_t = trajectory['pression']

    # 1. Tracer la ligne pour relier les points (en gris)
    ax.plot(
        lon_t, 
        lat_t, 
        color='gray', 
        linewidth=0.8,
        linestyle='-',
        alpha=0.6,
        transform=ccrs.PlateCarree(),
        label='Trajectoire de connexion' if not line_label_added else "" # Ajout de l'étiquette
    )
    line_label_added = True
    
    # 2. Retracer les points pour la couleur basée sur la pression
    ax.scatter(
        lon_t, 
        lat_t, 
        c=pression_t, # Couleur selon la pression
        cmap='viridis',
        norm=norm, # Utiliser la normalisation globale
        s=40, # Taille des points individuels
        marker='o',
        edgecolors='black', 
        linewidths=0.5,
        transform=ccrs.PlateCarree()
    )


# Ajouter la barre de couleur
cbar = plt.colorbar(scatter_proxy, orientation='vertical', pad=0.02, aspect=50)
cbar.set_label('Pression (unité)')

# Titre du graphique mis à jour avec le compteur
plt.title(f'Visualisation des données géospatiales: {nombre_trajectoires} Trajectoire(s) tracée(s)')

# Afficher la légende (pour la ligne de connexion)
if nombre_trajectoires > 0:
    # Récupérer les handles et labels existants
    handles, labels = ax.get_legend_handles_labels()
    # Afficher la légende
    if handles:
        # On utilise handles[0] et labels[0] pour n'afficher que la ligne de connexion
        ax.legend([handles[0]], [labels[0]], loc='lower left')

plt.show()