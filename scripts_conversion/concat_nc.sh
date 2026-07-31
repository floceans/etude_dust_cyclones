#!/bin/bash

# --- Configuration ---
# Chemin vers les fichiers
INPUT_DIR="/cnrm/mosca/USERS/gevaudanm/NO_SAVE/ALADIN/CAM20/output/CAM20_ERA5_NoRadDust/day/prw"

# Bornes temporelles pour le nom du fichier de sortie
YEAR_MIN=1960
YEAR_MAX=2000

# Variables à traiter
VARIABLES=("prw")

# --- Début du traitement ---
echo "Début de la concaténation CDO..."
echo "Répertoire source : $INPUT_DIR"

for VAR in "${VARIABLES[@]}"; do
    echo "------------------------------------------------"
    echo "Traitement de : $VAR"

    # Construction du nom du fichier de sortie
    # On reprend la structure de vos fichiers en injectant les années min/max
    OUTPUT_FILE="${VAR}_norad_dayly_4s_${YEAR_MIN}-${YEAR_MAX}.nc"

    # Commande CDO
    # -O : Écrase le fichier de sortie s'il existe déjà
    # mergetime : Concatène chronologiquement
    cdo -O mergetime "${INPUT_DIR}/${VAR}_"*.nc "$OUTPUT_FILE"

    # Vérification du succès
    if [ $? -eq 0 ]; then
        echo "Fichier créé avec succès : $OUTPUT_FILE"
    else
        echo "Erreur lors du traitement de $VAR. Vérifiez les fichiers sources."
    fi
done

echo "------------------------------------------------"
echo "Opération terminée."