import matplotlib.pyplot as plt
from func import load_data, print_stats, plot_aod_map, plot_time_series, plot_time_series_multi, plot_histogram


an_min = 2002
an_max = 2010

data = 'modis'  #modis aladin

if data == 'modis':
    VAR_AOD = "od550dust"
    FILE_PATH = "/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc"
elif data == 'aladin_dust':
    VAR_AOD = "od550dust"
    FILE_PATH = "/home/puyf/Documents/dust_brut_1/aladin/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc"
elif data == 'aladin_aer':
        VAR_AOD = 'od550aer'
        FILE_PATH = "/home/puyf/Documents/dust_brut_1/aladin/od550aer_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc"
elif data == 'merra':
    FILE_PATH = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'
    VAR_AOD = "DUEXTTAU"



# --- EXÉCUTION DU SCRIPT ---
if __name__ == "__main__":
    # Chargement
    if data  == 'aladin_dust' or data == 'aladin_aer':
        aod_data = load_data(FILE_PATH, VAR_AOD, an_min, an_max)
    elif data == 'merra':
        aod_data = load_data(FILE_PATH, VAR_AOD, an_min, an_max)
    else:
        aod_data = load_data(FILE_PATH, None, an_min, an_max)
    
    # Stats
    #print_stats(aod_data, data)
    
    # Carte (la fonction retourne l'objet fig si tu veux le sauvegarder plus tard)
    fig_map = plot_aod_map(aod_data, data)
    
    # Séries temporelles
    #plot_time_series(aod_data, data)

    aod_data_1 = load_data('/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc', "DUEXTTAU", an_min,an_max)
    aod_data_2 = load_data('/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc', None, an_min,an_max)
    aod_data_3 = load_data('/home/puyf/Documents/dust_brut_1/aladin/od550aer_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc', "od550aer", an_min,an_max)
    aod_data_4 = load_data('/home/puyf/Documents/dust_brut_1/aladin/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc', 'od550dust', an_min,an_max)

    #plot_time_series_multi(aod_data_1, "merra")
    #plot_time_series_multi(aod_data_2, 'medis')
    #plot_time_series_multi(aod_data_3, 'aladin_dust')
    #plot_time_series_multi(aod_data_4, 'aladin_aer')

    # Histogramme
    plot_histogram(aod_data, data)
    
    
    plt.show()