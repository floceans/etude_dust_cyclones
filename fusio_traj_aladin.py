import os

# Paramètres
start_year = 1960
end_year = 2024
# Vous pouvez changer 'rel10' par 'rel200' selon le groupe de fichiers à fusionner
suffix = "rel10" 
output_filename = f"combined_ERA5_{suffix}_1960_2024.csv"

first_file = True

with open(output_filename, 'w', encoding='utf-8') as outfile:
    for year in range(start_year, end_year + 1):
        # Construction du nom de fichier (ex: 1960-1961)

        filename = f"/home/puyf/Documents/git/etude_dust_cyclones/trac_3/suiERA5_evaluation_{year}-{year+1}.vor15_res17_1_-2_5.{suffix}.csv"
        
        if os.path.exists(filename):
            print(f"Traitement de : {filename}...")
            with open(filename, 'r', encoding='utf-8') as infile:
                # On utilise un énumérateur pour repérer la première ligne (index 0)
                for i, line in enumerate(infile):
                    # Si c'est le premier fichier, on prend tout
                    # Sinon, on saute la ligne 0 (l'en-tête)
                    if i == 0 and not first_file:
                        continue
                    outfile.write(line)
            
            first_file = False
        else:
            # Optionnel : afficher si un fichier manque dans la série
            print(f"⚠️ Fichier manquant : {filename}")

print(f"\nTerminé ! Le fichier fusionné est : {output_filename}")