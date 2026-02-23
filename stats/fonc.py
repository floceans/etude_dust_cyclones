import csv
import matplotlib.pyplot as plt
from datetime import datetime


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

def load_data(filename, svort):
    """Charge et filtre les données sans pandas."""
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
                    print(svort)
                    if vomax >= svort :
                        print("vomaaax = ", vomax)
                        vmax_list.append(vmax)
                        pmin_list.append(pmin)
                        vomax_list.append(vomax)
            except ValueError:
                continue # Ignore les lignes mal formées
                
    return vmax_list, pmin_list, vomax_list

def plot_bar_charts(vmax, pmin, vomax, filename):
    """Trace les distributions sous forme de diagrammes bâtons (Histogrammes)."""
    if not vmax: return
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    
    # Premier subplot
    axs[0].hist(vmax, bins=30, color='skyblue', edgecolor='black')
    axs[0].set_title("Distribution Vmax")
    axs[0].set_xlim(0, 100)
    #axs[0].set_ylim(0, 1800)

    # Deuxième subplot
    axs[1].hist(pmin, bins=30, color='salmon', edgecolor='black')
    axs[1].set_title("Distribution Pmin")
    axs[1].set_xlim(800, 1020)
    #axs[1].set_ylim(0, 2600)

    # Troisième subplot
    axs[2].hist(vomax, bins=30, color='lightgreen', edgecolor='black')
    axs[2].set_title("Distribution Vomax")
    axs[2].set_xlim(0, 500)
    #axs[2].set_ylim(0, 2600)

    plt.tight_layout()
    plt.show()

def plot_relation(x, y, label_x, label_y, filename):
    """Génère le nuage de points et la droite de régression."""
    if not x or not y: 
        print(f"Pas de données pour la relation {label_x}/{label_y}")
        return
        
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, alpha=0.1, s=10, label="Données")
    
    a, b = calculate_regression(x, y)
    if a is not None:
        # Création de la ligne de régression
        x_reg = [min(x), max(x)+20]
        y_reg = [a * xi + b for xi in x_reg]
        plt.plot(x_reg, y_reg, color='red', linewidth=2, label=f"Régression: y={a:.2f}x+{b:.2f}")
    
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(f"Relation {label_x} vs {label_y} pour data {filename}")
    plt.xlim(880, 1030)
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()



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