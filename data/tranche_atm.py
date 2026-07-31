
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm 
from scipy.interpolate import interp1d
import glob

# ================= CONFIGURATION =================
source = 'NoRadDust' #'ref'
JJASO = True  # True pr Juin to Octobre, False pr toute l'année
TARGET_LON = -10
FONT_SIZE = 25
LAT_MIN = 0
LAT_MAX = 30
# =================================================

dossier_ref = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/ref/"
dossier_norad = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/NoRadDust"

file_list_ref = [dossier_ref + 'ua_ref_3weeks_monthly_1960-2000.nc']
file_list_norad = [dossier_norad + 'ua_NoRadDust_3weeks_monthly_1960-2000.nc']

if source == 'NoRadDust' : 
    print('datas NoRadDust utilisées')
    file_list = file_list_norad
else : 
    print('data ref utilisées')
    file_list = file_list_ref

print("Chargement des données...")
ds = xr.open_mfdataset(file_list, combine='by_coords', chunks={'time': 12})

# 2. Filtrage Saisonnier
# 2. Filtrage Saisonnier et Calcul de la moyenne
if JJASO:
    # On sélectionne les mois de 6 (Juin) à 10 (Octobre)
    ua_to_process = ds['ua'].sel(time=ds.time.dt.month.isin([7, 8, 9]))
    suffix = "(Saison JAS)"
else:
    ua_to_process = ds['ua']
    suffix = "(Moyenne Annuelle)"

print(f"Calcul de la moyenne {suffix}...")

# IMPORTANT : On utilise ua_to_process ici, pas ds['ua']
ua_mean = ua_to_process.where(ua_to_process < 1e10).mean(dim='time').compute()

# Coordonnées
lons, lats, plevs = ds['lon'].values, ds['lat'].values, ds['plev'].values / 100

# 3. Extraction de la coupe
idx_x = np.abs(ds['lon'] - TARGET_LON).argmin(dim='x').values
idx_y = np.arange(len(ds.y))
ua_section = ua_mean.values[:, idx_y, idx_x]
# On récupère les latitudes correspondantes à ces points précis
lat_section = ds['lat'].values[idx_y, idx_x]

# 4. Interpolation verticale
plev_fine = np.linspace(plevs.min(), plevs.max(), 100)
ua_interp = np.zeros((len(plev_fine), len(lat_section)))

for i in range(len(lat_section)):
    data_col = ua_section[:, i]
    mask = ~np.isnan(data_col)
    if mask.sum() > 1:
        f = interp1d(plevs[mask], data_col[mask], kind='linear', fill_value="extrapolate")
        ua_interp[:, i] = f(plev_fine)
    else:
        ua_interp[:, i] = np.nan


# 5. Plot avec labels XXL
plt.figure(figsize=(16, 10))
ax = plt.gca()

# --- NOUVELLE LOGIQUE POUR CENTRER SUR 0 ---
# On définit les bornes (min, centre, max)
vmin, vcenter, vmax = -20, 0, 20
norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
# On crée des niveaux qui passent forcément par 0
norm_levels = np.linspace(vmin, vmax, 21) 

# Utilisation du paramètre 'norm' dans contourf
cf = plt.contourf(lat_section, plev_fine, ua_interp, levels=norm_levels, 
                  cmap='RdBu_r', extend='both', norm=norm)



# Contours classiques
cs = plt.contour(lat_section, plev_fine, ua_interp, levels=np.arange(-20, 20, 2), 
                 colors='black', linewidths=0.8, alpha=0.5)
plt.clabel(cs, inline=True, fontsize=11, fmt='%1.0f')
# --------------------------------------------

ax.set_xlim(LAT_MIN, LAT_MAX) 
plt.xlabel("Latitude (°N)", fontsize=FONT_SIZE)
plt.ylabel("Pression (hPa)", fontsize=FONT_SIZE)
ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE)

cbar = plt.colorbar(cf)
cbar.set_label('Vent Zonal Moyen (m/s)', fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE)

# On peut forcer les ticks de la colorbar pour voir le 0
cbar.set_ticks([-20, -10, 0, 10, 20])

plt.title(f"Coupe moyenne du vent zonal (1960-1999) {source} à {TARGET_LON}°E\n{suffix}", 
          fontsize=FONT_SIZE + 3, pad=20)

ax.invert_yaxis()
plt.grid(True, alpha=0.2, linestyle='--')
plt.show()