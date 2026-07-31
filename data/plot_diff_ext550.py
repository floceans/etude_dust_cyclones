import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import TwoSlopeNorm

# ================= CONFIGURATION =================
YEAR_MIN = 1960
YEAR_MAX = 2000

TARGET_PLEV = 85000
JJASO = True        
LAT_MIN, LAT_MAX = 0, 30
LON_MIN, LON_MAX = -105, 10
FONT_SIZE = 21
V_MIN, V_MAX = -0.00005, 0.00005 

file_ref = "/home/puyf/Documents/data/ext_aladin/ext550dust_ref_3weeks_monthly_1960-2023.nc"
file_exp = "/home/puyf/Documents/data/ext_aladin/ext550dust_norad_3weeks_monthly_1960-2000.nc"
VAR_NAME = 'ext550dust'

# =================================================

def get_ext_mean(path, plev, is_jjaso, ymin, ymax):
    """Charge les données et calcule la moyenne d'extinction sur la période choisie."""
    ds = xr.open_mfdataset(path, combine='by_coords')
    
    ds = ds.sel(time=slice(str(ymin), str(ymax)))
    
    # Sélection de la variable et du niveau
    ext = ds[VAR_NAME].sel(plev=plev, method='nearest')
    
    if is_jjaso:
        # Juin (6) à Octobre (10)
        ext = ext.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
        
    return ext.mean(dim='time').compute()

print(f"Calcul des moyennes d'extinction pour {YEAR_MIN}-{YEAR_MAX}...")
mean_ref = get_ext_mean(file_ref, TARGET_PLEV, JJASO, YEAR_MIN, YEAR_MAX)
mean_exp = get_ext_mean(file_exp, TARGET_PLEV, JJASO, YEAR_MIN, YEAR_MAX)

# Calcul de l'anomalie (Différence)
diff_ext = mean_exp - mean_ref

# ================= PLOT =================
map_proj = ccrs.PlateCarree()

fig = plt.figure(figsize=(18, 10))
ax = plt.axes(projection=map_proj)

ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())

# Normalisation centrée sur 0
# Si tes données n'atteignent pas V_MIN/V_MAX, on ajuste dynamiquement
norm = TwoSlopeNorm(vmin=V_MIN, vcenter=0, vmax=V_MAX)
levels = np.linspace(V_MIN, V_MAX, 21)

# --- Champ rempli ---
# 'RdBu_r' est possible, mais 'BrBG' (Brun-Bleu/Vert) est souvent plus parlant 
# pour les aérosols (Brun = plus d'extinction, Bleu/Vert = moins)
cf = ax.contourf(
    mean_ref.lon, mean_ref.lat, diff_ext,
    levels=levels,
    cmap='RdBu_r', 
    norm=norm,
    transform=ccrs.PlateCarree(),
    extend='both'
)

# --- Isolignes ---
cs = ax.contour(
    mean_ref.lon, mean_ref.lat, diff_ext,
    levels=levels[::1], # Une ligne tous les 4 niveaux pour ne pas surcharger
    colors='black',
    linewidths=0.3,
    transform=ccrs.PlateCarree()
)

# Labels avec format scientifique car les valeurs sont petites
ax.clabel(cs, inline=True, fontsize=FONT_SIZE - 7, fmt="%.1e")

# --- Habillage carte ---
ax.coastlines(resolution='50m', linewidth=1.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.7)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.2)

# --- Grille ---
gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': FONT_SIZE - 5}
gl.ylabel_style = {'size': FONT_SIZE - 5}

# --- Colorbar ---
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40, shrink=0.8)
cbar.set_label(f"Différence d'extinction (550nm) à {TARGET_PLEV/100:.0f} hPa ($m^{{-1}}$)", fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE - 5)
# Optionnel : forcer le format scientifique sur la colorbar
cbar.ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.1e'))

# --- Titre ---
suffix = "JJASO" if JJASO else "Annuel"
plt.title(
    f"Différence d'Extinction (Exp - Ref)\n"
    f"{suffix} {YEAR_MIN}-{YEAR_MAX} | {TARGET_PLEV/100:.0f} hPa",
    fontsize=FONT_SIZE + 4,
    pad=25
)

plt.tight_layout()
plt.show()