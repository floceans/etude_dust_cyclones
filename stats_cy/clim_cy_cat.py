import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from fonc import get_cyclone_category_climatology

YEAR_MIN, YEAR_MAX = 1960, 2000
aladin_ref = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
ibtracs = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ibtracs_transformed_1960_2024.csv'
aladin_ref_filtered = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_REF_filtered_vmax26.csv'

categories = ['TS', '1', '2', '3', '4', '5']
month_names = ['J', 'J', 'A', 'S', 'O', 'N']

def filter_vmax_observations(input_csv, output_csv, threshold=26):
    if not os.path.exists(input_csv): return False
    df = pd.read_csv(input_csv)
    
    col_id = 'numtc' 
    col_vmax = 'vmax'

    # OPTION 1 : On ne garde que les lignes où le vent > 26m/s
    # Cela retire les phases de genèse/dissipation faibles
    df_filtered = df[df[col_vmax] > threshold].copy()
    
    if df_filtered.empty:
        print(f"ATTENTION : Aucun point trouvé avec {col_vmax} > {threshold}")
        return False

    df_filtered.to_csv(output_csv, index=False)
    print(f"Filtrage : {len(df_filtered)} points conservés sur {len(df)}.")
    return True

def plot_jjason_comparison(all_ref, all_norad):
    fig, axes = plt.subplots(2, 3, figsize=(22, 14), sharey=True)
    axes = axes.flatten()
    x = np.arange(len(month_names))
    width = 0.35
    FS = 21 

    for i, cat in enumerate(categories):
        ax = axes[i]
        # On s'assure d'avoir des données pour les indices 5 à 10
        ref_vals = all_ref[cat][5:11] if cat in all_ref else [0]*6
        norad_vals = all_norad[cat][5:11] if cat in all_norad else [0]*6

        ax.bar(x - width/2, norad_vals, width, color='indianred', label='ibtracs')
        ax.bar(x + width/2, ref_vals, width, color='steelblue', label='ALADIN Ref')

        ax.set_title(f"Catégorie {cat}", fontweight='bold', fontsize=FS)
        ax.set_xticks(x)
        ax.set_xticklabels(month_names, fontsize=FS)
        ax.tick_params(axis='y', labelsize=FS)
        if i >= 3: ax.set_xlabel("Mois", fontsize=FS)
        if i % 3 == 0: ax.set_ylabel("Nb moyen / an", fontsize=FS)
        if i == 0: ax.legend(fontsize=FS)
        ax.grid(axis='y', linestyle='--', alpha=0.3)

    plt.suptitle(f"Climatologie JJASON ({YEAR_MIN}-{YEAR_MAX})\nPoints REF avec Vmax > 26 m/s", 
                 fontsize=FS + 4, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if filter_vmax_observations(aladin_ref, aladin_ref_filtered, threshold=26):
        dict_ref, dict_norad = {}, {}
        for cat in categories:
            clim_ref, _ = get_cyclone_category_climatology(aladin_ref_filtered, YEAR_MIN, YEAR_MAX, cat, ALADIN=True)
            clim_norad, _ = get_cyclone_category_climatology(ibtracs, YEAR_MIN, YEAR_MAX, cat, ALADIN=True)
            dict_ref[cat] = clim_ref
            dict_norad[cat] = clim_norad
        plot_jjason_comparison(dict_ref, dict_norad)