import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import TwoSlopeNorm

# ================= CONFIGURATION =================
YEAR_MIN = 1960
YEAR_MAX = 2000

JJASO = True        
LAT_MIN, LAT_MAX = 0, 30
LON_MIN, LON_MAX = -105, 10
FONT_SIZE = 16

# Chemins des fichiers
file_ref = "/home/puyf/Documents/data/prw/prw_ref_3weeks_monthly_1960-2023.nc"
file_exp = "/home/puyf/Documents/data/prw/prw_norad_3weeks_monthly_1960-2023.nc"

# =================================================

def get_prw_mean(path, is_jjaso, ymin, ymax):
    """Charge les données prw et calcule la moyenne temporelle."""
    # Note: open_mfdataset est utilisé si vous avez plusieurs fichiers, 
    # sinon open_dataset suffit.
    ds = xr.open_mfdataset(path, combine='by_coords')
    
    # Sélection de la période
    ds = ds.sel(time=slice(str(ymin), str(ymax)))
    
    # Sélection de la variable de rayonnement de surface
    data = ds['prw']
    
    if is_jjaso:
        # Juin (6) à Octobre (10) comme défini dans votre script initial
        data = data.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
        
    return data.mean(dim='time').compute()

# --- Calcul des données ---
print(f"Calcul des moyennes prw pour la période {YEAR_MIN}-{YEAR_MAX}...")
mean_ref = get_prw_mean(file_ref, JJASO, YEAR_MIN, YEAR_MAX)
mean_exp = get_prw_mean(file_exp, JJASO, YEAR_MIN, YEAR_MAX)
diff_prw = mean_exp - mean_ref

# --- Préparation de la figure ---
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 18), 
                         subplot_kw={'projection': ccrs.PlateCarree()})

# Paramètres communs pour les cartes absolues (Ref et Exp)
abs_min, abs_max = 0, 70
cmap_abs = 'BuPu'

# Paramètres pour la carte de différence
diff_limit = 5.56
norm_diff = TwoSlopeNorm(vmin=-diff_limit, vcenter=0, vmax=diff_limit)

titles = [f"Reférence - {YEAR_MIN}-{YEAR_MAX}", 
          f"NoRadDust - {YEAR_MIN}-{YEAR_MAX}", 
          "Différence (Norad - Ref)"]

data_to_plot = [mean_ref, mean_exp, diff_prw]

# --- Boucle de traçage ---
for i, ax in enumerate(axes):
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    
    # Habillage
    ax.coastlines(resolution='50m', linewidth=1.2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.6)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.2)
    
    if i < 2:
        # Cartes Ref et Exp
        cf = ax.contourf(mean_ref.lon, mean_ref.lat, data_to_plot[i],
                         levels=np.linspace(abs_min, abs_max, 21),
                         cmap=cmap_abs, extend='both', transform=ccrs.PlateCarree())
        cbar_label = "prw (mm)"
    else:
        # Carte Différence
        cf = ax.contourf(mean_ref.lon, mean_ref.lat, data_to_plot[i],
                         levels=np.linspace(-diff_limit, diff_limit, 21),
                         cmap='RdBu_r', norm=norm_diff, extend='both', transform=ccrs.PlateCarree())
        cbar_label = "Différence prw (mm)"
    
    # Colorbar individuelle pour chaque ligne
    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02, aspect=20, shrink=0.8)
    cbar.set_label(cbar_label, fontsize=FONT_SIZE - 2)
    
    # Grille et titres
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': FONT_SIZE - 4}
    gl.ylabel_style = {'size': FONT_SIZE - 4}
    
    ax.set_title(titles[i], fontsize=FONT_SIZE + 2, fontweight='bold')

suffix = "JJASO" if JJASO else "Annuel"
plt.suptitle(f"Analyse de l'eau précipitable (prw) - {suffix}", 
             fontsize=FONT_SIZE + 8, y=0.98)

#plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()