import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import TwoSlopeNorm

# ================= CONFIGURATION =================
YEAR_MIN = 1960
YEAR_MAX = 2000

TARGET_PLEV = 92500
JJASO = True        
LAT_MIN, LAT_MAX = 0, 30
LON_MIN, LON_MAX = -105, 10
FONT_SIZE = 21

# Paramètres de la colorbar fixes
V_MIN, V_MAX = -2,2

file_ref = "/cnrm/mosca/USERS/puyf/stage/data/temp/ta_ref_3weeks_monthly_1960-2023.nc"
file_exp = "/cnrm/mosca/USERS/puyf/stage/data/temp/ta_norad_3weeks_monthly_1960-2000.nc"
#/home/puyf/Documents/data/temp_aladin/temp_norad/ta_norad_3weeks_monthly_1960-2000.nc
# =================================================

def get_temp_mean(path, plev, is_jjaso, ymin, ymax):
    """Charge les données et calcule la moyenne sur la période choisie."""
    ds = xr.open_mfdataset(path, combine='by_coords')
    
    # Sélection de la période basée sur la config
    ds = ds.sel(time=slice(str(ymin), str(ymax)))
    
    temp = ds['ta'].sel(plev=plev, method='nearest')
    
    if is_jjaso:
        # Juillet (7), Août (8), Septembre (9)
        temp = temp.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
        
    return temp.mean(dim='time').compute()

print(f"Calcul des moyennes pour la période {YEAR_MIN}-{YEAR_MAX}...")
mean_ref = get_temp_mean(file_ref, TARGET_PLEV, JJASO, YEAR_MIN, YEAR_MAX)
mean_exp = get_temp_mean(file_exp, TARGET_PLEV, JJASO, YEAR_MIN, YEAR_MAX)
diff_temp = mean_exp - mean_ref

#plot 
# Projection
map_proj = ccrs.PlateCarree()

fig = plt.figure(figsize=(18, 10))
ax = plt.axes(projection=map_proj)

# Fenêtre géographique
ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())

# Normalisation centrée sur 0
norm = TwoSlopeNorm(vmin=V_MIN, vcenter=0, vmax=V_MAX)

# Niveaux pour le contourf
levels = np.linspace(V_MIN, V_MAX, 21)

# --- Champ rempli (anomalie) ---
cf = ax.contourf(
    mean_ref.lon, mean_ref.lat, diff_temp,
    levels=levels,
    cmap='RdBu_r',
    norm=norm,
    transform=ccrs.PlateCarree(),
    extend='both'
)

# --- Isolignes (moins nombreuses pour lisibilité) ---
contour_levels = np.linspace(V_MIN, V_MAX, 21)


cs = ax.contour(
    mean_ref.lon, mean_ref.lat, diff_temp,
    levels=contour_levels,
    colors='black',
    linewidths=0.2,
    transform=ccrs.PlateCarree()
)

# Labels sur isolignes
ax.clabel(cs, inline=True, fontsize=FONT_SIZE - 6, fmt="%.1f")


# --- Habillage carte ---
ax.coastlines(resolution='50m', linewidth=1.5)
ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.7)
ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)

# --- Grille ---
gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': FONT_SIZE - 5}
gl.ylabel_style = {'size': FONT_SIZE - 5}

# --- Colorbar ---
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40, shrink=0.8)
cbar.set_label(f'Différence de Température (K) à {TARGET_PLEV/100:.0f} hPa', fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE - 5)

# --- Titre ---
suffix = "JJASO" if JJASO else "Annuel"
plt.title(
    f"Différence de température (NoRadDust - Ref)\n"
    f"{suffix} {YEAR_MIN}-{YEAR_MAX} | {TARGET_PLEV/100:.0f} hPa",
    fontsize=FONT_SIZE + 4,
    pad=25
)

plt.tight_layout()
plt.show()