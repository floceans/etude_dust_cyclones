import matplotlib.pyplot as plt
import numpy as np
from fonc import get_cyclone_climatology 

# --- Configuration ---
YEAR_MIN = 1960
YEAR_MAX = 2024
FS = 21

aladin_ref = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
aladin_norad = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv'
ibtracs = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv'

# --- 1. Calcul de la climatologie (Moyenne par mois) ---
cy_clim_ibtracs = get_cyclone_climatology(ibtracs, YEAR_MIN, YEAR_MAX)
cy_clim_aladin = get_cyclone_climatology(aladin_ref, YEAR_MIN, YEAR_MAX, ALADIN=True)
cy_clim_aladin = get_cyclone_climatology(aladin_norad, YEAR_MIN, YEAR_MAX, ALADIN=True)


# --- 2. Fonction de visualisation dédiée (uniquement cyclones) ---
def plot_cyclone_only(cy_1, cy_2, ymin, ymax, total_obs, total_sim):
    """Affiche l'histogramme comparatif des cyclones uniquement."""
    months = np.arange(1, 13)
    month_names = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    width = 0.35 

    fig, ax = plt.subplots(figsize=(11, 6))

    # Barres décalées pour la comparaison
    ax.bar(months - width/2, cy_1, width, color='indianred', alpha=1, label=f'IBTrACS (Total: {total_obs})')
    ax.bar(months + width/2, cy_2, width, color='steelblue', alpha=1, label=f'ALADIN Ref (Total: {total_sim})')

    # Configuration esthétique
    ax.set_title(f"Climatologie du nombre de cyclones par mois ({ymin}-{ymax})", fontsize=FS+2, fontweight='bold')
    ax.set_ylabel("Fréquence moyenne (nb / an)", fontsize=FS)
    ax.set_xlabel("Mois", fontsize=FS-5)
    ax.set_xticks(months)
    ax.set_xticklabels(month_names, fontsize = FS)
    
    ax.legend(frameon=True, shadow=True, fontsize = FS)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.tight_layout()

# --- 2. Script Principal ---

if __name__ == "__main__":

    

    cy_clim_ibtracs, total_ib = get_cyclone_climatology(ibtracs, YEAR_MIN, YEAR_MAX)
    cy_clim_aladin_ref, total_al_ref = get_cyclone_climatology(aladin_ref, YEAR_MIN, YEAR_MAX, ALADIN=True)
    cy_clim_aladin_norad, total_al_norad = get_cyclone_climatology(aladin_norad, YEAR_MIN, YEAR_MAX, ALADIN=True)


    # Affichage des résultats en console pour contrôle
    print("-" * 30)
    print(f"Période : {YEAR_MIN} - {YEAR_MAX}")
    print(f"Nombre total de cyclones (IBTrACS) : {total_ib}")
    print(f"Nombre total de cyclones (ALADIN ref)  : {total_al_ref}")
    print(f"Nombre total de cyclones (ALADIN Norad)  : {total_al_norad}")

    print("-" * 30)

    # --- Plot ---
    #plot_cyclone_only(cy_clim_aladin_norad, cy_clim_aladin_ref, YEAR_MIN, YEAR_MAX, total_al_norad, total_al_ref)
    plot_cyclone_only(cy_clim_ibtracs, cy_clim_aladin_ref, YEAR_MIN, YEAR_MAX, total_al_norad, total_al_ref)

    plt.show()

