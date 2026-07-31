#!/bin/bash

# ==============================================================================
# CONFIGURATION
# ==============================================================================
YEARMIN=1960
YEARMAX=2023
BASE_PATH="/cnrm/mosca/USERS/gevaudanm/NO_SAVE/ALADIN/CAM20/output/CAM20_ERA5/day/rsds"

# Nom fichier final (Mis à jour pour refléter "full month")
FINAL_OUTPUT="rsds_ref_4s_${YEARMIN}-${YEARMAX}.nc"
TMP_DIR="tmp_work"
# ==============================================================================

chemins=("rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19600101-19601231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19610101-19651231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19660101-19701231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19710101-19751231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19760101-19801231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19810101-19851231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19860101-19901231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19910101-19951231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19960101-20001231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20010101-20051231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20060101-20101231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20110101-20151231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20160101-20201231.nc"
    "rsds_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20210101-20231231.nc")

mkdir -p "$TMP_DIR"
echo "Début du traitement des moyennes mensuelles (jours complets)..."

for FILE_NAME in "${chemins[@]}"; do
    
    FULL_PATH="${BASE_PATH}/${FILE_NAME}"

    if [ ! -f "$FULL_PATH" ]; then
        echo "XXX Fichier introuvable : $FILE_NAME (Ignoré) XXX"
        continue
    fi

    # Extraction des années du fichier
    RANGE=$(echo "$FILE_NAME" | grep -oE '[0-9]{8}-[0-9]{8}')
    START_FILE_YEAR=$(echo "$RANGE" | cut -d'-' -f1 | cut -c1-4)
    END_FILE_YEAR=$(echo "$RANGE" | cut -d'-' -f2 | cut -c1-4)

    echo ">>> Traitement : $FILE_NAME"

    for (( YEAR=$START_FILE_YEAR; YEAR<=$END_FILE_YEAR; YEAR++ )); do
        
        if (( YEAR < YEARMIN || YEAR > YEARMAX )); then
            continue
        fi

        echo "  --- Année : $YEAR ---"

        # On utilise directement monmean sur l'année sélectionnée.
        # CDO gère automatiquement le découpage par mois à l'intérieur d'une année.
        cdo -s -monmean -selyear,"$YEAR" "$FULL_PATH" "${TMP_DIR}/mean_${YEAR}.nc"
        
    done
done

# Fusion finale
echo "------------------------------------------------"
echo "Fusion finale..."
cdo -s -mergetime "${TMP_DIR}/mean_*.nc" "$FINAL_OUTPUT"

# Nettoyage
rm -rf "$TMP_DIR"

echo "Terminé ! Résultat disponible dans : $FINAL_OUTPUT"