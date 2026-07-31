#!/bin/bash

EXPS="ref" #"ERA5 ERA5_NoRadDust" #NoRadDust
PATHIN="~/Documents/data/vents_aladin/" #"/cnrm/mosca/USERS/gevaudanm/NO_SAVE/ALADIN/CAM20/output/CAM20_"
vars="va700 va850" #va700 sud et va850 nord ou inverse
#v
fname="_ref_dayly_4s_" #"_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_"
lfilter="2-10"
yini=1960
yend=2000

#-----------------
for EXP in $EXPS
do
    for cvar in $vars 
    do
        echo "Processing: $EXP $cvar"
        
        # Correction : Pas d'espace autour du "="
        PATHCO="${PATHIN}${EXP}"
        FILEIN="${cvar}${fname}${yini}-${yend}.nc"

        # Exécution de NCL
        ncl cvar="${cvar}" lfilter="${lfilter}" EXP="${EXP}" yini="${yini}" yend="${yend}" fname="${fname}" filter_timescales_ALADIN_y.ncl > "out_ALADIN_${cvar}_2-10d_${EXP}.txt"

        # Si vous ne voulez pas de "anom_BP-2-10_" dans le nom, modifiez cette ligne :
        # Ici, j'enlève la partie qui vous dérangeait selon votre message
        FILEIN2="${cvar}${fname}${yini}-${yend}"
        
        # Si le script NCL génère bien un fichier avec "anom_BP", gardez votre version :
        # FILEIN2="${cvar}_anom_BP-${lfilter}${fname}day_${yini}0101-${yend}1231"

        echo "##################"
        echo "Path: ${PATHCO}"
        
        # Vérification si le fichier existe avant CDO pour éviter les erreurs
        if [ -f "${PATHCO}/${FILEIN2}.nc" ]; then

            cdo selmon,5,6,7,8,9,10 "${PATHCO}/${FILEIN2}.nc" "${PATHCO}/${FILEIN2}_MJJASO.nc" 
            cdo selday,8/31 "${PATHCO}/${FILEIN2}_MJJASO.nc" "${PATHCO}/${FILEIN2}_MJJASO_filtered.nc" ########### tri day
            cdo timstd "${PATHCO}/${FILEIN2}_MJJASO_filtered.nc" "${PATHCO}/${FILEIN2}_MJJASO_std.nc"
        else
            echo "Erreur : Fichier introuvable ${PATHCO}/${FILEIN2}.nc"
        fi
    done
done



