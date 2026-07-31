import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
from func import get_density, indice_global_cyclogenese

# --- Fonction utilitaire pour gérer les listes d'années ---
def get_density_for_year_list(file, years_list, xi, yi, svent=26, spress=1005):
    """Calcule la densité annuelle moyenne pour une liste d'années données."""
    zi_list = []
    for yr in years_list:
        # On appelle ta fonction d'origine année par année
        zi, _, _, _ = get_density(file, yr, yr, xi, yi, svent=svent, spress=spress)
        zi_list.append(zi)
    
    # On renvoie la moyenne temporelle de la densité
    return np.mean(zi_list, axis=0)


# --- 1. FONCTION : Carte de densité pour UNE période (Liste d'années) ---
def plot_cyclone_density(xi, yi, zi, lonmin, lonmax, latmin, latmax, title_text):
    """Affiche la densité de trajectoires avec isolignes et police 21."""
    font_size = 21
    fig = plt.figure(figsize=(14, 9))
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=-50))
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
    
    ax.coastlines(resolution='50m', linewidth=1)
    
    # Configuration des lignes de repère et de leur police
    gl = ax.gridlines(draw_labels=True, alpha=0.3, linestyle='--')
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = {'size': font_size}
    gl.ylabel_style = {'size': font_size}

    # Tracé du fond (contourf)
    vmax = np.max(zi) if np.max(zi) > 0 else 1
    levels = np.linspace(0, 2, 21)
    cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='both')
    
    # Ajout des isolignes (contour)
    cs = ax.contour(xi, yi, zi, levels=levels[::2], colors='black', linewidths=0.8, alpha=0.5, transform=proj)
    ax.clabel(cs, inline=True, fontsize=font_size - 7, fmt='%1.1f')

    # Colorbar
    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40, ax=ax)
    cbar.set_label('Densité de trajectoires cycloniques', fontsize=font_size)
    cbar.ax.tick_params(labelsize=font_size - 2)

    plt.title(title_text, fontsize=font_size, pad=15, fontweight='bold')
    plt.tight_layout()
    return fig


# --- 2. FONCTION : Carte de DIFFÉRENCE entre deux périodes ---
def plot_cyclone_density_difference(xi, yi, zi_diff, lonmin, lonmax, latmin, latmax, title_text, label_cbar):
    """Affiche la différence de densité avec une palette divergente, isolignes et police 21."""
    font_size = 21
    fig = plt.figure(figsize=(14, 9))
    proj = ccrs.PlateCarree()
    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=-50))
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)
    
    ax.coastlines(resolution='50m', linewidth=1)
    
    gl = ax.gridlines(draw_labels=True, alpha=0.3, linestyle='--')
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = {'size': font_size}
    gl.ylabel_style = {'size': font_size}

    # Palette divergente centrée sur 0 pour les différences
    vmax = np.max(np.abs(zi_diff)) if np.max(np.abs(zi_diff)) > 0 else 1
    levels = np.linspace(-vmax, vmax, 21)

    cf = ax.contourf(xi, yi, zi_diff, levels=levels, cmap='RdBu_r', transform=proj, extend='both')
    
    # Isolignes de la différence
    cs = ax.contour(xi, yi, zi_diff, levels=levels[::2], colors='black', linewidths=0.8, alpha=0.6, transform=proj)
    ax.clabel(cs, inline=True, fontsize=font_size - 7, fmt='%1.1f')

    # Colorbar
    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40, ax=ax)
    cbar.set_label(label_cbar, fontsize=font_size)
    cbar.ax.tick_params(labelsize=font_size - 2)

    plt.title(title_text, fontsize=font_size, pad=15, fontweight='bold')
    plt.tight_layout()
    return fig


# --- Exécution principale ---
def main():
    file = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
    #file1 = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv'

    # --- 1. Définition des listes d'années personnalisées ---
    # Tu peux remplacer ces listes par les années issues de tes classements (ex: fortes vs faibles)
    annees_fort_AOD_top10 = [1970,1978,1994,1962,1966,1964,1967,2016, 2001, 2007] 
    annees_faible_AOD_top10 = [1987,1996,1972,1997,1989,1992,1973,1975,2011,1965]

    annees_fort_AOD= [1970,1978,1994]
    annees_faible_AOD = [1987,1996,1972]

    # --- Configuration de la grille commune ---
    lonmin, lonmax, latmin, latmax = -105, 5, 5, 30
    xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]

    # --- 2. Calcul des densités moyennes pour chaque liste d'années ---
    print(f"Calcul de la densité moyenne pour la Liste 1...")
    zi_periode1 = get_density_for_year_list(file, annees_fort_AOD, xi, yi, svent=26, spress=1005)
    
    print(f"Calcul de la densité moyenne pour la Liste 2...")
    zi_periode2 = get_density_for_year_list(file, annees_faible_AOD, xi, yi, svent=26, spress=1005)

    # --- 3. Génération des graphiques ---
    
    # Graphique A : Visualisation simple de la Période 1
    str_years1 = ", ".join(map(str, sorted(annees_fort_AOD)[:3])) + "..." # Version courte pour le titre
    plot_cyclone_density(
        xi, yi, zi_periode1, lonmin, lonmax, latmin, latmax, 
        title_text=f"Densité Moyenne - forts AOD ({str_years1})"
    )
    plt.show()

    plot_cyclone_density(
        xi, yi, zi_periode2, lonmin, lonmax, latmin, latmax, 
        title_text=f"Densité Moyenne - faibles AOD "
    )
    plt.show()

    # Graphique B : Visualisation de la DIFFÉRENCE (Liste 1 - Liste 2)
    zi_diff = zi_periode1 - zi_periode2
    
    # Calcul cosmétique de l'indice de cyclogénèse sur la différence
    indice_diff = indice_global_cyclogenese(zi_diff, lonmin, lonmax, latmin, latmax)
    print(f"Indice global de cyclogenèse (différence) : {indice_diff:.2f}")

    plot_cyclone_density_difference(
        xi, yi, zi_diff, lonmin, lonmax, latmin, latmax,
        title_text=f"Différence de Densité Cyclonique\n Années à forts AOD − Années à faibles AOD (3ans)",
        label_cbar=f"Δ Densité de trajectoires cycloniques (forts AOD - faibles AOD)"
    )
    plt.show()

if __name__ == "__main__":
    main()