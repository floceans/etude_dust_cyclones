#!/bin/bash

input="/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/aladin_dust_mensuel_1960-2024.nc" #"aladin_dust_mensuel_3weeks_1960-2024.nc"
output="aladin_dust_mensuel_MDR_1960-2024.nc"


lon_min=-80 #-50
lon_max=-20
lat_min=10
lat_max=20


if [ ! -f "$input" ]; then
    echo "Erreur : Le fichier $input est introuvable."
    exit 1
fi

echo "Découpage de la zone : Lon[$lon_min $lon_max] Lat[$lat_min $lat_max]..."

# Commande sellonlatbox : l'ordre est lon1, lon2, lat1, lat2
cdo sellonlatbox,$lon_min,$lon_max,$lat_min,$lat_max "$input" "$output"

echo "Découpage terminé !"
echo "Fichier final : $output"