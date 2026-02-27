import xarray as xr
import matplotlib.pyplot as plt
import csv
from datetime import datetime

def mask_time(da, year_min=2021, year_max=2024, juin_sept=False):
    """Masque les données en dehors de la plage temporelle spécifiée."""
    if "time" not in da.dims:
        print("Attention : La variable n'a pas de dimension temporelle.")
        return da
    mask = (da.time.dt.year >= year_min) & (da.time.dt.year <= year_max)
    if juin_sept : 
        mask = (da.time.dt.month >= 6) & (da.time.dt.month <= 9)
    return da.where(mask, drop=True)

def mask_atlantic(da):
    """
    Applique un masque sur une grille 2D (curvilinéaire).
    """
    lat_min, lat_max = 5, 35
    lon_min, lon_max = -105, 5
    
    # On identifie les noms réels des coordonnées de latitude et longitude
    # Dans ton fichier ALADIN, c'est probablement 'lat' et 'lon' (ou 'latitude'/'longitude')
    # On crée un masque booléen 2D
    
    mask = (da.lat >= lat_min) & (da.lat <= lat_max) & (da.lon >= lon_min) & (da.lon <= lon_max)
    
    # .where(mask, drop=True) masque les valeurs hors zone ET 
    # réduit les dimensions x et y au plus petit rectangle englobant.

    
    da_masked = da.where(mask, drop=True)
    
    return da_masked



def load_data(path, var_name, ymin, ymax, juin_sept=False):
    """Charge le dataset et gère les coordonnées 2D d'ALADIN."""
    ds = xr.open_dataset(path)
    
    if var_name is None:
        var_name = list(ds.data_vars)[0]
    da = ds[var_name]


    # 1. Correction des longitudes (0-360 -> -180-180) AVANT le masque
    if da.lon.max() > 180:
        # Pour les grilles 2D, on modifie les valeurs directement
        new_lon = ((da.lon + 180) % 360) - 180
        da = da.assign_coords(lon=new_lon)
    
    # 2. Application du masque spécifique 2D

    aod_masked = mask_atlantic(da)
    
    # 3. Application du masque temporel
    aod_masked = mask_time(aod_masked, ymin, ymax, juin_sept)

    #aod = aod_masked - aod_masked.mean()

    return aod_masked

def plot_time_series_multi(da, filename):
    """
    Ajoute une courbe au graphique actuel. 
    Note : plt.figure() doit être appelé AVANT d'utiliser cette fonction.
    """
    

    if "time" not in da.dims: 
        print(f"Erreur : pas de dimension 'time' dans {filename}")
        return
    
    # 1. Sélection automatique des dimensions spatiales selon le nom du fichier
    if filename in ['aladin_dust', 'aladin_aer']:
        dims_to_mean = ["x", "y"]
    else:
        dims_to_mean = ["lat", "lon"]
        
    # 2. Tracé de la moyenne spatiale
    # On utilise 'label' pour que la légende s'affiche correctement
    # On ne fixe pas la couleur pour que Matplotlib change de couleur à chaque appel
    da.mean(dim=dims_to_mean).plot(label=filename, linewidth=1.5)
    
    # 3. Configuration du graphique (écrasée à chaque appel, donc seule la dernière compte)
    plt.title(f"AOD/nbr cyclones {filename} (Moyenne zone Atlantique 5-35, -105, 5)", fontweight='bold')
    #plt.ylim(0, 0.35)
    plt.grid(True, alpha=0.3)
    
    # 4. Activation de la légende
    plt.legend()
    plt.tight_layout()



def nbr_cyclones_mois(chemin_csv, annee_min, annee_max, juin_sept_uniquement=False, label="Nombre de cyclones"):
    """
    Renvoie la liste des cyclones par mois et trace les points sur le graphique actuel.
    """
    donnees_temp = {}

    # 1. Lecture et comptage (sans pandas)
    with open(chemin_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_obj = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
            annee, mois, id_tc = date_obj.year, date_obj.month, row['numtc']

            if annee_min <= annee <= annee_max:
                if juin_sept_uniquement and not (6 <= mois <= 9):
                    continue
                
                cle = (annee, mois)
                if cle not in donnees_temp:
                    donnees_temp[cle] = set()
                donnees_temp[cle].add(id_tc)

    # 2. Construction de la liste et de l'axe temporel (X)
    liste_counts = []
    dates_x = []
    
    for an in range(annee_min, annee_max + 1):
        for m in range(1, 13):
            count = len(donnees_temp.get((an, m), set()))
            liste_counts.append(count)
            # On crée un point au milieu du mois pour l'alignement
            dates_x.append(datetime(an, m, 15))
    
    #centrage data
    '''
    liste_counts_1 = []
    for k in range(len(liste_counts)):
        if liste_counts[k]>0 : liste_counts_1.append(liste_counts[k])

    for k in range(len(liste_counts_1)) : 
        liste_counts[k]-=sum(liste_counts_1) / len(liste_counts_1)
    '''
    # 3. Tracé sur le graphique
    # On utilise twinx() pour ne pas écraser l'échelle AOD (0-0.35)
    ax1 = plt.gca()
    ax2 = ax1.twinx() 
    
    # Tracé avec un point par mois ('-o' = ligne + points)
    ax2.plot(dates_x, liste_counts, '-o', color='black', markersize=4, 
             linewidth=1, label=label, alpha=0.7)
    
    # Configuration du second axe
    ax2.set_ylabel("Nombre de cyclones", fontweight='bold')
    ax2.set_ylim(0, max(liste_counts) + 1 if liste_counts else 10)
    
    # Fusion des légendes (optionnel mais propre)
    ax2.legend(loc='upper left')
    
    #return liste_counts