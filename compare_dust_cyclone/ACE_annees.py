import csv
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from func_dust_cy import load_data 


FILTER_ZONE = True  # Mettre à True pour filtrer sur -80E/-20E et 10N/20N
lat_min, lat_max = 10, 20
lon_min, lon_max = -60, -20


an_min = 1960
an_max = 2000
svent = 26  # Seuil de vent en m/s
data_f = 'aladin' ## atention pr ibtracs mettre seuil vent à 0 !!! 
fort_AOD = True


liste_mois = ['j','j', 'a', 's', 'o']  

# Convertisseur auto
liste_mois_num = []
if all(isinstance(m, int) for m in liste_mois):
    liste_mois_num = liste_mois
else:
    ref_annee = ['j', 'f', 'm', 'a', 'm', 'j', 'j', 'a', 's', 'o', 'n', 'd']
    input_str = "".join([str(m).lower() for m in liste_mois])
    ref_str = "".join(ref_annee)
    start_idx = ref_str.find(input_str)
    
    if start_idx != -1:
        liste_mois_num = [start_idx + i + 1 for i in range(len(liste_mois))]
    else:
        mapping_3l = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12,
                      'janv':1, 'févr':2, 'mars':3, 'avri':4, 'mai':5, 'juin':6, 'juil':7, 'août':8, 'sept':9, 'octo':10, 'nove':11, 'déce':12}
        for m in liste_mois:
            m_str = str(m).lower()[:3]
            if m_str in mapping_3l:
                liste_mois_num.append(mapping_3l[m_str])
            elif m_str.isdigit():
                liste_mois_num.append(int(m_str))

print(f"📅 Mois pris en compte (numériques) : {liste_mois_num}")


ibtracs = 'ibtracs_transformed_1960_2024.csv'
aladin_N = 'ALADIN_rel10_1960_2024.csv'
aladin = 'ALADIN-NoRadDust-rel10_1960_2000.csv'
FILE = aladin if data_f == 'aladin' else ibtracs
aladin_NoRadDust = None
FILE = aladin_NoRadDust if data_f == 'aladin_norad' else FILE

aladin_dust = '/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_mensuel_1960-2024.nc'
merra = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'

AOD_FILE_PATH_1 = aladin_dust
AOD_FILE_PATH_2 = merra
VAR_AOD_1 = "od550dust"
VAR_AOD_2 = "DUEXTTAU"


aod_masked_1 = load_data(AOD_FILE_PATH_1, VAR_AOD_1, an_min, an_max, False)
aod_masked_2 = load_data(AOD_FILE_PATH_2, VAR_AOD_2, an_min, an_max, False)

aod_masked_1 = aod_masked_1.where(aod_masked_1.time.dt.month.isin(liste_mois_num), drop=True)
aod_masked_2 = aod_masked_2.where(aod_masked_2.time.dt.month.isin(liste_mois_num), drop=True)

if FILTER_ZONE:
    aod_masked_1 = aod_masked_1.where(
        (aod_masked_1.lat >= lat_min) & (aod_masked_1.lat <= lat_max) & 
        (aod_masked_1.lon >= lon_min) & (aod_masked_1.lon <= lon_max), 
        drop=True
    )
    aod_masked_2 = aod_masked_2.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

# Moyennes annuelles
aod_annual_series_1 = aod_masked_1.mean(dim=['x', 'y']).groupby('time.year').mean()
aod_annual_series_2 = aod_masked_2.mean(dim=['lat', 'lon']).groupby('time.year').mean()

years_aod = aod_annual_series_1.year.values if data_f == 'aladin' else aod_annual_series_2.year.values
values_aod = aod_annual_series_1.values if data_f == 'aladin' else aod_annual_series_2.values


cyclones = {}
with open(FILE, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            date_str = row['date'].strip()
            year_int = int(date_str[:4])
            month_int = int(date_str[5:7]) if '-' in date_str else int(date_str[4:6])
            
            v_ms = float(row['vmax'])
            lat_tc = float(row['lat'])
            lon_tc = float(row['lon'])
            
            if an_min <= year_int <= an_max:
                if month_int not in liste_mois_num:
                    continue
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
    ace_val = sum(((v * 1.94384)**2) / 10000 for v in data['vmax'])
    annual_ace[year] += ace_val

sorted_years = sorted(annual_ace.keys())
ace_values = [annual_ace[y] for y in sorted_years]


max_ace_global = max(ace_values) if ace_values else 10.0
max_ace_limit = max_ace_global * 1.1


# Graphique 1 : Séries temporelles
fig1, ax1 = plt.subplots(figsize=(12, 6))
color_ace = 'steelblue'
ax1.bar(sorted_years, ace_values, color=color_ace, alpha=0.6, label=f'ACE {data_f}')
ax1.set_xlabel('Année')
ax1.set_ylabel('ACE ($10^4 kt^2$)', color=color_ace)
ax1.tick_params(axis='y', labelcolor=color_ace)
ax1.set_ylim(0, max_ace_limit)  # Application de l'échelle fixe
ax1.set_title(f'ACE/Dust({an_min}-{an_max}) | Zone MDR {FILTER_ZONE} | Mois: {liste_mois_num}')

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
plt.scatter(values_aod, ace_values, color='purple', alpha=0.7)

z = np.polyfit(values_aod, ace_values, 1)
p = np.poly1d(z)
r_matrix = np.corrcoef(values_aod, ace_values)
r = r_matrix[0, 1]
r_squared = r**2

label_text = (f'Régression : y = {z[0]:.2f}x + {z[1]:.2f}\n'
              f'Coef. corrélation r = {r:.3f}\n'
              f'R² = {r_squared:.3f}')

plt.plot(values_aod, p(values_aod), "r--", alpha=0.8, label=label_text)
plt.xlabel(f'Moyenne AOD ({data_f}) [Mois: {liste_mois_num}]')
plt.ylabel(f'ACE Annuel ({data_f})')
plt.ylim(0, max_ace_limit)  # Application de l'échelle fixe
plt.title(f'Corrélation ACE vs AOD (Seuil vent: {svent} m/s)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(loc='best', fontsize=9)
plt.tight_layout()

# --- 5. Extraction et affichage des classements ---
ranking_ace = sorted(annual_ace.items(), key=lambda item: item[1], reverse=True)
aod_pairs = list(zip(years_aod, values_aod))
ranking_aod = sorted(aod_pairs, key=lambda item: item[1], reverse=True)


#Diagramme en bâtons pour le TOP 10 (Fort ou Faible AOD) ---
# --- BOOLEEN DE SELECTION ---
  # True pour les 10 plus forts, False pour les 10 plus faibles
# ----------------------------

if fort_AOD:
    selection_aod = ranking_aod[:10]
    titre_graphique = f"Valeurs d'ACE de NoRadDust pour le TOP 10 des années avec le plus FORT Dust-AOD\n(Mois filtrés: {liste_mois_num})"
    label_x = 'Années (Classées du plus fort au moins fort AOD →)'
    couleur_barres = 'indianred'
else:
    selection_aod = ranking_aod[-10:][::-1]
    titre_graphique = f"Valeurs d'ACE de NoRadDust pour le TOP 10 des années avec le plus FAIBLE Dust-AOD\n(Mois filtrés: {liste_mois_num})"
    label_x = 'Années (Classées du plus faible au moins faible AOD →)'
    couleur_barres = 'cornflowerblue'

annees_top_10 = [str(int(year)) for year, val in selection_aod]
annees_filtrees = [annee for annee in annees_top_10 if annee in annual_ace]
ace_filtres = [annual_ace[annee] for annee in annees_filtrees]

fig3, ax3 = plt.subplots(figsize=(10, 6))
barres = ax3.bar(annees_filtrees, ace_filtres, color=couleur_barres, alpha=0.8, edgecolor='black')

for barre in barres:
    hauteur = barre.get_height()
    ax3.text(barre.get_x() + barre.get_width() / 2, hauteur + (max_ace_limit * 0.01), 
             f'{hauteur:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax3.set_xlabel(label_x, fontsize=18)
ax3.set_ylabel('ACE ($10^4 kt^2$)', fontsize=18)
ax3.set_ylim(0, max_ace_limit)  # Application de l'échelle fixe
ax3.set_title(titre_graphique, fontsize=21, fontweight='bold')
ax3.grid(axis='y', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.show()