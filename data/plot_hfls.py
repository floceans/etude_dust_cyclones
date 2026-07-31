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
FONT_SIZE = 21

# Chemins des fichiers
file_ref = "/cnrm/mosca/USERS/puyf/stage/data/hf/hfls_concat_ref_3weeks_monthly_1960-2000.nc"
file_exp = "/cnrm/mosca/USERS/puyf/stage/data/hf/hfls_concat_norad_3weeks_monthly_1960-2000.nc"

# =================================================

def get_rsds_mean(path, is_jjaso, ymin, ymax):
    ds = xr.open_mfdataset(path, combine='by_coords')
    ds = ds.sel(time=slice(str(ymin), str(ymax)))
    data = ds['hfls']
    if is_jjaso:
        data = data.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
    return data.mean(dim='time').compute()

# --- Calcul des données ---
print(f"Calcul des moyennes HFLS pour la période {YEAR_MIN}-{YEAR_MAX}...")
mean_ref = get_rsds_mean(file_ref, JJASO, YEAR_MIN, YEAR_MAX)
mean_exp = get_rsds_mean(file_exp, JJASO, YEAR_MIN, YEAR_MAX)
diff_rsds = mean_exp - mean_ref

# --- Préparation de la figure ---
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 18), 
                         subplot_kw={'projection': ccrs.PlateCarree()})

# Paramètres pour les cartes absolues
abs_min, abs_max = 0, 220
levels_abs = np.linspace(abs_min, abs_max, 23)
iso_levels_abs = np.arange(abs_min, abs_max + 1, 20) # Une ligne tous les 20 W/m²

# Paramètres pour la carte de différence
diff_limit = 20
levels_diff = np.linspace(-diff_limit, diff_limit, 21)
iso_levels_diff = np.arange(-diff_limit, diff_limit + 1, 2) # Une ligne tous les 2 W/m²

titles = [f"NoRadDust - {YEAR_MIN}-{YEAR_MAX}", 
          f"Reférence - {YEAR_MIN}-{YEAR_MAX}", 
          "Différence (NoRadDust - Ref)"]

data_to_plot = [mean_exp, mean_ref, diff_rsds] # Inversion pour coller aux titres

# --- Boucle de traçage ---
for i, ax in enumerate(axes):
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    
    # Habillage
    ax.coastlines(resolution='50m', linewidth=1.2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.6)
    
    if i < 2:
        # --- Cartes Absolues ---
        # Remplissage
        cf = ax.contourf(mean_ref.lon, mean_ref.lat, data_to_plot[i],
                         levels=levels_abs, cmap='YlOrRd', extend='both', transform=ccrs.PlateCarree())
        # Isolines
        cs = ax.contour(mean_ref.lon, mean_ref.lat, data_to_plot[i],
                        levels=iso_levels_abs, colors='black', linewidths=0.8, 
                        alpha=0.7, transform=ccrs.PlateCarree())
        cbar_label = ""#"hfls (W/m²)"
    else:
        # --- Carte Différence ---
        norm_diff = TwoSlopeNorm(vmin=-diff_limit, vcenter=0, vmax=diff_limit)
        cf = ax.contourf(mean_ref.lon, mean_ref.lat, data_to_plot[i],
                         levels=levels_diff, cmap='RdBu_r', norm=norm_diff, extend='both', transform=ccrs.PlateCarree())
        # Isolines
        cs = ax.contour(mean_ref.lon, mean_ref.lat, data_to_plot[i],
                        levels=iso_levels_diff, colors='black', linewidths=0.5, 
                        alpha=0.5, transform=ccrs.PlateCarree())
        cbar_label = "Différence hfls (W/m²)"
    
    # Ajout des étiquettes sur les isolines
    ax.clabel(cs, inline=True, fontsize=FONT_SIZE - 10, fmt='%d')
    

# Colorbar
    cbar = plt.colorbar(cf, ax=ax, orientation='horizontal', pad=0.15, aspect=18, shrink=0.5)
    cbar.set_label(cbar_label, fontsize=FONT_SIZE - 2)
    cbar.ax.tick_params(labelsize=FONT_SIZE)
    
    # Grille et titres
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': FONT_SIZE - 2}
    gl.ylabel_style = {'size': FONT_SIZE - 2}
    
    #ax.set_title(titles[i], fontsize=FONT_SIZE + 2, fontweight='bold')

suffix = "JJASO" if JJASO else "Annuel"
plt.suptitle(f"Rayonnement montant au sommet de l'atmosphère (RLUT) - {suffix}", 
             fontsize=FONT_SIZE + 8, y=0.98)

plt.show()