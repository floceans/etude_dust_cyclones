import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm 
from scipy.interpolate import interp1d

# ================= CONFIGURATION =================
source = 'norad' 
JJASO = True  
# Remplacé TARGET_LON par une plage
LON_MIN = -55
LON_MAX = -45
FONT_SIZE = 30
LAT_MIN = 0
LAT_MAX = 30
# =================================================

dossier_ref = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/ref/"
dossier_norad = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/NoRadDust"

file_list_ref = [dossier_ref + 'ua_ref_3weeks_monthly_1960-2000.nc']
file_list_norad = [dossier_norad + 'ua_NoRadDust_3weeks_monthly_1960-2000.nc']

if source == 'ref' : 
    file_list = file_list_ref 
else :
    file_list = file_list_norad

print("Chargement des données...")
ds = xr.open_mfdataset(file_list, combine='by_coords', chunks={'time': 12})

# 2. Filtrage Saisonnier
if JJASO:
    # On sélectionne Juillet, Août, Septembre (JAS) comme dans votre code initial
    ua_to_process = ds['ua'].sel(time=ds.time.dt.month.isin([7, 8, 9]))
    suffix = "(Saison JAS)"
else:
    ua_to_process = ds['ua']
    suffix = "(Moyenne Annuelle)"

print(f"Calcul de la moyenne temporelle {suffix}...")
ua_time_mean = ua_to_process.where(ua_to_process < 1e10).mean(dim='time')

# 3. Extraction de la tranche (Moyenne sur les Longitudes)
print(f"Calcul de la moyenne zonale entre {LON_MIN}°E et {LON_MAX}°E...")

# On crée un masque pour les longitudes souhaitées
# Note : on utilise .compute() ici pour faciliter l'interpolation après
mask_lon = (ds['lon'] >= LON_MIN) & (ds['lon'] <= LON_MAX)

# On applique le masque et on moyenne sur la dimension 'x' (longitude)
ua_section_ds = ua_time_mean.where(mask_lon).mean(dim='x').compute()

# Pour l'axe X du plot, on moyenne aussi la latitude sur la même zone 
# (important si la grille est curviligne)
lat_section = ds['lat'].where(mask_lon).mean(dim='x').compute()
plevs = ds['plev'].values / 100

# 4. Interpolation verticale (pour un rendu plus lisse)
plev_fine = np.linspace(plevs.min(), plevs.max(), 100)
ua_interp = np.zeros((len(plev_fine), len(lat_section)))

for i in range(len(lat_section)):
    data_col = ua_section_ds.values[:, i]
    mask_nan = ~np.isnan(data_col)
    if mask_nan.sum() > 1:
        f = interp1d(plevs[mask_nan], data_col[mask_nan], kind='linear', fill_value="extrapolate")
        ua_interp[:, i] = f(plev_fine)
    else:
        ua_interp[:, i] = np.nan

# 5. Plot
plt.figure(figsize=(16, 10))
ax = plt.gca()

vmin, vcenter, vmax = -20, 0, 20
norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
norm_levels = np.linspace(vmin, vmax, 21) 

cf = plt.contourf(lat_section, plev_fine, ua_interp, levels=norm_levels, 
                  cmap='RdBu_r', extend='both', norm=norm)

# Contours
cs = plt.contour(lat_section, plev_fine, ua_interp, levels=np.arange(-20, 20, 2), 
                 colors='black', linewidths=0.8, alpha=0.5)
plt.clabel(cs, inline=True, fontsize=11, fmt='%1.0f')

# Mise en forme
ax.set_xlim(LAT_MIN, LAT_MAX) 
ax.set_ylim(1000, 200) # Force les limites de pression (Surface -> Haute atmosphère)
plt.xlabel("Latitude (°N)", fontsize=FONT_SIZE)
plt.ylabel("Pression (hPa)", fontsize=FONT_SIZE)
ax.tick_params(axis='both', which='major', labelsize=FONT_SIZE)

cbar = plt.colorbar(cf)
cbar.set_label('Vent Zonal Moyen (m/s)', fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE)
cbar.set_ticks([-20, -10, 0, 10, 20])

plt.title(f"Coupe Vent Zonal {source} (Moyenne {LON_MIN}° à {LON_MAX}°E)\n{suffix}", 
          fontsize=FONT_SIZE + 2, pad=20)

plt.grid(True, alpha=0.2, linestyle='--')
plt.tight_layout()
plt.show()