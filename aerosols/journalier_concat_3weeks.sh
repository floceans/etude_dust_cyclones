#!/bin/bash


files=(
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19600101-19601231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19610101-19651231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19660101-19701231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19710101-19751231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19760101-19801231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19810101-19851231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19860101-19901231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19910101-19951231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19960101-20001231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20010101-20051231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20060101-20101231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20110101-20151231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20160101-20201231.nc"
"/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20210101-20231231.nc"
)

output="final_without_first_weeks.nc"
temp_concat="temp_total.nc"

echo "Étape 1 : Concaténation des fichiers..."

cdo mergetime "${files[@]}" "$temp_concat"

if [ ! -f "$temp_concat" ]; then
    echo "Erreur : La concaténation a échoué, vérifiez la présence des fichiers source."
    exit 1
fi

echo "Étape 2 : Suppression de la première semaine de chaque mois..."

cdo selday,8/31 "$temp_concat" "$output"

echo "Étape 3 : Nettoyage..."
rm -f "$temp_concat"

echo "Terminé ! Le fichier final est : $output"