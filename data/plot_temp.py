import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


###############
JJASO = True
plev = 85000
file_ta = "/cnrm/mosca/USERS/puyf/stage/data/temp/ta_ref_3weeks_monthly_1960-2023.nc"


def get_temp_mean(path, plev, is_jjaso):
    """Charge le fichier, sélectionne le niveau et calcule la moyenne."""
    # On utilise open_mfdataset pour plus de flexibilité sur la lecture
    ds = xr.open_mfdataset(path, combine='by_coords')
    
    # Alignement temporel sur la période commune (ex: 1960-2000)
    ds = ds.sel(time=slice('1960', '2000'))
    
    # Sélection du niveau de pression
    temp = ds['ta'].sel(plev=plev, method='nearest')
    
    # Filtrage saisonnier (JAS)
    if is_jjaso:
        temp = temp.sel(time=ds.time.dt.month.isin([7, 8, 9])) - 273.15
    
    return temp.mean(dim='time').compute()

temp = get_temp_mean(file_ta, plev, JJASO)

lons, lats = temp.lon.values, temp.lat.values


# 5. Configuration de la projection Lambert
map_proj = ccrs.LambertConformal(central_longitude=-49.0, 
                                 central_latitude=9.5, 
                                 standard_parallels=(9.5,))

# 6. Création de la figure
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=map_proj)

# Habillage géographique
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor='none', edgecolor='black')

# 7. Affichage de la température
# On adapte les levels pour de la température à 850hPa (ex: entre 0 et 30°C)
levels = np.linspace(temp.min(), temp.max(), 21)

cf = ax.contourf(lons, lats, temp, levels=levels, 
                 cmap='RdYlBu_r', transform=ccrs.PlateCarree(), extend='both')

# 8. Ajout des isolignes de température (optionnel)
cs = ax.contour(lons, lats, temp, levels=levels[::2], 
                colors='black', linewidths=0.3, alpha=0.5, transform=ccrs.PlateCarree())
plt.clabel(cs, inline=True, fontsize=8, fmt='%1.0f')

# 9. Barre de couleur
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05, aspect=50)
cbar.set_label('Température ($^\circ$C)')

plt.title(f"Carte de la température à {plev/100:.0f} hPa", loc='left')

plt.show()