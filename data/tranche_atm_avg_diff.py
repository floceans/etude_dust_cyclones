import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm 
from scipy.interpolate import interp1d

# ================= CONFIGURATION =================
JJASO = True  
LON_MIN = -55
LON_MAX = -45
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

# 1. Fonction pour obtenir la moyenne temporelle
def get_seasonal_mean(ds, is_jjaso):
    ds_subset = ds.sel(time=slice('1960', '2000'))
    if is_jjaso:
        # Juillet, Août, Septembre (JAS)
        ua = ds_subset['ua'].sel(time=ds_subset.time.dt.month.isin([7, 8, 9]))
    else:
        ua = ds_subset['ua']
    return ua.where(ua < 1e10).mean(dim='time')

print("Calcul des moyennes temporelles...")
mean_ref_raw = get_seasonal_mean(ds_ref, JJASO)
mean_norad_raw = get_seasonal_mean(ds_norad, JJASO)

# 2. Extraction de la tranche moyennée zonalement (sur la plage de longitude)
print(f"Extraction de la zone {LON_MIN}° à {LON_MAX}°E...")

mask_lon = (ds_ref['lon'] >= LON_MIN) & (ds_ref['lon'] <= LON_MAX)

# On moyenne zonalement (dim 'x') pour les deux datasets
section_ref = mean_ref_raw.where(mask_lon).mean(dim='x').compute()
section_norad = mean_norad_raw.where(mask_lon).mean(dim='x').compute()

# Calcul de la différence sur la section moyennée
diff_section = section_norad - section_ref

# Latitude moyenne sur la bande de longitude (pour la cohérence géométrique)
lat_section = ds_ref['lat'].where(mask_lon).mean(dim='x').compute()
plevs = ds_ref['plev'].values / 100

# 3. Interpolation verticale pour un rendu lisse
plev_fine = np.linspace(plevs.min(), plevs.max(), 100)
diff_interp = np.zeros((len(plev_fine), len(lat_section)))

for i in range(len(lat_section)):
    data_col = diff_section.values[:, i]
    mask_nan = ~np.isnan(data_col)
    if mask_nan.sum() > 1:
        f = interp1d(plevs[mask_nan], data_col[mask_nan], kind='linear', fill_value="extrapolate")
        diff_interp[:, i] = f(plev_fine)
    else:
        diff_interp[:, i] = np.nan

# 4. Plot de la différence
plt.figure(figsize=(16, 10))
ax = plt.gca()

# Ajustement de l'échelle de couleur (symétrique autour de 0)
vlimit = 5
norm = TwoSlopeNorm(vmin=-vlimit, vcenter=0, vmax=vlimit)
levels_cf = np.linspace(-vlimit, vlimit, 21)

cf = plt.contourf(lat_section, plev_fine, diff_interp, levels=levels_cf, 
                  cmap='RdBu_r', extend='both', norm=norm)

# Contours de la différence
cs = plt.contour(lat_section, plev_fine, diff_interp, levels=11, 
                 colors='black', linewidths=0.5, alpha=0.5)
plt.clabel(cs, inline=True, fontsize=10, fmt='%1.1f')

# --- REGLAGE DE L'AXE Y ---
# En mettant (1000, 200), le premier chiffre est le BAS et le second le HAUT.
# On n'a plus besoin de ax.invert_yaxis().
ax.set_ylim(1000, 200) 
# --------------------------

# Décoration
ax.set_xlim(LAT_MIN, LAT_MAX)
plt.xlabel("Latitude (°N)", fontsize=FONT_SIZE)
plt.ylabel("Pression (hPa)", fontsize=FONT_SIZE)
ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE)

cbar = plt.colorbar(cf)
cbar.set_label('$\Delta$ Vent Zonal (m/s)', fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE)

suffix = "(JAS)" if JJASO else "(Annuel)"
plt.title(f"Différence Vent Zonal (NoRadDust - Ref)\nMoyenne {LON_MIN}° à {LON_MAX}°E | {suffix}", 
          fontsize=FONT_SIZE + 2, pad=20)

plt.grid(True, alpha=0.2, linestyle='--')
plt.tight_layout()
plt.show()