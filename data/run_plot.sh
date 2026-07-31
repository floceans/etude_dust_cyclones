#!/bin/bash

# Nom de ton script python
PYTHON_SCRIPT="data/plot_diff_theta_e.py"

# Liste des niveaux de pression en Pa
PLEVS=(100000 92500 85000 75000 70000 60000 50000 40000 30000 25000 20000)

echo "Début de la génération des cartes de différence Theta_e..."
echo "-----------------------------------------------------------"

for PLEV in "${PLEVS[@]}"
do
    echo "Traitement du niveau : $((PLEV/100)) hPa..."
    
    # Exécution du script python avec le niveau en argument
    python3 "$PYTHON_SCRIPT" "$PLEV"
    
done

echo "-----------------------------------------------------------"
echo "Terminé ! Toutes les images ont été générées."