import csv
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from matplotlib.ticker import ScalarFormatter

def calculate_regression(x, y):
    """Calcule manuellement la pente et l'interception (Moindres Carrés)."""
    n = len(x)
    if n < 2: return None, None, 0
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_xx = sum(xi**2 for xi in x)
    
    # Formule de la pente (a) et de l'ordonnée à l'origine (b)
    denominator = (n * sum_xx - sum_x**2)
    if denominator == 0: return None, None, 0
    
    a = (n * sum_xy - sum_x * sum_y) / denominator
    b = (sum_y - a * sum_x) / n
    
    # Calcul simplifié du coefficient de corrélation R (optionnel pour le titre)
    return a, b

def load_data(filename, svort, spress, svent):

    vmax_list, pmin_list, vomax_list = [], [], []
    
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Récupération des valeurs
                vmax = float(row['vmax']) #if row['vmax'] else None
                pmin = float(row['pmin']) #if row['pmin'] else None
                vomax = float(row['vomax']) #if row['vomax'] else None
                
                # Application de vos filtres :
                # 1. Si pmin est absent (vide), on ignore la ligne.
                # 2. Si vomax est égal à 0, on ignore la ligne.
                if pmin is not None and vomax is not None : #and vomax != 0:
                    if vomax >= svort and pmin<spress and vmax>svent:
                        vmax_list.append(vmax)
                        pmin_list.append(pmin)
                        vomax_list.append(vomax)
            except ValueError:
                continue # Ignore les lignes mal formées
                
    return vmax_list, pmin_list, vomax_list

import csv



def load_data_max(filename, seuil_vent, seuil_pression):
    """
    Détecte un nouveau cyclone chaque fois que 'step' revient à 1.
    Garde uniquement le pic d'intensité par cyclone.
    """
    vmax_final, pmin_final = [], []
    
    # Variables temporaires pour le cyclone en cours de lecture
    current_vmax = -1.0
    current_pmin = 2000.0 # Valeur arbitraire haute
    is_first_row = True

    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                step = int(row['step'])
                v = float(row['vmax'])
                p = float(row['pmin'])

                # Détection d'un nouveau cyclone
                if step == 1:
                    # Si ce n'est pas la toute première ligne du fichier, 
                    # on enregistre le cyclone qui vient de se terminer
                    if not is_first_row:
                        if current_vmax > seuil_vent and current_pmin < seuil_pression and current_pmin > 100 :
                            vmax_final.append(current_vmax)
                            pmin_final.append(current_pmin)
                    
                    # Réinitialisation pour le nouveau cyclone
                    current_vmax = v
                    current_pmin = p
                    is_first_row = False
                else:
                    # On est au sein du même cyclone, on met à jour les records
                    if v > current_vmax: current_vmax = v
                    if p < current_pmin: current_pmin = p
                        
            except (ValueError, KeyError):
                continue

        # Très important : on n'oublie pas d'ajouter le dernier cyclone 
        # après la sortie de la boucle loop
        if not is_first_row:
            if current_vmax > seuil_vent and current_pmin < seuil_pression:
                vmax_final.append(current_vmax)
                pmin_final.append(current_pmin)

    return vmax_final, pmin_final


def plot_bar_charts(vmax, pmin, vomax, filename):
    """Trace les distributions sous forme de diagrammes bâtons (Histogrammes)."""
    if not vmax: return
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    
    # Premier subplot
    axs[0].hist(vmax, bins=30, color='skyblue', edgecolor='black')
    axs[0].set_title("Distribution Vmax")
    axs[0].set_xlim(0, 100)
    axs[0].set_ylim(0, 2500)

    # Deuxième subplot
    axs[1].hist(pmin, bins=30, color='salmon', edgecolor='black')
    axs[1].set_title("Distribution Pmin")
    axs[1].set_xlim(800, 1020)
    axs[1].set_ylim(0, 2500)

    # Troisième subplot
    axs[2].hist(vomax, bins=30, color='lightgreen', edgecolor='black')
    axs[2].set_title("Distribution Vomax")
    axs[2].set_xlim(0, 500)
    #axs[2].set_ylim(0, 2600)

    plt.tight_layout()
    plt.show()

import netCDF4 as nc
import os

# --- CONFIGURATION ---
# Liste des périodes à concaténer
dates_a_traiter = ["202101-202312", "202401-202612"] 
template_nom = "od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_{}.nc"
fichier_final = "od550dust_global_concatene.nc"


def plot_relation(pmin_list, vmax_list, filename, ax=None, color='teal'):
    """
    Régression : log(vmax) = log(alpha) + log((1020-pmin)^beta)
    Affichage : vmax en fonction de pmin
    """
    pmin = np.array(pmin_list)
    vmax = np.array(vmax_list)
    
    # 1. Préparation des données
    delta_p = 1020 - pmin
    mask = (delta_p > 0) & (vmax > 0)
    
    x_reg = delta_p[mask]
    y_reg_data = vmax[mask]
    pmin_plot = pmin[mask]

    if len(x_reg) < 2:
        print(f"Données insuffisantes pour {filename}.")
        return

    # 2. Régression linéaire sur les logs
    beta, log_alpha = np.polyfit(np.log(x_reg), np.log(y_reg_data), 1)
    alpha = np.exp(log_alpha)

    # 3. Gestion de l'axe (si ax est None, on crée une nouvelle figure)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Nuage de points
    ax.scatter(y_reg_data, pmin_plot, alpha=0.2, s=15, color=color, label=f"Points : {filename}")

    # Courbe de tendance
    pmin_smooth = np.linspace(pmin_plot.min(), pmin_plot.max(), 100)
    v_pred = alpha * (1020 - pmin_smooth)**beta
    
    ax.plot(v_pred, pmin_smooth, color=color, linewidth=2,
             label=f"Modèle {filename}: $V_{{max}} = {alpha:.1f} \cdot \Delta P^{{{beta:.2f}}}$")

    # 4. Cosmétique (appliquée sur l'objet ax)
    ax.set_ylabel("$P_{min}$ [hPa]")
    ax.set_xlabel("$V_{max}$ [m/s]")
    ax.set_title("Comparaison Relation Vent/Pression")
    
    # Inversion de l'axe Y (pression décroissante vers le haut)
    # On vérifie si c'est déjà inversé pour ne pas le remettre à l'endroit au 2ème appel
    if ax.get_ylim()[0] < ax.get_ylim()[1]:
        ax.invert_yaxis()

    ax.set_xlim(0, 100)
    ax.set_ylim(1020, 850)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()

    return ax # On retourne l'axe pour pouvoir le réutiliser




def plot_vmax_pmin_time(filename, an_min, an_max):
    """Trace l'évolution de Vmax et Pmin en reliant les points par cyclone."""
    
    # On utilise un dictionnaire pour grouper les points par identifiant de cyclone (numtc)
    cyclones = {}

    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                pmin_val = row['pmin']
                vmax_val = row['vmax']
               # vomax_val = row.get('vomax', '0')
                date_raw = row['date']
                numtc = row['numtc'] # L'identifiant unique du cyclone
                year = int(date_raw[:4])

                # Filtres demandés
                if pmin_val and vmax_val and (an_min <= year <= an_max) : #and float(vomax_val) != 0:
                    if numtc not in cyclones:
                        cyclones[numtc] = {'dates': [], 'vmax': [], 'pmin': []}
                    
                    dt = datetime.strptime(date_raw, '%Y-%m-%d %H:%M:%S')
                    cyclones[numtc]['dates'].append(dt)
                    cyclones[numtc]['vmax'].append(float(vmax_val))
                    cyclones[numtc]['pmin'].append(float(pmin_val))
            except (ValueError, KeyError):
                continue

    if not cyclones:
        print(f"Aucune donnée pour {an_min}-{an_max} avec les filtres (pmin présent & vomax != 0).")
        return

    fig, ax1 = plt.subplots(figsize=(14, 8))
    ax2 = ax1.twinx()

    # Paramètres esthétiques
    color_vmax = 'tab:blue'
    color_pmin = 'tab:red'

    # On trace chaque cyclone séparément
    first_label = True
    for tc_id, data in cyclones.items():
        # Tri chronologique pour chaque cyclone pour éviter les retours en arrière
        combined = sorted(zip(data['dates'], data['vmax'], data['pmin']))
        d_sort, v_sort, p_sort = zip(*combined)

        # On n'affiche la légende qu'une seule fois pour ne pas surcharger
        lbl_v = 'Vmax (Vent)' if first_label else ""
        lbl_p = 'Pmin (Pression)' if first_label else ""

        # Tracé des lignes (interpolation linéaire simple "point à point")
        ax1.plot(d_sort, v_sort, color=color_vmax, alpha=0.6, linewidth=1.2, label=lbl_v)
        ax2.plot(d_sort, p_sort, color=color_pmin, alpha=0.6, linewidth=1.2, label=lbl_p)
        first_label = False

    # Configuration des axes
    ax1.set_xlabel('Temps')
    ax1.set_ylabel('Vmax (m/s)', color=color_vmax, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color_vmax)
    
    ax2.set_ylabel('Pmin (hPa)', color=color_pmin, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_pmin)
    ax2.invert_yaxis() # Convention : pression basse en haut (intensité max)

    # Légendes fusionnées
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.title(f"Trajectoires d'intensité des cyclones ({an_min} - {an_max})\nLignes par cyclone individuel (Filtre: Vomax ≠ 0)")
    plt.grid(True, alpha=0.2)
    fig.tight_layout()
    plt.show()