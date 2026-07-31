#!/bin/bash

# ==============================================================================
# CONFIGURATION
# ==============================================================================
YEARMIN=1960
YEARMAX=2023
BASE_PATH="/cnrm/mosca/USERS/gevaudanm/NO_SAVE/ALADIN/CAM20/output/CAM20_ERA5_NoRadDust/day/hus_concat"

# Nom fichier final
FINAL_OUTPUT="hus_concat_NoRadDust_3weeks_monthly_${YEARMIN}-${YEARMAX}.nc"
TMP_DIR="tmp_work"
# ==============================================================================

chemins=("hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1960.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1961.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1962.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1963.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1964.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1965.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1966.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1967.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1968.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1969.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1970.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1971.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1972.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1973.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1974.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1975.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1976.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1977.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1978.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1979.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1980.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1981.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1982.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1983.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1984.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1985.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1986.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1987.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1988.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1989.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1990.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1991.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1992.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1993.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1994.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1995.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1996.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1997.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1998.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_1999.nc"
"hus_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_2000.nc")


mkdir -p "$TMP_DIR"
echo "Début du traitement..."

# --- BOUCLE 1 : Sur chaque fichier de la liste ---
for FILE_NAME in "${chemins[@]}"; do
    
    FULL_PATH="${BASE_PATH}/${FILE_NAME}"

    if [ ! -f "$FULL_PATH" ]; then
        echo "XXX Fichier introuvable : $FILE_NAME (Ignoré) XXX"
        continue
    fi

    # --- CORRECTION DE L'EXTRACTION ---
    # On regarde si le fichier contient une plage (YYYYMMDD-YYYYMMDD) ou juste une année (YYYY.nc)
    if [[ "$FILE_NAME" =~ ([0-9]{8})-([0-9]{8}) ]]; then
        # Cas plage de dates : on prend les 4 premiers chiffres de chaque bloc
        START_FILE_YEAR=${BASH_REMATCH[1]:0:4}
        END_FILE_YEAR=${BASH_REMATCH[2]:0:4}
    elif [[ "$FILE_NAME" =~ ([0-9]{4})\.nc ]]; then
        # Cas année unique : début et fin sont identiques
        START_FILE_YEAR=${BASH_REMATCH[1]}
        END_FILE_YEAR=${BASH_REMATCH[1]}
    else
        echo "XXX Impossible de déterminer l'année pour : $FILE_NAME (Ignoré) XXX"
        continue
    fi

    echo ">>> Traitement : $FILE_NAME (Période : $START_FILE_YEAR à $END_FILE_YEAR)"

    # --- BOUCLE 2 : Sur chaque année du fichier en cours ---
    for (( YEAR=$START_FILE_YEAR; YEAR<=$END_FILE_YEAR; YEAR++ )); do
        
        # On vérifie si l'année est dans la plage globale souhaitée
        if (( YEAR < YEARMIN || YEAR > YEARMAX )); then
            continue
        fi

        echo "  --- Analyse de l'année : $YEAR ---"

        # Extraction de l'année complète
        cdo -s selyear,"$YEAR" "$FULL_PATH" "${TMP_DIR}/year_temp.nc" 2>/dev/null
        
        if [ $? -ne 0 ]; then 
            continue 
        fi

        for MONTH in {01..12}; do
            # Extraction du mois
            cdo -s -selmon,$((10#$MONTH)) "${TMP_DIR}/year_temp.nc" "${TMP_DIR}/month_full.nc" 2>/dev/null
            
            if [ $? -eq 0 ] && [ -f "${TMP_DIR}/month_full.nc" ]; then
                N_DAYS=$(cdo -s ntime "${TMP_DIR}/month_full.nc")
                
                # Correction : on vérifie que N_DAYS n'est pas vide avant le test
                if [ -n "$N_DAYS" ] && [ "$N_DAYS" -gt 7 ]; then
                    # Moyenne mensuelle à partir du 8ème jour (3 semaines)
                    cdo -s -monmean -seltimestep,8/"$N_DAYS" "${TMP_DIR}/month_full.nc" "${TMP_DIR}/mean_${YEAR}_${MONTH}.nc"
                fi
                rm -f "${TMP_DIR}/month_full.nc"
            fi
        done
        rm -f "${TMP_DIR}/year_temp.nc"
    done
done

# Fusion finale
echo "------------------------------------------------"
if ls "${TMP_DIR}"/mean_*.nc >/dev/null 2>&1; then
    echo "Fusion finale de tous les mois..."
    cdo -s -mergetime $(ls ${TMP_DIR}/mean_*.nc | sort) "$FINAL_OUTPUT"
    echo "Terminé ! Résultat : $FINAL_OUTPUT"
else
    echo "Erreur : Aucun fichier mensuel n'a été généré."
fi

# Nettoyage
rm -rf "$TMP_DIR"