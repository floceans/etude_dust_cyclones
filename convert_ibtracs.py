import csv
from datetime import datetime


def temps_6h(iso_time):
    # Vérifie si l'heure est à 00:00, 06:00, 12:00 ou 18:00
    return iso_time.hour in [0, 6, 12, 18]


def convert_ibtracs_to_suiera5(input_file, output_file):
    data = []
    
    with open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # On ignore la deuxième ligne (celle des unités)
        next(reader)
        
        for row in reader:
            try:
                # 1. Extraction et conversion des données de base
                sid = row['SID']
                iso_time = datetime.strptime(row['ISO_TIME'], '%Y-%m-%d %H:%M:%S')
                
                # Gestion des valeurs numériques (conversion sécurisée)
                usa_wind = float(row['USA_WIND']) if row['USA_WIND'].strip() else 0.0
                usa_pres = float(row['USA_PRES']) if row['USA_PRES'].strip() else 0.0
                lat = float(row['LAT']) if row['LAT'].strip() else 0.0
                lon = float(row['LON']) if row['LON'].strip() else 0.0
                
                # 2. Calcul de vmax et filtrage (vmax > 17 m/s)
                # Formule : (WIND en kts * 0.514444) / 1.12
                vmax = (usa_wind * 0.514444) / 1.12

                
                if vmax > 17 and temps_6h(iso_time):
                    data.append({
                        'SID': sid,
                        'ISO_TIME': iso_time,
                        'lat': lat,
                        'lon': lon,
                        'vmax': vmax,
                        'pmin': usa_pres
                    })
            except (ValueError, KeyError):
                # Ignore les lignes mal formées ou avec des données manquantes critiques
                continue

    # 3. Tri des données par SID puis par Temps
    data.sort(key=lambda x: (x['SID'], x['ISO_TIME']))

    # 4. Génération des numtc et step + Écriture du fichier
    fieldnames = ['numtc', 'step', 'date', 'lon', 'lat', 'vomax', 'vmax', 'pmin', 'oprel']
    
    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        current_sid = None
        numtc = 0
        step = 0
        
        for entry in data:
            # Gestion du changement de tempête pour numtc et step
            if entry['SID'] != current_sid:
                current_sid = entry['SID']
                numtc += 1
                step = 1
            else:
                step += 1
            
            writer.writerow({
                'numtc': numtc,
                'step': step,
                'date': entry['ISO_TIME'].strftime('%Y-%m-%d %H:%M:%S'),
                'lon': entry['lon'],
                'lat': entry['lat'],
                'vomax': 0.0,
                'vmax': round(entry['vmax'], 4),
                'pmin': entry['pmin'],
                'oprel': 1
            })

    print(f"Conversion terminée. {len(data)} lignes traitées.")
    print(f"Fichier sauvegardé sous : {output_file}")

# Utilisation
input_filename = 'ibtracs.NA.list.v04r01_1960-2024.csv'
output_filename = 'ibtracs_transformed_1960_2024.csv'
convert_ibtracs_to_suiera5(input_filename, output_filename)