import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys
from func import get_density_cyclogenese_aladin, get_density_cyclogenese_ibtracs, indice_global_cyclogenese

nom_fichier = "resultats_cyclogenese.txt"

def main():

    AN_MIN = 1960
    AN_MAX = 2024
    SVORT = 0
    SVENT = 28
    SPRESS = 1020

    file1 = 'ALADIN_rel10_1960_2024.csv'
    file2 = 'ibtracs_transformed_1960_2024.csv'

    yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else AN_MIN
    yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else AN_MAX
    seuil_press = float(sys.argv[3]) if len(sys.argv) > 3 else SPRESS ###########" pas pris en compte apres"
    seuil_vent = float(sys.argv[4]) if len(sys.argv) > 4 else SVENT #seuil de vort 
    seuil_vort = float(sys.argv[5]) if len(sys.argv) > 5 else SVORT #seuil de vort 


    # config grille pr deux densités
    lonmin, lonmax, latmin, latmax = -105, 5, 0, 25
    #-105, 5, 5, 35 #pr tt domaine - 
    #mdr -60, -15, 5, 20 #
    #mdr++ -105, 5, 0, 25
    # calcul densités
    print(f"Calcul de la densité pour {file1}...")
    zi1, x1, y1, xi, yi, npts1 = get_density_cyclogenese_aladin(file1, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vort, seuil_vent, seuil_press)
    
    print(f"Calcul de la densité pour {file2}...")
    zi2, x2, y2, _, _, npts2 = get_density_cyclogenese_ibtracs(file2, yearmin, yearmax, lonmin, lonmax, latmin, latmax)

    # --- Calcul de la DIFFÉRENCE ---
    # zi_diff > 0 : Plus de trajectoires dans le fichier 1
    # zi_diff < 0 : Plus de trajectoires dans le fichier 2
    zi_diff = zi1 - zi2

    indice_global_cyclogenese_diff = indice_global_cyclogenese(zi_diff, lonmin, lonmax, latmin, latmax)
    print(f"RMSE pour {file1} - {file2} : {indice_global_cyclogenese_diff:.2f}")
    print(f"Nombre de points de cyclogenèse pour {file1} : {npts1}")
    print(f"Nombre de points de cyclogenèse pour {file2} : {npts2}")
    print(f"Années couvertes : {yearmin} à {yearmax}")
    print(f'seuil vorticité : {seuil_vort}, seuil de vent : {seuil_vent}')

    with open(nom_fichier, 'a') as fichier:
#        fichier.write(f"seuil vort: {seuil_vort} | seuil vent: {seuil_vent} | RMSE: {indice_global_cyclogenese_diff:.2f} | Npts {file1}: {npts1} | Npts {file2}: {npts2}\n")
        fichier.write(f"{seuil_vort}, {seuil_vent}, {indice_global_cyclogenese_diff:.2f}, {npts1}, {npts2}\n")

    # --- Plotting ---
    fig = plt.figure(figsize=(12, 8))
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=-50))
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
    
    ax.coastlines(resolution='50m', linewidth=1)
    ax.gridlines(draw_labels=True, alpha=0.3)

    # Pour une différence, on utilise souvent une colormap divergente (ex: 'RdBu_r')
    # Mais si tu tiens à 'turbo', attention : elle ne montre pas bien le zéro.
    # 'RdBu_r' : Rouge = Surplus, Bleu = Déficit.
    vmax = np.max(np.abs(zi_diff))
    levels = np.linspace(-5, 5, 21)

    cf = ax.contourf(xi, yi, zi_diff, levels=levels, cmap='RdBu_r', 
                     vmin=-vmax, vmax=vmax, transform=proj, extend='both')

    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40)
    cbar.set_label(f'Différence de densité ({file1} - {file2})')

    plt.title(f'Carte Différence cyclogénèse\n{yearmin}-{yearmax} \n seuil vort = {seuil_vort}$s^{-1}$, seuil vent = {seuil_vent}$m.s^{-1}$ sur Aladin', fontsize=14)
    
    output = "difference_density.png"
    #plt.savefig(output, dpi=150, bbox_inches='tight')
    #plt.show()

if __name__ == "__main__":
    main()