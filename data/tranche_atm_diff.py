import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm 
from scipy.interpolate import interp1d

# ================= CONFIGURATION =================
JJASO = True  
TARGET_LON = -10
FONT_SIZE = 20
LAT_MIN = 0
LAT_MAX = 30
# =================================================

dossier_ref = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/ref/"
dossier_norad = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/NoRadDust"

file_list_ref = [dossier_ref + 'ua_ref_3weeks_monthly_1960-2000.nc']
file_list_norad = [dossier_norad + 'ua_NoRadDust_3weeks_monthly_1960-2000.nc']

print("Chargement des données...")
ds_ref = xr.open_mfdataset(file_list_ref, combine='by_coords', chunks={'time': 12})
ds_norad = xr.open_mfdataset(file_list_norad, combine='by_coords', chunks={'time': 12})

# 1. Alignement temporel (1960-2000) et filtrage saisonnier
def get_seasonal_mean(ds, is_jjaso):
    # On restreint à la période commune pour comparer ce qui est comparable
    ds_subset = ds.sel(time=slice('1960', '2000'))
    if is_jjaso:
        ua = ds_subset['ua'].sel(time=ds_subset.time.dt.month.isin([7, 8, 9]))
    else:
        ua = ds_subset['ua']
    return ua.where(ua < 1e10).mean(dim='time').compute()

print("Calcul des moyennes...")
mean_ref = get_seasonal_mean(ds_ref, JJASO)
mean_norad = get_seasonal_mean(ds_norad, JJASO)

# 2. Calcul de la DIFFÉRENCE (NoRadDust - Ref)
diff_mean = mean_norad - mean_ref

# Coordonnées
plevs = ds_ref['plev'].values / 100
# Extraction de la coupe à TARGET_LON
idx_x = np.abs(ds_ref['lon'] - TARGET_LON).argmin(dim='x').values
idx_y = np.arange(len(ds_ref.y))
diff_section = diff_mean.values[:, idx_y, idx_x]
lat_section = ds_ref['lat'].values[idx_y, idx_x]

# 3. Interpolation verticale
plev_fine = np.linspace(plevs.min(), plevs.max(), 100)
diff_interp = np.zeros((len(plev_fine), len(lat_section)))

for i in range(len(lat_section)):
    data_col = diff_section[:, i]
    mask = ~np.isnan(data_col)
    if mask.sum() > 1:
        f = interp1d(plevs[mask], data_col[mask], kind='linear', fill_value="extrapolate")
        diff_interp[:, i] = f(plev_fine)
    else:
        diff_interp[:, i] = np.nan


# 4. Plot de la différence avec contours
plt.figure(figsize=(16, 10))
ax = plt.gca()

# Configuration de l'échelle de couleur (centrée sur 0)
abs_max = np.nanmax(np.abs(diff_interp))
# On arrondit à l'entier supérieur pour une colorbar propre
vlimit = np.ceil(abs_max)
vmin, vmax = -vlimit, vlimit

norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
levels_cf = np.linspace(vmin, vmax, 21)

# Remplissage de couleur
cf = plt.contourf(lat_section, plev_fine, diff_interp, levels=levels_cf, 
                  cmap='RdBu_r', extend='both', norm=norm)

# --- AJOUT DES CONTOURS (ISO-VENTS) ---
# On définit des intervalles de contours (ex: tous les 0.5 m/s ou 1 m/s selon vos données)
# Ici, on génère auto des niveaux raisonnables
step = 0.5 if vlimit < 5 else 1.0
levels_iso = np.arange(np.floor(vmin), np.ceil(vmax) + step, step)

# Tracé des lignes de contours
cs = plt.contour(lat_section, plev_fine, diff_interp, levels=levels_iso, 
                 colors='black', linewidths=0.5, alpha=0.7)

# Ajout des étiquettes sur les contours
plt.clabel(cs, inline=True, fontsize=10, fmt='%1.1f')

# Ligne de zéro renforcée
plt.contour(lat_section, plev_fine, diff_interp, levels=[0], 
            colors='black', linewidths=2.5)
# --------------------------------------

# Décoration
ax.set_xlim(LAT_MIN, LAT_MAX) 
plt.xlabel("Latitude (°N)", fontsize=FONT_SIZE)
plt.ylabel("Pression (hPa)", fontsize=FONT_SIZE)
ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE)

cbar = plt.colorbar(cf)
cbar.set_label('Différence Vent Zonal (m/s)', fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE)

suffix = "(JAS)" if JJASO else "(Annuel)"
plt.title(f"Différence de Vent Zonal (NoRadDust - Ref) à {TARGET_LON}°E\n{suffix} 1960-2000", 
          fontsize=FONT_SIZE + 2, pad=20)

ax.invert_yaxis()
plt.grid(True, alpha=0.3, linestyle='--')
plt.show()