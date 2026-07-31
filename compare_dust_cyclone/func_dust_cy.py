import xarray as xr
import matplotlib.pyplot as plt
import csv
from datetime import datetime
import numpy as np


def mask_time(da, year_min, year_max, juin_oct=False):
    """Masque les données sur la plage d'années ET optionnellement sur les mois."""
    if "time" not in da.dims:
        print("Attention : La variable n'a pas de dimension temporelle.")
        return da
    
    # Masque pour les années
    mask = (da.time.dt.year >= year_min) & (da.time.dt.year <= year_max)
    
    # Masque additionnel pour les mois (ne pas écraser, mais ajouter)
    if juin_oct:
        mask = mask & (da.time.dt.month >= 6) & (da.time.dt.month <= 8) ################################################## JJA DCP ################""
        
    return da.where(mask, drop=True)

def mask_atlantic_seuils(da):
    """
    Applique un masque sur une grille 2D (curvilinéaire).
    """
    lat_min, lat_max = 5, 35
    lon_min, lon_max = -105, 5
 
    mask = (da.lat >= lat_min) & (da.lat <= lat_max) & (da.lon >= lon_min) & (da.lon <= lon_max)
    
    # .where(mask, drop=True) masque valeurs hors zone ET 
    da_masked = da.where(mask, drop=True)
    
    return da_masked



def load_data(path, var_name, ymin, ymax, juin_oct=False):
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

    aod_masked = mask_atlantic_seuils(da)
    
    # 3. Application du masque temporel
    aod_masked = mask_time(aod_masked, ymin, ymax, juin_oct)

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
    plt.ylim(0, 0.35)
    plt.grid(True, alpha=0.3)
    
    # 4. Activation de la légende
    plt.legend()
    plt.tight_layout()


import csv
import matplotlib.pyplot as plt
from datetime import datetime

def nbr_cyclones_an(chemin_csv, annee_min, annee_max, juin_oct_uniquement=True, label="Nombre de cyclones", svent=26):
    """
    Compte le nombre de cyclones par an et trace un diagramme à barres.
    """
    # 1. Préparation du stockage (un ensemble par année pour éviter les doublons d'ID)
    cyclones_par_an = {an: set() for an in range(annee_min, annee_max + 1)}
    
    lat_min, lat_max, lon_min, lon_max = 10, 20, -80, -20

    # 2. Lecture et comptage
    with open(chemin_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_obj = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
            annee, mois, id_tc = date_obj.year, date_obj.month, row['numtc']
            lat, lon = float(row['lat']), float(row['lon'])

            # Filtre temporel (années)
            if annee_min <= annee <= annee_max:
                # Filtre saisonnier (Juin à Octobre)
                if juin_oct_uniquement and not (6 <= mois <= 10):
                    continue  # On passe à la ligne suivante si on est hors saison
                # Filtre géographique
                #if (lat_min <= lat <= lat_max) and (lon_min <= lon <= lon_max):
                if lat>= 30 :
                    continue
                if float(row['vmax'])>=svent and float(row['pmin'])<=1005:
                    cyclones_par_an[annee].add(id_tc)
                

    # 3. Préparation des données pour le graphique
    annees = sorted(cyclones_par_an.keys())
    counts = [len(cyclones_par_an[an]) for an in annees]

    # 4. Tracé du diagramme à barres
    ax1 = plt.gca()
    
    # On utilise .bar au lieu de .plot
    # width=0.6 pour laisser un peu d'espace entre les barres
    ax1.bar(annees, counts, color='blue', alpha=0.5, label=label, width=0.6)
    
    # Configuration de l'axe
    ax1.set_ylabel("Nombre de cyclones (par an)", fontweight='bold')
    # On ajuste le max pour que les barres ne touchent pas le haut du cadre
    ax1.set_ylim(0, max(counts) + 2 if counts else 10)
    
    # Positionnement de la légende
    ax1.legend(loc='upper left')
    print(sum(counts))
    return annees, counts

def nbr_cyclones_mois(chemin_csv, annee_min, annee_max, juin_oct_uniquement=True, label="Nombre de cyclones"):
    """
    Renvoie la liste des cyclones par mois et trace les points sur le graphique actuel.
    """
    donnees_temp = {}
    lat_min, lat_max, lon_min, lon_max = 10, 20, -80, -20,
    # 1. Lecture et comptage (sans pandas)
    with open(chemin_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_obj = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
            annee, mois, id_tc = date_obj.year, date_obj.month, row['numtc']
            lat, lon = float(row['lat']), float(row['lon'])

            if annee_min <= annee <= annee_max:
                if juin_oct_uniquement and not (6 <= mois <= 10):
                    if (lat_min <= lat <= lat_max) and (lon_min <= lon <= lon_max):
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
    ax2.set_ylim(0, 10)
    
    # Fusion des légendes (optionnel mais propre)
    ax2.legend(loc='upper left')
    
    #return liste_counts


def get_cyclone_climatology(file_path, year_min, year_max, ALADIN=False):
    """Calcule le nombre moyen de cyclones par mois et le nombre total unique."""
    # Dictionnaire de sets pour stocker les IDs uniques (année, num_tc) par mois
    monthly_unique_tcs = {m: set() for m in range(1, 13)}
    # Set global pour compter chaque cyclone unique sur toute la période
    all_tcs = set() 
    
    num_years = year_max - year_min + 1

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                dt = datetime.strptime(row['date'].strip()[:10], '%Y-%m-%d')
            except ValueError:
                dt = datetime.strptime(row['date'].strip()[:8], '%Y%m%d')

            if year_min <= dt.year <= year_max:
                # Logique de filtrage (Vmax > 26 m/s pour ALADIN par exemple)
                is_valid = False
                if float(row['lat']) < 29 :
                    if ALADIN:
                        if float(row['vmax']) > 26 and float(row['pmin'])<1005:
                            is_valid = True
                    else:
                        is_valid = True

                    if is_valid:
                        tc_id = (dt.year, row['numtc'])
                        monthly_unique_tcs[dt.month].add(tc_id)
                        all_tcs.add(tc_id)

    # Conversion en moyenne par année pour chaque mois
    clim_counts = [len(monthly_unique_tcs[m]) / num_years for m in range(1, 13)]
    # Nombre total de cyclones uniques sur la période
    total_cyclones = len(all_tcs)
    
    return clim_counts, total_cyclones



def get_aod_climatology_xr(da):
    """Calcule la moyenne mensuelle spatiale puis temporelle."""
    # 1. Moyenne spatiale (lat/lon ou x/y selon le modèle)
    spatial_dims = [d for d in da.dims if d != 'time']
    da_spatial_mean = da.mean(dim=spatial_dims)
    
    # 2. Moyenne par mois (Climatologie)
    # Renvoie un DataArray de taille 12
    return da_spatial_mean.groupby('time.month').mean(dim='time')

def plot_climatology(aod_clim, cy_counts, title):
    months = list(range(1, 13))
    month_names = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Axe gauche : Cyclones (Barres)
    ax1.bar(months, cy_counts, color='steelblue', alpha=0.4, label='Nombre moyen cyclones')
    ax1.set_ylabel('Fréquence (nb/an)', color='steelblue')
    ax1.set_xticks(months)
    ax1.set_xticklabels(month_names)

    # Axe droit : AOD (Ligne)
    ax2 = ax1.twinx()
    ax2.plot(months, aod_clim.values, color='darkorange', marker='s', linewidth=2, label='AOD')
    ax2.set_ylabel('AOD (moyenne)', color='darkorange')

    plt.title(title)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    fig.tight_layout()


def plot_combined_climatology(aod_obs, cy_obs, aod_sim, cy_sim, year_min, year_max):
    months = np.arange(1, 13)
    month_names = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    width = 0.35  # Largeur des barres

    fig, ax1 = plt.subplots(figsize=(12, 7))

    # --- AXE 1 : CYCLONES (BARRES) ---
    # On décale les barres de l'observation à gauche et ALADIN à droite
    rects1 = ax1.bar(months - width/2, cy_obs, width, color='steelblue', alpha=0.6, label='Cyclones (IBTrACS)')
    rects2 = ax1.bar(months + width/2, cy_sim, width, color='indianred', alpha=0.6, label='Cyclones (ALADIN)')
    
    ax1.set_xlabel('Mois')
    ax1.set_ylabel('Nombre moyen de cyclones', color='black', fontsize=12)
    ax1.set_xticks(months)
    ax1.set_xticklabels(month_names)
    ax1.set_ylim(0, max(max(cy_obs), max(cy_sim)) * 1.2) # Marge en haut

    # --- AXE 2 : AOD (LIGNES) ---


    ax2 = ax1.twinx()
    line1 = ax2.plot(months, aod_obs.values, color='blue', marker='o', linewidth=2, 
                    label='AOD (MERRA)', linestyle='-')
    line2 = ax2.plot(months, aod_sim.values, color='red', marker='s', linewidth=2, 
                    label='AOD (ALADIN Dust)', linestyle='--')
    
    ax2.set_ylabel('Aerosol Optical Depth (AOD)', color='black', fontsize=12)
    # On synchronise les limites de l'AOD pour que la comparaison soit juste
    max_aod = max(float(aod_obs.max()), float(aod_sim.max()))
    ax2.set_ylim(0, max_aod * 1.2)

    # --- ESTHÉTIQUE ET LÉGENDE ---
    plt.title(f"Climatologie mensuelle AOD & nbr cyclones, OBS vs ALADIN ({year_min}-{year_max})", fontsize=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Fusion des légendes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left', ncol=2)

    fig.tight_layout()


import csv
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def plot_cyclones_vs_aod(da, chemin_csv, annee_min, annee_max,jjaso=True, label=""):
    """
    Ajoute un nuage de points (AOD vs Nb Cyclones) au graphique actuel.
    """
    # --- 1. Paramètres MDR ---
    lat_min, lat_max = 10, 20
    lon_min, lon_max = -80, -20
    mois_jjaso = [6, 7, 8, 9, 10]

    # --- 2. Calcul de l'AOD moyen annuel (Zone MDR) ---
    dims_spatiales = ["x", "y"] if "x" in da.dims else ["lat", "lon"]
    
    # Tentative de sélection spatiale si les coordonnées lat/lon existent
    try:
        if "lat" in da.coords:
            da_mdr = da.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))
        else:
            da_mdr = da
    except:
        da_mdr = da
    
    da_mdr = da
    # Moyenne annuelle (JJASO est normalement déjà filtré par load_data)
    aod_annuel = da_mdr.mean(dim=dims_spatiales).groupby('time.year').mean()
    annees_communes = aod_annuel.year.values
    valeurs_aod = aod_annuel.values

    # --- 3. Comptage des cyclones (Genèse MDR + JJASO) ---
    counts_par_an = {an: 0 for an in annees_communes}
    
    with open(chemin_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Filtrage strict sur le point de formation (step 1)
                if row['step'].strip() == '1':
                    date_obj = datetime.strptime(row['date'].strip(), '%Y-%m-%d %H:%M:%S')
                    an, mois = date_obj.year, date_obj.month
                    lat, lon = float(row['lat']), float(row['lon'])

                    if annee_min <= an <= annee_max:
                        #if mois in mois_jjaso and jjaso:##################################################################################
                            #if (lat_min <= lat <= lat_max) and (lon_min <= lon <= lon_max):
                        if an in counts_par_an:
                            counts_par_an[an] += 1
            except (ValueError, KeyError):
                continue

    liste_counts = [counts_par_an[an] for an in annees_communes]

    # --- 4. Tracé sur l'axe courant ---
    ax = plt.gca()
    # Scatter plot (les points)
    p = ax.scatter(valeurs_aod, liste_counts, alpha=0.7, edgecolors='w', label=label)
    color = p.get_facecolor()[0] # Récupère la couleur auto-assignée pour la courbe de tendance

    # Ajout de la droite de tendance
    if len(valeurs_aod) > 1:
        m, b = np.polyfit(valeurs_aod, liste_counts, 1)
        ax.plot(valeurs_aod, m*valeurs_aod + b, color=color, linestyle='--', alpha=0.8)
        
        # Calcul Corrélation
        corr = np.corrcoef(valeurs_aod, liste_counts)[0, 1]
        print(f"[{label}] Corrélation R = {corr:.3f}")

    # Configuration esthétique (ne s'applique qu'une fois)
    ax.set_xlabel("AOD moyen (JJASO) - MDR", fontweight='bold')
    ax.set_ylabel("Nombre de cyclones par an (Genèse MDR)", fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend()