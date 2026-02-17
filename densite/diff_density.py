import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import sys

def get_density(filename, yearmin, yearmax, xi, yi):
    """Calcule la densité KDE pour un fichier et une période donnés sur une grille imposée."""
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'])
    
    mask = (df['date'].dt.year >= yearmin) & (df['date'].dt.year <= yearmax)
    df_f = df.loc[mask]
    
    if df_f.empty:
        return np.zeros(xi.shape), 0
    
    x, y = df_f['lon'].values, df_f['lat'].values
    
    # Calcul KDE
    k = gaussian_kde(np.vstack([x, y]))
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    
    # On normalise par le nombre de points pour que la différence soit comparable
    # ou on garde le scaling original (ici conservé : nb_points / 4 * 25)
    zi = zi.reshape(xi.shape) * (len(x) / 4 * 25)
    return zi, len(x)

def main():
    
    file1 = 'ALADIN_rel10_1960_2024.csv'
    file2 = 'ibtracs_transformed_1960_2024.csv'

    yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
    yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else 2022 

    # --- Configuration de la grille commune ---
    lonmin, lonmax, latmin, latmax = -105, 5, 5, 35
    xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]

    # --- Calcul des deux densités ---
    print(f"Calcul de la densité pour {file1}...")
    zi1, n1 = get_density(file1, yearmin, yearmax, xi, yi)
    
    print(f"Calcul de la densité pour {file2}...")
    zi2, n2 = get_density(file2, yearmin, yearmax, xi, yi)

    # --- Calcul de la DIFFÉRENCE ---
    # zi_diff > 0 : Plus de trajectoires dans le fichier 1
    # zi_diff < 0 : Plus de trajectoires dans le fichier 2
    zi_diff = zi1 - zi2

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
    cf = ax.contourf(xi, yi, zi_diff, levels=31, cmap='RdBu_r', 
                     vmin=-vmax, vmax=vmax, transform=proj, extend='both')

    cbar = plt.colorbar(cf, orientation='horizontal', pad=0.1, aspect=40)
    cbar.set_label(f'Différence de densité ({file1} - {file2})')

    plt.title(f'Carte Différentielle ALADIN\n{yearmin}-{yearmax}', fontsize=14)
    
    output = "difference_density.png"
    #plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Carte de différence sauvegardée : {output}")
    plt.show()

if __name__ == "__main__":
    main()