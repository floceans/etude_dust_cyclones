#!/bin/bash

# 1. Liste des fichiers (vérifie bien qu'ils sont dans le dossier courant)
files=(
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19600101-19601231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19610101-19651231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19660101-19701231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19710101-19751231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19760101-19801231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19810101-19851231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19860101-19901231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19910101-19951231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_19960101-20001231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20010101-20051231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20060101-20101231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20110101-20151231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20160101-20201231.nc"
"/home/puyf/Documents/dust_brut_1/aladin/quotidien/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_day_20210101-20231231.nc"
)

output="final_without_first_weeks.nc"
temp_concat="temp_total.nc"

echo "Étape 1 : Concaténation des fichiers..."
# On utilise mergetime pour être sûr que l'ordre chronologique est respecté
cdo mergetime "${files[@]}" "$temp_concat"

# Vérification si le fichier a bien été créé
if [ ! -f "$temp_concat" ]; then
    echo "Erreur : La concaténation a échoué, vérifiez la présence des fichiers source."
    exit 1
fi

echo "Étape 2 : Suppression de la première semaine de chaque mois..."
# La commande selday,8/31 sélectionne les jours du 8 au 31 pour CHAQUE mois présent
# CDO gère automatiquement les mois courts (28, 30 jours) sans erreur.
cdo selday,8/31 "$temp_concat" "$output"

echo "Étape 3 : Nettoyage..."
rm -f "$temp_concat"

echo "Terminé ! Le fichier final est : $output"