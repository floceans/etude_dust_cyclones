import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER


JJASO = True
plev = 300
plev*=100
FS = 21  # Taille de la police globale

# Chemins des fichiers
file_ref = "/cnrm/mosca/USERS/puyf/NO_SAVE/hus/hus_concat_ref_3weeks_monthly_1960-2023.nc"
file_norad = "/cnrm/mosca/USERS/puyf/NO_SAVE/hus/hus_concat_NoRadDust_3weeks_monthly_1960-2023.nc"



def get_hus_mean(path, plev, is_jjaso):
    ds = xr.open_mfdataset(path, combine='by_coords')
    ds = ds.sel(time=slice('1960', '2000'))
    hus = ds['hus'].sel(plev=plev, method='nearest') * 1000
    if is_jjaso:
        hus = hus.sel(time=ds.time.dt.month.isin([7, 8, 9]))
    return hus.mean(dim='time').compute()

# Calcul des données
hus_ref = get_hus_mean(file_ref, plev, JJASO)
hus_norad = get_hus_mean(file_norad, plev, JJASO)
diff = hus_norad - hus_ref

lons, lats = diff.lon.values, diff.lat.values

#######################
# CONFIGURATION DU PLOT
#######################
plt.rcParams.update({'font.size': FS})

# Projection Lambert
map_proj = ccrs.PlateCarree()

fig = plt.figure(figsize=(18, 12))
ax = plt.axes(projection=map_proj)

# --- DÉFINITION DE L'EXTENT (Zoom) ---
# [Lon_min, Lon_max, Lat_min, Lat_max]
ax.set_extent([-105, 10, 0, 30], crs=ccrs.PlateCarree())

# Habillage
ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)
ax.add_feature(cfeature.LAND, facecolor='none', edgecolor='black', alpha=0.3)

# --- AJOUT DES AXES (Gridlines) ---
gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False   # Désactiver les labels en haut
gl.right_labels = False # Désactiver les labels à droite
gl.xlabel_style = {'size': FS-4}
gl.ylabel_style = {'size': FS-4}
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

# Niveaux et Plot
vmax = 2.5#np.abs(diff).max()
levels = np.linspace(-vmax, vmax, 21)

cf = ax.contourf(lons, lats, diff, levels=levels, 
                 cmap='BrBG', transform=ccrs.PlateCarree(), extend='both')

# Isolignes
cs = ax.contour(lons, lats, diff, levels=levels[::2], 
                colors='black', linewidths=0.8, alpha=0.6, transform=ccrs.PlateCarree())
plt.clabel(cs, inline=True, fontsize=FS-8, fmt='%1.2f')

# Barre de couleur
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.08, aspect=40)
cbar.set_label('$\Delta$ Humidité spécifique ($g/kg$)', fontsize=FS)

plt.title(f"Différence hus (NoRadDust - ref) à {plev/100:.0f} hPa", 
          fontsize=FS, pad=25)

plt.show()