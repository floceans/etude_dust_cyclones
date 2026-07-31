import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import csv
import sys
from datetime import datetime


# fichier source
def fichier_source(argv, file):
    if len(argv) > 1 and argv[1] == 'ibtracs':
        return 'ibtracs_transformed_1960_2024.csv'
    elif len(argv) > 1 and argv[1] == 'aladin':
        return 'ALADIN_rel10_1960_2024.csv'
    elif file == 'aladin' :
        return 'ALADIN_rel10_1960_2024.csv'
    elif file == 'ibtracs' :
        return 'ibtracs_transformed_1960_2024.csv'


def indice_global_cyclogenese(zi, lonmin, lonmax, latmin, latmax):
    """
    Calcule l'intégrale discrète du champ de densité zi.
    Retourne un nombre réel représentant l'intensité globale.
    """
    nx, ny = zi.shape
    

    indice = np.sum(np.abs(zi)) / (nx * ny)
    return indice

def get_density(filename, yearmin, yearmax, xi, yi, svent, spress):
    # Listes pour stocker nos coordonnées filtrées
    lons = []
    lats = []

    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Extraction et conversion des données
                # On assume que les colonnes s'appellent 'date', 'vmax', 'lat', 'lon'
                dt = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S') # Ajuste le format si besoin
                vmax = float(row['vmax'])
                lat = float(row['lat'])
                lon = float(row['lon'])

                if (yearmin <= dt.year <= yearmax) and (vmax > 17) and (lat < 29)and float(row['vmax']) > svent and float(row['pmin'])<spress: ######################### filtre latitudes & vmax & temps
                    lons.append(lon)
                    lats.append(lat)
            except (ValueError, KeyError):
                # On passe les lignes mal formées ou entêtes vides
                continue


    # Conversion en tableaux numpy pour les calculs
    x = np.array(lons)
    y = np.array(lats)
    n_points = len(x)

    # Gestion du cas où aucune donnée ne correspond aux critères
    if n_points == 0:
        return np.zeros(xi.shape), x, y, 0

    # Calcul de la densité par noyau gaussien (KDE)
    # np.vstack crée une matrice 2xN
    positions = np.vstack([x, y])
    k = gaussian_kde(positions)
    
    # Évaluation sur la grille xi, yi
    grid_coords = np.vstack([xi.flatten(), yi.flatten()])
    zi = k(grid_coords)
    
    # Redimensionnement et mise à l'échelle personnalisée
    # (zi * facteur de normalisation basé sur ton code original)
    zi = zi.reshape(xi.shape) * (n_points / 4 * 25)
    
    return zi, x, y, n_points


def get_density_cyclogenese_aladin(filename, yearmin, yearmax, lonmin, lonmax, latmin, latmax, seuil_vent, seuil_press):
    #####ibtracs = True if filename == 'ibtracs_transformed_1960_2024.csv' else False

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
            if yearmin <= year <= yearmax and nbr == 0 and float(row['vmax']) > seuil_vent and float(row['pmin'])<seuil_press: #and row['step'] == '1':
                if float(row['lat']) < 29:
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
    zi = zi.reshape(xi.shape) * (len(x) /4 * 25)
    
    return zi, x, y, xi, yi, len(x)

def get_density_cyclogenese_ibtracs(filename, yearmin, yearmax, lonmin, lonmax, latmin, latmax):
    #####ibtracs = True if filename == 'ibtracs_transformed_1960_2024.csv' else False
    lons = []
    lats = []
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        nbr = 0
        for row in reader: 
            year = int(row['date'][:4])
            if yearmin <= year <= yearmax and int(row['step']) == 1:
                if float(row['lat']) < 30:
                    nbr+=1
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

    coef = len(x) / 4 * 25

    zi = zi.reshape(xi.shape) * coef

    return zi, x, y, xi, yi, len(x)