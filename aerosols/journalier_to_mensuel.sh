#!/bin/bash

input="/home/puyf/Documents/vents/vents_aladin/vas_1960-2023_total.nc"
output="/home/puyf/Documents/vents/vents_aladin/vas_1960-2023_mensuel_total.nc"

if [ ! -f "$input" ]; then
    echo "Erreur : Le fichier $input est introuvable."
    exit 1
fi

echo "Calcul des moyennes mensuelles en cours..."


cdo monmean "$input" "$output"

echo "Traitement terminé !"
echo "Fichier produit : $output"