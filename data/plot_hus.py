import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

###############
# CONFIGURATION
###############
JJASO = True
plev = 85000
AN_MIN = '1960'
AN_MAX = '2000'
# Remplacez par le chemin de votre fichier hus
file_hus = "/cnrm/mosca/USERS/puyf/NO_SAVE/hus/hus_concat_NoRadDust_3weeks_monthly_1960-2023.nc"

def get_hus_mean(path, plev, is_jjaso):
    """Charge le fichier hus, sélectionne le niveau et convertit en g/kg."""
    ds = xr.open_mfdataset(path, combine='by_coords')
    
    # Alignement temporel (1960-2000)
    ds = ds.sel(time=slice(AN_MIN,AN_MAX))
    
    # Sélection de la variable hus et du niveau de pression
    # On multiplie par 1000 pour passer de kg/kg à g/kg
    hus = ds['hus'].sel(plev=plev, method='nearest') * 1000
    
    # Filtrage saisonnier (JAS : Juillet, Août, Septembre)
    if is_jjaso:
        hus = hus.sel(time=ds.time.dt.month.isin([7, 8, 9]))
    
    return hus.mean(dim='time').compute()

# Calcul de la moyenne
hus_mean = get_hus_mean(file_hus, plev, JJASO)

lons, lats = hus_mean.lon.values, hus_mean.lat.values

#######################
# CONFIGURATION DU PLOT
#######################
map_proj = ccrs.PlateCarree()

fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=map_proj)

ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor='none', edgecolor='black')

# Niveaux adaptés à l'humidité spécifique à 850hPa (souvent entre 2 et 18 g/kg)
levels = np.linspace(hus_mean.min(), hus_mean.max(), 21)

# Changement de la colormap : 'YlGnBu' ou 'GnBu' est plus intuitif pour l'humidité
cf = ax.contourf(lons, lats, hus_mean, levels=levels, 
                 cmap='YlGnBu', transform=ccrs.PlateCarree(), extend='both')

# Isolignes
cs = ax.contour(lons, lats, hus_mean, levels=levels[::2], 
                colors='black', linewidths=0.3, alpha=0.5, transform=ccrs.PlateCarree())
plt.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')

# Barre de couleur
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05, aspect=50)
cbar.set_label('Humidité spécifique ($g/kg$)')

plt.title(f"Humidité spécifique moyenne Norad à {plev/100:.0f} hPa (JAS)", loc='left')

plt.show()