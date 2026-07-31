import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

###############
JJASO = True
plev_val = 100000
file_ta = "/cnrm/mosca/USERS/puyf/stage/data/temp/ta_ref_3weeks_monthly_1960-2023.nc"
file_hus = "/cnrm/mosca/USERS/puyf/stage/data/hus/hus_concat_NoRadDust_3weeks_monthly_1960-2023.nc"



def T_to_theta_e(temp, hum_s, plev_pa):
    Lv = 2.5e6  
    Cp = 1004.0 
    P0 = 100000.0 
    R = 287.05
    k = R / Cp 

    r = hum_s / (1 - hum_s)
    theta = temp * (P0 / plev_pa)**k
    # Utilisation de np.exp pour gérer les tableaux xarray/numpy
    theta_e = theta * np.exp((Lv * r) / (Cp * temp))
    return theta_e

def get_nc_mean(path, plev, is_jjaso, var):
    ds = xr.open_dataset(path)
    # Sélection temporelle
    ds = ds.sel(time=slice('1960', '2000'))
    
    # Sélection du niveau
    data = ds[var].sel(plev=plev, method='nearest')
    
    if is_jjaso:
        data = data.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
    
    return data.mean(dim='time').compute()

# --- Chargement et calcul ---
temp_k = get_nc_mean(file_ta, plev_val, JJASO, 'ta')
hus = get_nc_mean(file_hus, plev_val, JJASO, 'hus')

theta_e = T_to_theta_e(temp_k, hus, plev_val)

# VERIFICATION : Si tout est NaN, on s'arrête ici
if np.isnan(theta_e).all():
    raise ValueError("Erreur : La variable theta_e ne contient que des NaN. Vérifiez l'extraction des données.")

lons = theta_e.lon
lats = theta_e.lat

# --- Configuration de la figure ---
map_proj = ccrs.LambertConformal(central_longitude=-49.0, 
                                 central_latitude=9.5, 
                                 standard_parallels=(9.5,))

fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=map_proj)

# Optionnel mais recommandé : limiter la vue à la zone de tes données
# ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)

# CORRECTION ICI : np.nanpercentile au lieu de np.percentile
vmin = np.nanpercentile(theta_e, 2)
vmax = np.nanpercentile(theta_e, 98)

# Si vmin ou vmax sont NaN, on définit des limites par défaut pour éviter le crash
if np.isnan(vmin) or np.isnan(vmax):
    vmin, vmax = 300, 360

levels = np.linspace(vmin, vmax, 21)

cf = ax.contourf(lons, lats, theta_e, levels=levels, 
                 cmap='RdYlBu_r', transform=ccrs.PlateCarree(), extend='both')

cs = ax.contour(lons, lats, theta_e, levels=levels[::2], 
                colors='black', linewidths=0.3, alpha=0.5, transform=ccrs.PlateCarree())

plt.clabel(cs, inline=True, fontsize=8, fmt='%1.0f')

cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05, aspect=50)
cbar.set_label('Température Potentielle Équivalente (K)')

plt.title(f"$\Theta_e$ Moyenne - Saison JJASO (1960-2000)\nNiveau {plev_val/100:.0f} hPa", loc='left')

plt.show()