#!/bin/bash

# Liste des valeurs à passer en argument
valeurs_vent=(0 5 10 12 14 16 18 20 22 24 26 28 30 32 34)
valeurs_vort=(0 10 15 20 25 30 40 50 60 70 80 90 100)
valeurs_press=(1010 1005 1000 995 990 985 980 975 970 965 960 955 950)
#valeurs_vent=(27.5 32.5)
#valeurs_vort=(22.5 27.5)

# Boucle pour exécuter le script Python avec chaque valeur
for s_vent in "${valeurs_vent[@]}"
do
    for s_press in "${valeurs_press[@]}"
    do
        echo "Exécution avec s_vent = $s_vent et s_press = $s_press " 
        /bin/python3 /home/puyf/Documents/git/etude_dust_cyclones/densite/diff_density_cyclogenese.py 1960 2024 "$s_press" "$s_vent" 0 #"$s_vort"
    done
done
