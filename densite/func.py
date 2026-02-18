import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import csv
import sys


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
    return zi,x,y, len(x)


def get_density_cyclogenese(filename, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vort):
    print(f"--- Extraction des points de cyclogenèse (step=1) dans {filename} ---")

    lons = []
    lats = []
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        nbr = 0
        for row in reader: 
        ### magouille avec nbr pour prendre que premier pt avec vort > seuil_vort pour chaque cyclone
            if float(row['step']) == 1 :
                nbr = 0
            year = int(row['date'][:4])
            if yearmin <= year <= yearmax and float(row['vomax']) > seuil_vort and nbr == 0: #and row['step'] == '1':
                nbr += 1
                lons.append(float(row['lon']))
                lats.append(float(row['lat']))

    x = np.array(lons)
    y = np.array(lats)

    if len(x) < 10:
        print("Erreur : Pas assez de points trouvés.")
        sys.exit()

    # --- 3. Calcul de la densité (KDE) ---

    xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]
    coords = np.vstack([xi.flatten(), yi.flatten()])

    k = gaussian_kde(np.vstack([x, y]))
    zi = k(coords)
    zi = zi.reshape(xi.shape) * (len(x) / 4 * 25)
    
    return zi, x, y, xi, yi, len(x)