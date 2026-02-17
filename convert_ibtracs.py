import pandas as pd
import numpy as np

def convert_ibtracs_to_suiera5(input_file, output_file):
    # 1. Chargement des données
    # On saute la 2ème ligne (index 1) qui contient les unités dans IBTrACS
    df = pd.read_csv(input_file, skiprows=[1], low_memory=False)

    # 2. Nettoyage et tri
    # On s'assure que le temps est au format datetime pour le tri
    df['ISO_TIME'] = pd.to_datetime(df['ISO_TIME'])
    df = df.sort_values(['SID', 'ISO_TIME'])

    # 3. Création des identifiants (numtc et step)
    # numtc : Numéro unique par tempête (basé sur le SID)
    df['numtc'] = pd.factorize(df['SID'])[0] + 1
    
    # step : Étape temporelle au sein de chaque tempête
    df['step'] = df.groupby('SID').cumcount() + 1

    # 4. Conversion des variables numériques
    # On convertit en numérique et on gère les valeurs manquantes (espaces)
    df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
    df['LON'] = pd.to_numeric(df['LON'], errors='coerce')
    df['USA_WIND'] = pd.to_numeric(df['USA_WIND'], errors='coerce')
    df['USA_PRES'] = pd.to_numeric(df['USA_PRES'], errors='coerce')

    # 5. Mapping vers le format suiERA5
    output_df = pd.DataFrame()
    output_df['numtc'] = df['numtc']
    output_df['step'] = df['step']
    output_df['date'] = df['ISO_TIME'].dt.strftime('%Y-%m-%d %H:%M:%S')
    output_df['lon'] = df['LON']
    output_df['lat'] = df['LAT']
    
    # vomax n'existe pas dans IBTrACS, on met 0.0
    output_df['vomax'] = 0.0
    
    # vmax : Conversion kts -> m/s (si USA_WIND est présent)
    output_df['vmax'] = df['USA_WIND'] * 0.514444 /1.12 # pour convertir frequence mesure 
    
    # pmin : Pression minimale
    output_df['pmin'] = df['USA_PRES']
    
    # oprel : Toujours 1 selon votre consigne
    output_df['oprel'] = 1

    # 6. Exportation
    output_df.to_csv(output_file, index=False)
    print(f"Conversion terminée. Fichier sauvegardé sous : {output_file}")

# Utilisation
input_filename = 'ibtracs.NA.list.v04r01_1960-2024.csv'
output_filename = 'ibtracs_transformed_1960_2024.csv'
convert_ibtracs_to_suiera5(input_filename, output_filename)