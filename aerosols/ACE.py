import csv
import matplotlib.pyplot as plt
from datetime import datetime

# --- 1. Paramètres de filtrage et fichiers ---
annee_min = 2000
annee_max = 2020

aladin = 'ALADIN_rel10_1960_2024.csv'
ibtracs = 'ibtracs_transformed_1960_2024.csv'

file_path = ibtracs  # Modifiez ici pour changer de source

conversion_factor = 1.94384  # m/s vers Noeuds
cyclones = {}  # { (year, numtc): { 'vmax': [], 'lon': [], 'lat': [] } }

# --- 2. Lecture du fichier CSV avec filtre temporel ---
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

        # FILTRE : On ignore les lignes hors de la période choisie
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

# --- 3. Calcul de l'ACE ---
annual_ace = {} 
cyclone_ace_results = [] 

for (year, num), data in cyclones.items():
    # Formule ACE : somme des (v^2)/10000 pour v >= 35 kts
    ace_val = sum((v**2) / 10000 for v in data['vmax'] if v >= 35)
    
    # Agrégation annuelle
    annual_ace[year] = annual_ace.get(year, 0) + ace_val
    
    # Stockage pour le top trajectoires
    cyclone_ace_results.append({
        'id': f"{year}-{num}",
        'ace': ace_val,
        'lon': data['lon'],
        'lat': data['lat']
    })

# --- 4. Préparation des données pour le Plot ---
# On s'assure que toutes les années de la plage sont présentes, même à 0
sorted_years = [str(y) for y in range(annee_min, annee_max + 1)]
ace_values = [annual_ace.get(y, 0) for y in sorted_years]

# Top 5 des cyclones les plus énergétiques sur la période sélectionnée
top_5_tcs = sorted(cyclone_ace_results, key=lambda x: x['ace'], reverse=True)[:5]

# --- 5. Visualisation ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Plot 1 : ACE Annuelle
ax1.bar(sorted_years, ace_values, color='skyblue', edgecolor='navy')
ax1.set_title(f"Énergie Cyclonique Accumulée (ACE) de {annee_min} à {annee_max}", fontsize=14)
ax1.set_ylabel("ACE ($10^4 kt^2$)")
ax1.tick_params(axis='x', rotation=70)

# Plot 2 : Trajectoires du Top 5 de la période
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

plt.tight_layout()
plt.show()