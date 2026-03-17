import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys
from func import get_density, indice_global_cyclogenese



def main():
    
    file1 = 'ALADIN_rel10_1960_2024.csv'
    file2 = 'ibtracs_transformed_1960_2024.csv'

    yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else 1960
    yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else 2024

    # --- Configuration de la grille commune ---
    lonmin, lonmax, latmin, latmax = -105, 5, 5, 30
    xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]

    # --- Calcul des deux densités ---
    print(f"Calcul de la densité pour {file1}...")
    zi1, x1, y1, long_x1 = get_density(file1, yearmin, yearmax, xi, yi)
    
    print(f"Calcul de la densité pour {file2}...")
    zi2, x2, y2, long_x2 = get_density(file2, yearmin, yearmax, xi, yi)

    # --- Calcul de la DIFFÉRENCE ---
    # zi_diff > 0 : Plus de trajectoires dans le fichier 1
    # zi_diff < 0 : Plus de trajectoires dans le fichier 2
    zi_diff = zi1 - zi2

    indice_global_cyclogenese_diff = indice_global_cyclogenese(zi_diff, lonmin, lonmax, latmin, latmax)
    print(f"Indice global de cyclogenèse (différence) pour {file1} - {file2} : {indice_global_cyclogenese_diff:.2f}")

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
    level = np.linspace(-90, 90, 19) ###################" changer pour mm echelle"

    cf = ax.contourf(xi, yi, zi_diff, levels=level, cmap='RdBu_r', 
                     vmin=-vmax, vmax=vmax, transform=proj, extend='both')
    
    cs = ax.contour(xi, yi, zi_diff, levels=level, colors='black', linewidths=0.5, alpha=0.4, transform=ccrs.PlateCarree())
    ax.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')

    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40)
    cbar.set_label(f'Différence de densité ({file1} - {file2})')

    plt.title(f'Carte Différentielle ALADIN\n{yearmin}-{yearmax}', fontsize=14)
    
    output = "difference_density.png"
    #plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Carte de différence sauvegardée : {output}")
    plt.show()

if __name__ == "__main__":
    main()