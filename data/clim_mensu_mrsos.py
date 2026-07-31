import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

##############################################################
YEAR_MIN = 1960
YEAR_MAX = 1960

JJASO = False        

LAT_MIN, LAT_MAX = 10, 30
LON_MIN, LON_MAX = -10, 15

FONT_SIZE = 21

# Chemins des fichiers
file_ref = "/cnrm/mosca/USERS/puyf/NO_SAVE/mrso/mrsos_concat_ref_3weeks_monthly_1960-2000.nc"
file_exp = "/cnrm/mosca/USERS/puyf/NO_SAVE/mrso/mrsos_concat_norad_3weeks_monthly_1960-2000.nc"
############################################################################################

def get_mrsos_climatology(path, name, is_jjaso, ymin, ymax, lat_min, lat_max, lon_min, lon_max):
    ds = xr.open_mfdataset(path, combine='by_coords')
    ds = ds.sel(time=slice(str(ymin), str(ymax)))
    
    mask = (ds['lat'] >= lat_min) & (ds['lat'] <= lat_max) & \
           (ds['lon'] >= lon_min) & (ds['lon'] <= lon_max)
    
    mask = mask.compute()
    
    if not mask.any():
        print(f"\n TABARNAK ERREUR pour {name} : Les coordonnées demandées sont totalement HORS-DOMAINE.")
        print(f"   -> Gamme Lat du fichier : {float(ds.lat.min()):.1f}° à {float(ds.lat.max()):.1f}°")
        print(f"   -> Gamme Lon du fichier : {float(ds.lon.min()):.1f}° à {float(ds.lon.max()):.1f}°")
        return None
        
    # masquage selon lat et lon def
    ds_zone = ds.where(mask, drop=True)
        
    spatial_mean = ds_zone['mrsos'].mean(dim=['y', 'x'])
    
    clim = spatial_mean.groupby('time.month').mean(dim='time')
    
    if is_jjaso:
        clim = clim.sel(month=[6, 7, 8, 9, 10])
        
    return clim.compute()

print("Calcul des climatologies mensuelles...")
clim_ref = get_mrsos_climatology(file_ref, "REFERENCE", JJASO, YEAR_MIN, YEAR_MAX, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)
clim_exp = get_mrsos_climatology(file_exp, "EXPERIENCE", JJASO, YEAR_MIN, YEAR_MAX, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)

if clim_ref is None or clim_exp is None:
    raise ValueError("Le tracé a été arrêté car les coordonnées demandées ne touchent pas le domaine géographique du modèle.")

diff_clim = clim_exp - clim_ref

global_min = min(clim_exp.min().values, clim_ref.min().values)
global_max = max(clim_exp.max().values, clim_ref.max().values)
padding = (global_max - global_min) * 0.10 if global_max != global_min else 1.0
y_limits_shared = (global_min - padding, global_max + padding)

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 14), sharex=True)

titles = [f"NoRadDust - {YEAR_MIN}-{YEAR_MAX}", 
          f"Référence - {YEAR_MIN}-{YEAR_MAX}", 
          "Différence (NoRadDust - Ref)"]

data_to_plot = [clim_exp, clim_ref, diff_clim]
colors = ['crimson', 'navy', 'purple']  
y_labels = ["mrsos (kg m⁻²)", "mrsos (kg m⁻²)", "Différence mrsos (kg m⁻²)"]

month_names = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin', 
               7: 'Juil', 8: 'Août', 9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Déc'}

months_axis = data_to_plot[0].month.values
x_labels = [month_names[m] for m in months_axis]

# --- Boucle de traçage ---
for i, ax in enumerate(axes):
    ax.plot(months_axis, data_to_plot[i], marker='o', linewidth=2.5, color=colors[i], markersize=8)
    
    ax.set_title(titles[i], fontsize=FONT_SIZE + 2, fontweight='bold')
    ax.set_ylabel(y_labels[i], fontsize=FONT_SIZE)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.tick_params(labelsize=FONT_SIZE - 2)
    
    if i < 2:
        ax.set_ylim(y_limits_shared)
    
    if i == 2:
        ax.axhline(0, color='black', linestyle='-', linewidth=1, alpha=0.7)

axes[-1].set_xticks(months_axis)
axes[-1].set_xticklabels(x_labels, fontsize=FONT_SIZE)
axes[-1].set_xlabel("Mois", fontsize=FONT_SIZE + 2)

suffix = "JJASO" if JJASO else "Annuel"
plt.suptitle(f"mrsos clim mensu, Zone : {LAT_MIN}°N à {LAT_MAX}°N | {LON_MIN}°E à {LON_MAX}°E", 
             fontsize=FONT_SIZE + 2, y=0.98)

plt.tight_layout()
plt.show()