import csv
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime
# Import de vos fonctions personnalisées
from func_dust_cy import load_data 


######################
# -- 1 pour fichiers aladin -> se lisent avec x et y
# -- 2 pour fichiers merra et modis -> se lisent avec lat et lon
######################

# --- 1. Paramètres ---
an_min = 2002
an_max = 2020
#conversion_factor = 1.9438
svent = 28
spress = 1005

data_f = 'ibtracs'

# Fichiers
ibtracs = 'ibtracs_transformed_1960_2024.csv'
aladin = 'ALADIN_rel10_1960_2024.csv'

if data_f == 'aladin':
    FILE = aladin  
elif data_f == 'ibtracs':
    FILE = ibtracs
else :
    raise ValueError("Le paramètre 'data' doit être soit 'aladin' soit 'ibtracs'.")

aladin_dust = '/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_mensuel_1960-2024.nc'
aladin_aer = '/home/puyf/Documents/dust_brut_1/aladin/aladin_aer_mensuel_1960-2024.nc'


merra = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'
modis = '/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc'


AOD_FILE_PATH_1 = aladin_dust
AOD_FILE_PATH_2 = merra
VAR_AOD_1 = "od550dust"
VAR_AOD_2 = "DUEXTTAU"

# AOD
aod_masked_1 = load_data(AOD_FILE_PATH_1, VAR_AOD_1, an_min, an_max, True)
aod_masked_2 = load_data(AOD_FILE_PATH_2, VAR_AOD_2, an_min, an_max, True)

# Moyenne spatiale (sur tout l'Atlantique masqué) puis moyenne annuelle
# Pour obtenir une valeur d'AOD par an
aod_annual_series_1 = aod_masked_1.mean(dim=['x', 'y']).groupby('time.year').mean()
aod_annual_series_2 = aod_masked_2.mean(dim=['lat', 'lon']).groupby('time.year').mean()
years_aod_1 = aod_annual_series_1.year.values
years_aod_2 = aod_annual_series_2.year.values

values_aod_1 = aod_annual_series_1.values
values_aod_2 = aod_annual_series_2.values

# ACE 
cyclones = {}
with open(FILE, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date_str = row['date'].strip()
        year_str = date_str[:4]
        year_int = int(year_str)
        
        if an_min <= year_int and year_int <= an_max : #data_f=='aladin and float(row['vmax'])>28 and float(row['pmin'])<1005) or data_f == 'ibtracs':
            tc_id = (year_str, row['numtc'])
            if tc_id not in cyclones:
                cyclones[tc_id] = {'vmax': []}
            try:
                v_kts = float(row['vmax']) #* conversion_factor
                cyclones[tc_id]['vmax'].append(v_kts)
            except (ValueError, TypeError):
                continue

# Calcul de l'ACE par année
annual_ace = {str(y): 0.0 for y in range(an_min, an_max + 1)}
for (year, num), data in cyclones.items():
    ace_val = sum(((v*1.94)**2) / 10000 for v in data['vmax'] if (v > svent and data_f == 'aladin') or data_f == 'ibtracs') ### filtrage ici
    annual_ace[year] += ace_val

sorted_years = sorted(annual_ace.keys())
ace_values = [annual_ace[y] for y in sorted_years]

# plot
fig, ax1 = plt.subplots(figsize=(12, 6))

# plot histogramme ACE
color_ace = 'steelblue'
bars = ax1.bar(sorted_years, ace_values, color=color_ace, alpha=0.6, label=f'ACE {data_f}')
ax1.set_ylim(0,360)
ax1.set_xlabel('Année', fontsize=12)
ax1.set_ylabel('ACE ($10^4 kt^2$)', color=color_ace, fontsize=12)
ax1.tick_params(axis='y', labelcolor=color_ace)
ax1.set_title(f'Relation ACE vs AOD_dust - {data_f} - ({an_min}-{an_max})', fontsize=14)

#plot graph aod
ax2 = ax1.twinx()  # Création du deuxième axe Y
color_aod = 'darkorange'


if data_f == 'aladin':
    ax2.plot([str(y) for y in years_aod_1], values_aod_1, color=color_aod, marker='o', linewidth=2, label=f'AOD dust {data_f}')
elif data_f == 'ibtracs':
    ax2.plot([str(y) for y in years_aod_2], values_aod_2, color=color_aod, marker='s', linewidth=2, label=f'AOD {data_f}') #list(range(an_min, an_max))

ax2.set_ylabel(f'Aerosol Optical Depth (AOD)', color=color_aod, fontsize=12)
ax2.tick_params(axis='y', labelcolor=color_aod)
ax2.set_ylim(0.06,0.13) ########################################################################################################



ax1.grid(axis='y', linestyle='--', alpha=0.3)
fig.tight_layout()

# Fusion des légendes des deux axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.show()