import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# --- PARAMÈTRES DE PERSONNALISATION ---
donnee = 'ref'
var = 'prw'
LABEL_SIZE = 21  # Taille globale des labels (titre, colorbar, axes)
CMAP = 'turbo'   # Nouvelle colormap demandée
# ---------------------------------------

# 1. Chargement du fichier
filename = f'/cnrm/mosca/USERS/puyf/NO_SAVE/prw/ref/{var}_{donnee}_dayly_3s_1960-2023_MJJASO_std.nc'
ds = xr.open_dataset(filename)

# 2. Extraction de la variable et sélection du temps
data = ds[var].isel(time=0)
lat = ds['lat']
lon = ds['lon']

# 3. Configuration de la projection "plane classique" (PlateCarree)
map_proj = ccrs.PlateCarree()

# 4. Création de la figure
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=map_proj)

# 5. Tracé des données
# On garde transform=ccrs.PlateCarree() car les données sont en coordonnées lat/lon
v_max = 15
mesh = ax.pcolormesh(lon, lat, data, 
                    transform=ccrs.PlateCarree(),
                    cmap=CMAP,
                    vmin=0, vmax=v_max, 
                    shading='auto')

# 6. Ajout des éléments cartographiques
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.7)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)

# Graticules (lignes de latitude/longitude)
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.5)
gl.top_labels = False
gl.right_labels = False
# Application de la taille des labels aux axes
gl.xlabel_style = {'size': LABEL_SIZE}
gl.ylabel_style = {'size': LABEL_SIZE}

# 7. Colorbar et titres
cbar = plt.colorbar(mesh, ax=ax, orientation='vertical', pad=0.05, shrink=0.6)
cbar.set_label(f"{ds[var].long_name} ({ds[var].units})", size=LABEL_SIZE)
cbar.ax.tick_params(labelsize=LABEL_SIZE) # Taille des chiffres de la colorbar


plt.title(f"Écart type de l'eau précipitable ({var}) filtré 2-10j jours\nSimulation {donnee}, MJJASO, 3s", 
          fontsize=LABEL_SIZE + 2)

plt.show()