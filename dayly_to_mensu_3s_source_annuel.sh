#!/bin/bash

# ==============================================================================
# CONFIGURATION
# ==============================================================================
YEARMIN=1960
YEARMAX=2023
BASE_PATH="/cnrm/mosca/USERS/gevaudanm/NO_SAVE/ALADIN/CAM20/output/CAM20_ERA5/day/hus500"


# Nom fichier final
FINAL_OUTPUT="$HOME/Documents/data/ext_aladin/ext550dust_ref_3weeks_monthly_${YEARMIN}-${YEARMAX}.nc"
TMP_DIR="tmp_work"
# ==============================================================================

mkdir -p "$TMP_DIR"

echo "Début du traitement..."

for (( YEAR=$YEARMIN; YEAR<=$YEARMAX; YEAR++ )); do
    
    # Construction du nom de fichier pour l'année en cours
    FILE="${BASE_PATH}/hus500_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_${YEAR}0101-${YEAR}1231.nc"

    # Vérification de l'existence du fichier
    if [ ! -f "$FILE" ]; then
        echo "--- Année $YEAR : Fichier introuvable, passage à la suivante ---"
        continue
    fi

    echo "--- Analyse de l'année : $YEAR ---"

    for MONTH in {01..12}; do
        # Extraction du mois spécifique
        cdo -s -selmon,$((10#$MONTH)) "$FILE" "${TMP_DIR}/month_full.nc" 2>/dev/null
        
        if [ $? -eq 0 ] && [ -f "${TMP_DIR}/month_full.nc" ]; then
            
            N_DAYS=$(cdo -s ntime "${TMP_DIR}/month_full.nc")
            
            # On ne traite que si on a assez de jours pour retirer la première semaine
            if [ "$N_DAYS" -gt 7 ]; then
                # On prend du 8ème jour jusqu'à la fin (N_DAYS) puis on fait la moyenne mensuelle
                cdo -s -monmean -seltimestep,8/"$N_DAYS" "${TMP_DIR}/month_full.nc" "${TMP_DIR}/mean_${YEAR}_${MONTH}.nc"
                echo "  Mois $MONTH : Moyenné du jour 8 au jour $N_DAYS"
            else
                echo "  Mois $MONTH : Ignoré (pas assez de données : $N_DAYS jours)"
            fi
            
            rm -f "${TMP_DIR}/month_full.nc"
        fi
    done
done

# Fusion finale
echo "------------------------------------------------"
echo "Fusion finale de tous les mois..."
# On utilise un tri pour être sûr que l'ordre chronologique est respecté
cdo -s -mergetime $(ls ${TMP_DIR}/mean_*.nc | sort) "$FINAL_OUTPUT"

# Nettoyage final
rm -rf "$TMP_DIR"

echo "Terminé ! Résultat disponible dans : $FINAL_OUTPUT"