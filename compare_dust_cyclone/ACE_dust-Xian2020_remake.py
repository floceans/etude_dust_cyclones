import csv
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from func_dust_cy import load_data 

# objectif ici : refaire données du papier de Xian 2020

# --- 0. Configuration du filtrage ---
FILTER_ZONE = True  # Mettre à True pour filtrer sur -80E/-20E et 10N/20N
lat_min, lat_max = 10, 20
lon_min, lon_max = -60, -20

# --- 1. Paramètres ---
an_min = 1960
an_max = 2020
svent = 26  # Seuil de vent en m/s
data_f = 'aladin' ## atention pr ibtracs mettre seuil vent à 0 !!! 
JJASO_AOD = True
JJASO = True

# Fichiers
ibtracs = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ibtracs_transformed_1960_2024.csv'
aladin = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
aladin_NoRadDust = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv'
FILE = aladin if data_f == 'aladin' else ibtracs
FILE = aladin_NoRadDust if data_f == 'aladin_norad' else FILE

aladin_dust = '/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_mensuel_1960-2024.nc'
merra = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'

AOD_FILE_PATH_1 = aladin_dust
AOD_FILE_PATH_2 = merra
VAR_AOD_1 = "od550dust"
VAR_AOD_2 = "DUEXTTAU"

# --- 2. Chargement et filtrage spatial AOD ---
aod_masked_1 = load_data(AOD_FILE_PATH_1, VAR_AOD_1, an_min, an_max, JJASO_AOD)
aod_masked_2 = load_data(AOD_FILE_PATH_2, VAR_AOD_2, an_min, an_max, JJASO_AOD)

if FILTER_ZONE:
    # Pour Aladin
    aod_masked_1 = aod_masked_1.where(
        (aod_masked_1.lat >= lat_min) & (aod_masked_1.lat <= lat_max) & 
        (aod_masked_1.lon >= lon_min) & (aod_masked_1.lon <= lon_max), 
        drop=True
    )
    # Pour Merra
    aod_masked_2 = aod_masked_2.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

# Moyennes annuelles
aod_annual_series_1 = aod_masked_1.mean(dim=['x', 'y']).groupby('time.year').mean()
aod_annual_series_2 = aod_masked_2.mean(dim=['lat', 'lon']).groupby('time.year').mean()

years_aod = aod_annual_series_1.year.values if data_f == 'aladin' else aod_annual_series_2.year.values
values_aod = aod_annual_series_1.values if data_f == 'aladin' else aod_annual_series_2.values

# --- 3. ACE avec filtrage vent, zone et MOIS (JJASO) ---
cyclones = {}
with open(FILE, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            date_str = row['date'].strip()
            year_int = int(date_str[:4])
            
            # --- AJOUT DU FILTRE MOIS (JJASO : 6 à 10) ---
            # Si le format est YYYY-MM-DD, le mois est à [5:7]. Si YYYYMMDD, il est à [4:6].
            # On teste ici le format avec '-' pour être flexible.
            month_int = int(date_str[5:7]) if '-' in date_str else int(date_str[4:6])
            
            v_ms = float(row['vmax'])
            lat_tc = float(row['lat'])
            lon_tc = float(row['lon'])
            
            # Application des filtres
            # 1. Filtre Année
            if an_min <= year_int <= an_max:
                

                
                # 2. Filtre Mois (uniquement si JJASO est True)
                if JJASO and not (6 <= month_int <= 8):
                    continue
                

                '''
                # 3. Filtre Zone (MDR)
                if FILTER_ZONE:
                    if not (lat_min <= lat_tc <= lat_max and lon_min <= lon_tc <= lon_max):
                        continue'''
                
                # 4. Filtre intensité (Seuil de vent)
                if v_ms < svent:
                    continue

                tc_id = (str(year_int), row['numtc'])
                if tc_id not in cyclones:
                    cyclones[tc_id] = {'vmax': []}
                
                cyclones[tc_id]['vmax'].append(v_ms)
        except (ValueError, TypeError, KeyError):
            continue

# Calcul de l'ACE par année
annual_ace = {str(y): 0.0 for y in range(an_min, an_max + 1)}
for (year, num), data in cyclones.items():
    # Application du seuil de vent de 26 m/s
    # ACE = sum(v_kts^2) / 10000                            | 1 m/s = 1.94384 knts #################################################### TOFIX ###########################""
    ace_val = sum(((v * 1.94384)**2) / 10000 for v in data['vmax']) #if vent>svent
    annual_ace[year] += ace_val

sorted_years = sorted(annual_ace.keys())
ace_values = [annual_ace[y] for y in sorted_years]

# --- 4. Plots ---

# Graphique 1 : Séries temporelles
fig1, ax1 = plt.subplots(figsize=(12, 6))
color_ace = 'steelblue'
ax1.bar(sorted_years, ace_values, color=color_ace, alpha=0.6, label=f'ACE {data_f}')
ax1.set_xlabel('Année')
ax1.set_ylabel('ACE ($10^4 kt^2$)', color=color_ace)
ax1.tick_params(axis='y', labelcolor=color_ace)
ax1.set_title(f'ACE/Dust({an_min}-{an_max}) | Zone MDR {FILTER_ZONE}')

ax2 = ax1.twinx()
color_aod = 'darkorange'
ax2.plot(sorted_years, values_aod, color=color_aod, marker='o', linewidth=2, label=f'AOD {data_f}')
ax2.set_ylabel('Dust AOD', color=color_aod)
ax2.tick_params(axis='y', labelcolor=color_aod)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
ax1.grid(axis='y', linestyle='--', alpha=0.3)
plt.xticks(sorted_years[::5]) 

# Graphique 2 : Corrélation ACE f(AOD)
plt.figure(figsize=(8, 6))
plt.scatter(values_aod, ace_values, color='purple', alpha=0.7, label='Données annuelles')

# Calcul de la droite de tendance
z = np.polyfit(values_aod, ace_values, 1)
p = np.poly1d(z)

# Création de la légende avec les coefficients (f-string)
# z[0] est la pente (a), z[1] est l'ordonnée à l'origine (b)
equation_label = f'Régression : y = {z[0]:.2f}x + {z[1]:.2f}'



# ... (tes données values_aod et ace_values) ...

plt.figure(figsize=(8, 6))
plt.scatter(values_aod, ace_values, color='purple', alpha=0.7)

# 1. Calcul de la régression linéaire
z = np.polyfit(values_aod, ace_values, 1)
p = np.poly1d(z)

# 2. Calcul du coefficient de corrélation (r)
# np.corrcoef renvoie une matrice de corrélation, on prend l'élément [0, 1]
r_matrix = np.corrcoef(values_aod, ace_values)
r = r_matrix[0, 1]
r_squared = r**2


# 3. Création de l'étiquette avec l'équation et le coefficient r
# On affiche r et éventuellement R² pour plus de précision
label_text = (f'Régression : y = {z[0]:.2f}x + {z[1]:.2f}\n'
              f'Coef. corrélation r = {r:.3f}\n'
              f'R² = {r_squared:.3f}')

plt.plot(values_aod, p(values_aod), "r--", alpha=0.8, label=label_text)

plt.xlabel(f'Moyenne annuelle AOD ({data_f})')
plt.ylabel(f'ACE Annuel ({data_f})')
plt.title(f'Corrélation ACE vs AOD (Seuil vent: {svent} m/s)')
plt.grid(True, linestyle=':', alpha=0.6)

# On place la légende (on peut ajuster loc='best' ou 'upper left')
plt.legend(loc='best', fontsize=9)

plt.tight_layout()
plt.show()

# --- 5. Extraction et affichage des classements ---

# 1. Classement ACE (Tri décroissant des valeurs du dictionnaire annual_ace)
ranking_ace = sorted(annual_ace.items(), key=lambda item: item[1], reverse=True)

# 2. Classement AOD (Association des années et des valeurs, puis tri décroissant)
aod_pairs = list(zip(years_aod, values_aod))
ranking_aod = sorted(aod_pairs, key=lambda item: item[1], reverse=True)

# --- Affichage formaté dans la console ---

print("\n" + "="*45)
print(f"  🏆 CLASSEMENT ACE ({an_min}-{an_max}) - Source: {data_f}")
print("="*45)
print(f"{'Rang':<6} | {'Année':<6} | {'Valeur ACE (10⁴ kt²)':<20}")
print("-" * 45)
for rank, (year, val) in enumerate(ranking_ace, 1):
    print(f"{rank:<6} | {year:<6} | {val:.2f}")

print("\n" + "="*45)
print(f"  🌪️ CLASSEMENT AOD MOYEN ({an_min}-{an_max})")
print("="*45)
print(f"{'Rang':<6} | {'Année':<6} | {'AOD Moyen':<20}")
print("-" * 45)
for rank, (year, val) in enumerate(ranking_aod, 1):
    # int(year) au cas où le format numpy d'origine persiste
    print(f"{rank:<6} | {int(year):<6} | {val:.4f}")