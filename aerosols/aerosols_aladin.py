import matplotlib.pyplot as plt
from func import load_data, print_stats, plot_aod_map, plot_time_series, plot_histogram

# --- CONFIGURATION ---
FILE_PATH = "/home/florent/Documents/CNRM/git/etude_dust_cyclones/aerosols/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_202101-202312.nc"

# On peut spécifier la variable si on veut être précis
VAR_AOD = "od550dust"

if __name__ == "__main__":
    # 1. Chargement et Masquage (la correction lon est incluse dedans)
    aod_data = load_data(FILE_PATH, var_name=VAR_AOD)
    
    # 2. Statistiques
    print_stats(aod_data, "aladin")
    
    # 3. Visualisations
    # La carte
    plot_aod_map(aod_data, "aladin")
    
    # La série temporelle (moyenne mensuelle)
    plot_time_series(aod_data, 'aladin')
    
    # L'histogramme
    plot_histogram(aod_data, 'aladin')
    
    plt.show()