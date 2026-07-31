import csv
import matplotlib.pyplot as plt
from datetime import datetime


### Plot série temporelle ACE avec traj des cyclones avec plus grande ACE ###


conversion_factor = 1.94384  # m/s vers Noeuds


annee_min = 1960
annee_max = 2020
data_f = 'aladin'
svent = 28*conversion_factor

aladin = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
ibtracs = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ibtracs_transformed_1960_2024.csv'

if data_f == 'aladin' :
    file_path = aladin
else :
    file_path = ibtracs


cyclones = {}  # { (year, numtc): { 'vmax': [], 'lon': [], 'lat': [] } }


with open(file_path, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Extraction de l'année
        date_str = row['date'].strip()
        year_str = date_str[:4]
        
        try:
            year_int = int(year_str)
        except ValueError:
            continue

        # FILTRE 
        if not (annee_min <= year_int <= annee_max):
            continue
            
        tc_id = (year_str, row['numtc'])
        
        # Initialisation si nouveau cyclone
        if tc_id not in cyclones:
            cyclones[tc_id] = {'vmax': [], 'lon': [], 'lat': []}
        
        # Conversion et stockage
        try:
            v_kts = float(row['vmax']) * conversion_factor
            cyclones[tc_id]['vmax'].append(v_kts)
            cyclones[tc_id]['lon'].append(float(row['lon']))
            cyclones[tc_id]['lat'].append(float(row['lat']))
        except ValueError:
            continue


annual_ace = {} 
cyclone_ace_results = [] 

for (year, num), data in cyclones.items():
    # ace + seuillage à 26m/s
    ace_val = sum((v**2) / 10000 for v in data['vmax'] if (v > svent and data_f == 'aladin') or data_f == 'ibtracs')
    # Agrégation annuelle
    annual_ace[year] = annual_ace.get(year, 0) + ace_val
    

    cyclone_ace_results.append({
        'id': f"{year}-{num}",
        'ace': ace_val,
        'lon': data['lon'],
        'lat': data['lat']
    })


sorted_years = [str(y) for y in range(annee_min, annee_max + 1)]
ace_values = [annual_ace.get(y, 0) for y in sorted_years]

top_5_tcs = sorted(cyclone_ace_results, key=lambda x: x['ace'], reverse=True)[:5]


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))


ax1.bar(sorted_years, ace_values, color='skyblue', edgecolor='navy')
ax1.set_title(f"Énergie Cyclonique Accumulée (ACE) de {annee_min} à {annee_max}", fontsize=14)
ax1.set_ylabel("ACE ($10^4 kt^2$)")
ax1.tick_params(axis='x', rotation=70)
ax1.set_ylim(0, 375)


if top_5_tcs:
    for tc in top_5_tcs:
        ax2.plot(tc['lon'], tc['lat'], label=f"TC {tc['id']} (ACE: {tc['ace']:.1f})", marker='o', markersize=2)
    ax2.set_title(f"Trajectoires des 5 plus gros cyclones ({annee_min}-{annee_max})", fontsize=14)
    ax2.set_xlabel("Longitude")
    ax2.set_ylabel("Latitude")
    ax2.legend(loc='upper right', fontsize='small')
    ax2.grid(True, linestyle='--', alpha=0.5)
else:
    ax2.text(0.5, 0.5, "Aucune donnée sur cette période", ha='center')

plt.title(f'Données {data_f}')
plt.tight_layout()
plt.show()