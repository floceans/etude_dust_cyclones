import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# --- Configuration globale de la police ---
plt.rcParams.update({'font.size': 21})

###############
JJASO = True

if len(sys.argv) < 2:
    plev_val = 85000
    print(f'Valeur p par défaut : {plev_val} Pa')
else:
    try:
        plev_val = float(sys.argv[1])
    except ValueError:
        print("Erreur : plev_val doit être un nombre (en Pa).")
        sys.exit(1)

# --- Chemins des fichiers ---
file_ta_norad = "/home/puyf/Documents/data/temp_aladin/temp_norad/ta_norad_3weeks_monthly_1960-2000.nc"
file_hus_norad = "/cnrm/mosca/USERS/puyf/NO_SAVE/hus/hus_concat_NoRadDust_3weeks_monthly_1960-2023.nc"
file_ta_ref = "/home/puyf/Documents/data/temp_aladin/temp_ref/ta_ref_3weeks_monthly_1960-2023.nc"
file_hus_ref = "/cnrm/mosca/USERS/puyf/NO_SAVE/hus/hus_concat_ref_3weeks_monthly_1960-2023.nc"

def T_to_theta_e(temp, hum_s, plev_pa):
    Lv, Cp, P0, R = 2.5e6, 1004.0, 100000.0, 287.05
    k = R / Cp
    r = hum_s / (1 - hum_s)
    #print(r*1000)
    #r *= 1000
    theta = temp * (P0 / plev_pa)**k
    theta_e = theta * np.exp((Lv * r) / (Cp * temp))
    return theta_e

def get_nc_mean(path, plev, is_jjaso, var):
    ds = xr.open_dataset(path)
    ds = ds.sel(time=slice('1960', '2000'))
    data = ds[var].sel(plev=plev, method='nearest')
    if is_jjaso:
        data = data.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
    return data.mean(dim='time').compute()

# --- Calculs ---
print(f"Calcul de la différence de Theta_e à {int(plev_val/100)} hPa...")
ta_norad = get_nc_mean(file_ta_norad, plev_val, JJASO, 'ta')
hus_norad = get_nc_mean(file_hus_norad, plev_val, JJASO, 'hus')
theta_e_norad = T_to_theta_e(ta_norad, hus_norad, plev_val)

ta_ref = get_nc_mean(file_ta_ref, plev_val, JJASO, 'ta')
hus_ref = get_nc_mean(file_hus_ref, plev_val, JJASO, 'hus')
theta_e_ref = T_to_theta_e(ta_ref, hus_ref, plev_val)

diff_theta_e = theta_e_norad - theta_e_ref

# --- Figure ---
fig = plt.figure(figsize=(18, 12))
ax = plt.axes(projection=ccrs.PlateCarree())

# Fenêtre restreinte : [Lon_min, Lon_max, Lat_min, Lat_max]
ax.set_extent([-105, 10, 0, 30], crs=ccrs.PlateCarree())

ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=1)

# --- Grille et Graduations ---
gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.3, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 21}
gl.ylabel_style = {'size': 21}

# --- 1. Fond coloré (contourf) ---
vmin, vmax = -2,2
levels_f = np.linspace(vmin, vmax, 41) 
cf = ax.contourf(diff_theta_e.lon, diff_theta_e.lat, diff_theta_e, 
                 levels=levels_f, cmap='RdBu_r', extend='both', transform=ccrs.PlateCarree())

# --- 2. Isolignes (contour) ---
# On trace des lignes tous les 0.4 K pour la clarté
levels_l = np.arange(-2.4, 2.4, 0.4)
cs = ax.contour(diff_theta_e.lon, diff_theta_e.lat, diff_theta_e, 
                levels=levels_l, colors='black', linewidths=1.0, alpha=0.6, transform=ccrs.PlateCarree())

# Étiquettes sur les lignes
ax.clabel(cs, inline=True, fontsize=16, fmt="%.1f")

# --- Colorbar ---
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.12, aspect=40, shrink=0.9)
cbar.set_label('Différence de $\Theta_e$ (K)', size=21)
cbar.ax.tick_params(labelsize=21)

plt.title(f"Différence $\Theta_e$ (Norad - Ref)\nJJASO (1960-2000) - {int(plev_val/100)} hPa", 
          fontweight='bold', pad=25)

# --- Sauvegarde ---
output_name = f"diff_thetae_couleurs_isolignes_{int(plev_val/100)}hPa.png"
#plt.savefig(output_name, dpi=300, bbox_inches='tight')
print(f"Figure sauvegardée : {output_name}")

plt.show()