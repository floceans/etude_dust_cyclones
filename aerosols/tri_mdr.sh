#!/bin/bash

# Fichiers d'entrée et de sortie
input="/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_mensuel_1960-2024.nc" #"aladin_dust_mensuel_3weeks_1960-2024.nc"
output="aladin_dust_mensuel_MDR_1960-2024.nc"

# Définition des bornes (West, East, South, North)
# 20W à 80W s'écrit -80,-20 (on va du plus petit au plus grand)
# 10N à 20N s'écrit 10,20
lon_min=-80 #-50
lon_max=-20
lat_min=10
lat_max=20

# Vérification du fichier source
if [ ! -f "$input" ]; then
    echo "Erreur : Le fichier $input est introuvable."
    exit 1
fi

echo "Découpage de la zone : Lon[$lon_min $lon_max] Lat[$lat_min $lat_max]..."

# Commande sellonlatbox : l'ordre est lon1, lon2, lat1, lat2
cdo sellonlatbox,$lon_min,$lon_max,$lat_min,$lat_max "$input" "$output"

echo "Découpage terminé !"
echo "Fichier final : $output"