import csv
import matplotlib.pyplot as plt


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

def load_data(filename):
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
    
    axs[0].hist(vmax, bins=30, color='skyblue', edgecolor='black')
    axs[0].set_title("Distribution Vmax")
    
    axs[1].hist(pmin, bins=30, color='salmon', edgecolor='black')
    axs[1].set_title("Distribution Pmin")
    
    axs[2].hist(vomax, bins=30, color='lightgreen', edgecolor='black')
    axs[2].set_title("Distribution Vomax")
    
    plt.tight_layout()
    plt.title(f"Distributions des Variables pour data {filename}")
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
        x_reg = [min(x), max(x)]
        y_reg = [a * xi + b for xi in x_reg]
        plt.plot(x_reg, y_reg, color='red', linewidth=2, label=f"Régression: y={a:.2f}x+{b:.2f}")
    
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.title(f"Relation {label_x} vs {label_y} pour data {filename}")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()