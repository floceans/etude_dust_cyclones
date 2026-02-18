import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde


# fichier source
def fichier_source(argv):
    if len(argv) > 1 and argv[1] == 'ibtracs':
        return 'ibtracs_transformed_1960_2024.csv'
    elif len(argv) > 1 and argv[1] == 'aladin':
        return 'ALADIN_rel10_1960_2024.csv'
    else:
        print('Fichier source non reconnu. Utilisez "aladin" ou "ibtracs" en argument. Par défaut : aladin.')
        return 'ALADIN_rel10_1960_2024.csv'


def indice_global_cyclogenese(zi, lonmin, lonmax, latmin, latmax):
    """
    Calcule l'intégrale discrète du champ de densité zi.
    Retourne un nombre réel représentant l'intensité globale.
    """
    nx, ny = zi.shape
    
    dx = (lonmax - lonmin) / (nx - 1)
    dy = (latmax - latmin) / (ny - 1)
    
    indice = np.sum(zi) * dx * dy
    return indice

def get_density(filename, yearmin, yearmax, xi, yi):
    # calcul densité du csv avec gaussian_kde (jsp détail formule)
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

