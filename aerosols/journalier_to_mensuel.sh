#!/bin/bash

# Nom du fichier généré à l'étape précédente
input="aladin_dust_dayly_3weeks_1960_2024.nc"
output="aladin_dust_mensuel_3weeks_1960-2024.nc"

# Vérification de l'existence du fichier source
if [ ! -f "$input" ]; then
    echo "Erreur : Le fichier $input est introuvable."
    exit 1
fi

echo "Calcul des moyennes mensuelles en cours..."

# L'opérateur 'monmean' calcule la moyenne par mois.
# Comme les 7 premiers jours sont absents du fichier, CDO fera :
# (Somme des jours 8 à 31) / (Nombre de jours présents)
# Il ne comptera pas les jours manquants comme des zéros.
cdo monmean "$input" "$output"

echo "Traitement terminé !"
echo "Fichier produit : $output"