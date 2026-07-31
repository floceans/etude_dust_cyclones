import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# --- PARAMÈTRES DE PERSONNALISATION ---
var = 'va850'
LABEL_SIZE = 20
CMAP = 'RdBu_r' 

# --- NOUVEAU : LIMITES SPATIALES ---
lonmin, lonmax, latmin, latmax = -105, 5, 0, 30 #-130, 30, -25, 35
# ---------------------------------------

# Chemins des deux fichiers (Exemple : Expérience vs Référence)
file_ref = f'/cnrm/mosca/USERS/puyf/NO_SAVE/vents_aladin/ref/{var}_ref_dayly_3s_1960-2000_MJJASO_std.nc'
file_exp = f'/cnrm/mosca/USERS/puyf/NO_SAVE/vents_aladin/NoRadDust/{var}_norad_dayly_3s_1960-2000_MJJASO_std.nc'

# 1. Chargement des datasets
ds_ref = xr.open_dataset(file_ref)
ds_exp = xr.open_dataset(file_exp)

# 2. Calcul de la différence (Expérience - Référence)
# On s'assure de sélectionner le premier pas de temps pour les deux
diff = ds_exp[var].isel(time=0) - ds_ref[var].isel(time=0)

lon = ds_ref['lon']
lat = ds_ref['lat']

# 3. Configuration de la projection
map_proj = ccrs.PlateCarree()

# 4. Création de la figure
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1, projection=map_proj)

# --- NOUVEAU : APPLICATION DES LIMITES DE LA CARTE ---
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=map_proj)

# 5. Tracé des données
v_max = 0.5

mesh = ax.pcolormesh(lon, lat, diff, 
                    transform=ccrs.PlateCarree(),
                    cmap=CMAP, 
                    vmin=-v_max, vmax=v_max,
                    shading='auto')

# 6. Éléments cartographiques
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.7)

gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.5)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': LABEL_SIZE}
gl.ylabel_style = {'size': LABEL_SIZE}

# 7. Colorbar et titres
cbar = plt.colorbar(mesh, ax=ax, orientation='vertical', pad=0.05, shrink=0.55)
cbar.set_label(f"diff {var} ({ds_ref[var].units})", size=LABEL_SIZE)
cbar.ax.tick_params(labelsize=LABEL_SIZE)
cbar.set_ticks([-0.5, -0.25, 0, 0.25, 0.5])

plt.title(f"Différence d'écart type du vent méridional ({var}) filtré 2-10j jours\nNoRadDust-ref, MJJASO, 3s", 
          fontsize=LABEL_SIZE + 2)

plt.show()