import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ================= CONFIGURATION =================
YEAR_MIN = 1960
YEAR_MAX = 2000

JJASO = False # Passé à False pour avoir une ligne continue sans "trous" pendant l'hiver      

LAT_MIN, LAT_MAX = 10, 30
LON_MIN, LON_MAX = -10, 15

FONT_SIZE = 21

# Chemins des fichiers
file_ref = "/cnrm/mosca/USERS/puyf/stage/data/mrso/mrso_concat_ref_3weeks_monthly_1960-2000.nc"
file_exp = "/cnrm/mosca/USERS/puyf/stage/data/mrso/mrso_concat_norad_3weeks_monthly_1960-2000.nc"
# =================================================

def get_mrso_timeseries(path, name, is_jjaso, ymin, ymax, lat_min, lat_max, lon_min, lon_max):

    ds = xr.open_mfdataset(path, combine='by_coords')
    ds = ds.sel(time=slice(str(ymin), str(ymax)))
    
    mask = (ds['lat'] >= lat_min) & (ds['lat'] <= lat_max) & \
           (ds['lon'] >= lon_min) & (ds['lon'] <= lon_max)
    
    mask = mask.compute()
    
    if not mask.any():
        print(f"\nERREUR pour {name} : Les coordonnées demandées sont totalement HORS-DOMAINE.")
        return None
        
    ds_zone = ds.where(mask, drop=True)
        
    ts = ds_zone['mrso'].mean(dim=['y', 'x'])
    
    
    if is_jjaso:
        ts = ts.sel(time=ts['time.month'].isin([6, 7, 8, 9, 10]))
        
    return ts.compute()


print("Calcul des séries temporelles (cela peut prendre un instant)...")
ts_ref = get_mrso_timeseries(file_ref, "REFERENCE", JJASO, YEAR_MIN, YEAR_MAX, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)
ts_exp = get_mrso_timeseries(file_exp, "EXPERIENCE", JJASO, YEAR_MIN, YEAR_MAX, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)

if ts_ref is None or ts_exp is None:
    raise ValueError("Le tracé a été arrêté car les coordonnées sont hors domaine.")

diff_ts = ts_exp - ts_ref


global_min = min(ts_exp.min().values, ts_ref.min().values)
global_max = max(ts_exp.max().values, ts_ref.max().values)
padding = (global_max - global_min) * 0.10 if global_max != global_min else 1.0
y_limits_shared = (global_min - padding, global_max + padding)


fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(14, 12), sharex=True)

titles = [f"Série Temporelle : NoRadDust", 
          f"Série Temporelle : Référence", 
          "Différence (NoRadDust - Ref)"]

data_to_plot = [ts_exp, ts_ref, diff_ts]
colors = ['crimson', 'navy', 'purple']  
y_labels = ["mrso (kg m⁻²)", "mrso (kg m⁻²)", "Différence mrso (kg m⁻²)"]


time_axis = data_to_plot[0].time.values


for i, ax in enumerate(axes):

    ax.plot(time_axis, data_to_plot[i], linewidth=1.5, color=colors[i], alpha=0.9)
    
    ax.set_title(titles[i], fontsize=FONT_SIZE + 2, fontweight='bold')
    ax.set_ylabel(y_labels[i], fontsize=FONT_SIZE)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.tick_params(labelsize=FONT_SIZE - 2)
    
    
    if i < 2:
        ax.set_ylim(y_limits_shared)
    
   
    if i == 2:
        ax.axhline(0, color='black', linestyle='-', linewidth=1.5, alpha=0.8)


axes[-1].set_xlabel("Années", fontsize=FONT_SIZE + 2)


locator = mdates.YearLocator(base=5) 
formatter = mdates.DateFormatter('%Y')
axes[-1].xaxis.set_major_locator(locator)
axes[-1].xaxis.set_major_formatter(formatter)

suffix = "Mois JJASO uniquement" if JJASO else "Tous les mois"
plt.suptitle(f"Séries temporelles mensuelles de l'humidité du sol (mrso) - {YEAR_MIN} à {YEAR_MAX}\nZone : {LAT_MIN}°N à {LAT_MAX}°N | {LON_MIN}°E à {LON_MAX}°E ({suffix})", 
             fontsize=FONT_SIZE + 4, y=0.97)

plt.tight_layout()
plt.show()