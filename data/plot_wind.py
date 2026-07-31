import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 1. Chemins des fichiers (à adapter selon votre dossier)
file_ua = "/home/puyf/Documents/data/vents_aladin/ref/ua_ref_3weeks_monthly_1960-2023.nc"
file_uv = file_ua.replace("ua_", "va_") # On suppose que le fichier v suit la même nomenclature

# 2. Chargement des données
ds_u = xr.open_dataset(file_ua)
ds_v = xr.open_dataset(file_uv)

# 3. Sélection du niveau de pression et de la première échéance temporelle
# plev est en Pa dans votre fichier (85000 Pa = 850 hPa)
target_plev = 85000

u = ds_u.ua.sel(plev=target_plev, method='nearest').isel(time=0)
v = ds_v.va.sel(plev=target_plev, method='nearest').isel(time=0)

# 4. Calcul du module du vent (vitesse)
ws = np.sqrt(u**2 + v**2)

# 5. Récupération des coordonnées 2D
lons = ds_u.lon.values
lats = ds_u.lat.values

# 6. Configuration de la projection Lambert (extraite de votre ncdump)
# Paramètres : lat_0=9.5, lon_0=-49, std_parallel=9.5
map_proj = ccrs.LambertConformal(central_longitude=-49.0, 
                                 central_latitude=9.5, 
                                 standard_parallels=(9.5,))

# 7. Création de la figure
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=map_proj)

# Ajout des traits de côte et frontières
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)

# 8. Affichage du module du vent (vitesse)
# On utilise transform=ccrs.PlateCarree() car les lat/lon sont en degrés
cf = ax.contourf(lons, lats, ws, levels=np.arange(0, 26, 2), 
                 cmap='turbo', transform=ccrs.PlateCarree(), extend='both')

# Ajout d'une barre de couleur
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05, aspect=50)
cbar.set_label('Vitesse du vent (m/s)')

# 9. Ajout des vecteurs vent (optionnel)
# On affiche un vecteur tous les 20 points pour ne pas surcharger la carte
skip = (slice(None, None, 20), slice(None, None, 20))
ax.quiver(lons[skip], lats[skip], u.values[skip], v.values[skip], 
          transform=ccrs.PlateCarree(), color='black', alpha=0.6, scale=150)

plt.title(f"Carte des vents à {target_plev/100:.0f} hPa\nMoyenne 2000-2010", loc='left')

plt.show()