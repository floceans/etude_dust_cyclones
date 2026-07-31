import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys
from func import get_density_cyclogenese_aladin, get_density_cyclogenese_ibtracs, indice_global_cyclogenese

nom_fichier = "resultats_cyclogenese.txt"

def main():
    # --- AUGMENTATION DE LA TAILLE DE LA POLICE GLOBALE ---
    # Cela va impacter les axes, la colorbar et les labels de la grille
    plt.rcParams.update({'font.size': 21}) 

    AN_MIN = 1960
    AN_MAX = 2000
    SVORT = 0
    SVENT = 26
    SPRESS = 1005

    ibtracs = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ibtracs_transformed_1960_2024.csv'

    file2 = 'ALADIN_rel10_1960_2024.csv'
    file1 = 'ALADIN-NoRadDust-rel10_1960_2000.csv' #ibtracs

    yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else AN_MIN
    yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else AN_MAX
    seuil_press = float(sys.argv[3]) if len(sys.argv) > 3 else SPRESS
    seuil_vent = float(sys.argv[4]) if len(sys.argv) > 4 else SVENT 
    seuil_vort = float(sys.argv[5]) if len(sys.argv) > 5 else SVORT 

    lonmin, lonmax, latmin, latmax = -105, 5, 0, 30 #-130, 30, -25, 35 

    print(f"Calcul de la densité pour {file1}...")
    zi1, x1, y1, xi, yi, npts1 = get_density_cyclogenese_aladin(file1, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vent, seuil_press)
    
    print(f"Calcul de la densité pour {file2}...")
    zi2, x2, y2, _, _, npts2 = get_density_cyclogenese_aladin(file2, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vent, seuil_press)

    zi_diff = zi1 - zi2

    indice_global_cyclogenese_diff = indice_global_cyclogenese(zi_diff, lonmin, lonmax, latmin, latmax)
    print(f"RMSE pour {file1} - {file2} : {indice_global_cyclogenese_diff:.2f}")
    print(f"Nombre de points de cyclogenèse pour {file1} : {npts1}")
    print(f"Nombre de points de cyclogenèse pour {file2} : {npts2}")
    print(f"Années couvertes : {yearmin} à {yearmax}")
    print(f'seuil vorticité : {seuil_vort}, seuil de vent : {seuil_vent}')

    with open(nom_fichier, 'a') as fichier:
        fichier.write(f"{seuil_press}, {seuil_vent}, {indice_global_cyclogenese_diff:.2f}, {npts1}, {npts2}\n")

    # --- Plotting ---
    fig = plt.figure(figsize=(14, 10)) # Légèrement agrandi pour accueillir les plus grosses polices
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=proj)
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
    
    ax.coastlines(resolution='50m', linewidth=1)
    
    # Augmentation de la taille des étiquettes des coordonnées (gridlines)
    gl = ax.gridlines(draw_labels=True, alpha=0.3)
    gl.xlabel_style = {'size': 21}
    gl.ylabel_style = {'size': 21}

    echelle = 1
    vmax = np.max(np.abs(zi_diff))
    levels = np.linspace(-echelle, echelle, 17)

    # --- ADAPTATION DALTONISME ---
    # Définition des styles : tirets ('--') pour < 0, continu ('-') pour >= 0
    styles_lignes = ['--' if val < 0 else '-' for val in levels]

    cf = ax.contourf(xi, yi, zi_diff, levels=levels, cmap='RdBu_r', 
                     vmin=-vmax, vmax=vmax, transform=proj, extend='both')
    
    # Ajout de l'argument 'linestyles=styles_lignes'
    cs = ax.contour(xi, yi, zi_diff, levels=levels, colors='black', 
                    linewidths=0.5, alpha=0.8, transform=ccrs.PlateCarree(), 
                    linestyles=styles_lignes)
    
    # --- MISE EN GRAS DES ÉTIQUETTES (CORRECTION PYTHON) ---
    # 1. On récupère la liste des objets texte générés
    labels = ax.clabel(cs, inline=True, fontsize=10, fmt='%1.1f')
    # 2. On applique le style "bold" (gras) sur chaque étiquette de la liste
    for t in labels:
        t.set_fontweight('bold')

    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40)
    # Augmentation de la taille du label de la colorbar
    cbar.set_label(f'Différence de densité ({file1} - {file2})', fontsize=14)

    # Augmentation de la taille du titre (fontsize=18 au lieu de 14)
    plt.title(f'Carte Différence cyclogénèse\n{yearmin}-{yearmax} \n seuil press = {seuil_press} $hPa$, seuil vent = {seuil_vent} $m.s^{{-1}}$ sur Aladin', fontsize=18)
    
    output = "difference_density.png"
    plt.show()

if __name__ == "__main__":
    main()