import matplotlib.pyplot as plt
from func import load_data, print_stats, plot_aod_map, plot_time_series, plot_histogram

# --- CONFIGURATION ---
FILE_PATH = "/home/florent/Documents/CNRM/git/etude_dust_cyclones/aerosols/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc"



# --- EXÉCUTION DU SCRIPT ---
if __name__ == "__main__":
    # Chargement
    aod_data = load_data(FILE_PATH)
    
    # Stats
    print_stats(aod_data, "modis")
    
    # Carte (la fonction retourne l'objet fig si tu veux le sauvegarder plus tard)
    fig_map = plot_aod_map(aod_data, "modis")
    
    # Séries temporelles
    plot_time_series(aod_data, 'modis')
    
    # Histogramme
    plot_histogram(aod_data, 'modis')
    
    plt.show()