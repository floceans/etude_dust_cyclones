import matplotlib.pyplot as plt
from func import load_data, print_stats, plot_aod_map, plot_time_series, plot_histogram

data = 'aladin' #modis

if data == 'modis':
    FILE_PATH = "/home/puyf/Documents/git/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc"
elif data== 'aladin':
    FILE_PATH = "/home/puyf/Documents/dust_brut_1/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_202101-202312.nc"

VAR_AOD = "od550dust"

# --- EXÉCUTION DU SCRIPT ---
if __name__ == "__main__":
    # Chargement
    if data  == 'aladin':
        aod_data = load_data(FILE_PATH, var_name=VAR_AOD)
    else:
        aod_data = load_data(FILE_PATH)
    
    # Stats
    print_stats(aod_data, data)
    
    # Carte (la fonction retourne l'objet fig si tu veux le sauvegarder plus tard)
    fig_map = plot_aod_map(aod_data, data)
    
    # Séries temporelles
    plot_time_series(aod_data, data)
    
    # Histogramme
    plot_histogram(aod_data, data)
    
    plt.show()