import matplotlib.pyplot as plt
from func import load_data, print_stats, plot_aod_map, plot_aod_diff_map, plot_time_series, plot_time_series_multi, plot_histogram, plot_climatology_bars, plot_time_series_interactive

### code principal pour afficher les données des aérosols ###
# voir plus bas les appels

an_min = 2000
an_max = 2020

data = 'merra'  #modis aladin

if data == 'modis':
    VAR_AOD = "od550dust"
    FILE_PATH = "/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc"
elif data == 'aladin_dust':
    VAR_AOD = "od550dust"
    FILE_PATH = "/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_mensuel_1960-2024.nc"
elif data == 'aladin_aer':
        VAR_AOD = 'od550aer'
        FILE_PATH = "/home/puyf/Documents/dust_brut_1/aladin/aladin_aer_mensuel_1960-2024.nc"
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
    print_stats(aod_data, data)
    
    # Carte
    #fig_map = plot_aod_map(aod_data, data)

    # Séries temporelles
    #plot_time_series(aod_data, data)

    aod_data_merra_dust = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/merra/AOT_MERRA2_198001-202012.nc', "DUEXTTAU", an_min,an_max, JJASO=False)
    aod_data_merra_dust_mdr = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/merra/AOT_MERRA2_MDR_198001-202012.nc', "DUEXTTAU", an_min,an_max, JJASO=False)
    aod_data_merra_aer = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/merra/AOT_MERRA2_198001-202012.nc', "TOTEXTTAU", an_min,an_max, JJASO=False)
    aod_data_modis = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc', None, an_min,an_max,JJASO=False)
    aod_data_aladin_aer = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/aladin/aladin_aer_mensuel_1960-2024.nc', "od550aer", an_min,an_max,JJASO=False)
    aod_data_aladin_dust_4s = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/aladin/aladin_dust_mensuel_1960-2024.nc', 'od550dust', an_min,an_max,JJASO=False)
    aod_data_aladin_dust_3s = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/aladin/aladin_dust_3s_mensuel_1960-2024.nc.nc', 'od550dust', an_min,an_max,JJASO=False)
    aod_data_aladin_dust_3s_mdr = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/aladin/aladin_dust_MDR_mensuel_3weeks_1960_2024.nc', 'od550dust', an_min,an_max,JJASO=False)
    aod_data_aladin_dust_4s_mdr = load_data('/cnrm/mosca/USERS/puyf/stage/data/dusts/aladin/aladin_dust_mensuel_MDR_1960-2024.nc', 'od550dust', an_min,an_max,JJASO=False)

    
    plot_time_series_multi(aod_data_merra_dust, "merra_dust", color = 'blue')
    plot_time_series_multi(aod_data_merra_aer, "merra_aer", color = 'darkred')
    plot_time_series_multi(aod_data_modis, 'modis', color = 'blue')
    plot_time_series_multi(aod_data_aladin_aer, 'aladin_aer', linestyle='--')
    #plot_time_series_multi(aod_data_aladin_dust, 'aladin_dust', color = 'green')
    plot_time_series_multi(aod_data_aladin_dust_3s, 'aladin_dust_3s', linestyle='-.', color = 'red')
    plot_time_series_multi(aod_data_aladin_dust_3s_mdr, 'aladin_dust_3s_mdr', linestyle='--', color = 'purple')
    plot_time_series_multi(aod_data_merra_dust_mdr, 'merra_dust_mdr', color = 'green')
    
    # Histogramme
    plot_histogram(aod_data_aladin_aer, 'Aladin aer JJASO')

    ########################## AOD DIFF MAP A FIX #######################
    
    fig_diff = plot_aod_diff_map( 
        aod_data_aladin_aer,
        aod_data_modis,
        "ALADIN-REF", 
        "MODIS sur JJASO", 
        vlimit=0.2  # Ajuste selon l'intensité de la différence
    )
    
    fig_diff = plot_aod_diff_map( 
        aod_data_aladin_dust_4s_mdr,
        aod_data_merra_dust_mdr,
        "ALADIN-REF 4S", 
        "MERRA-2 sur JJASO", 
        vlimit=0.2  # Ajuste selon l'intensité de la différence
    )
    
    fig_diff = plot_aod_map( 
        aod_data_aladin_dust_3s,
        "aladin dust jjaso"
    )

    fig_diff = plot_aod_map( 
        aod_data_modis,
        "MODIS jjaso"
    )
    

    data_to_plot = {
        "merra_dust": (aod_data_merra_dust, 'blue', 'solid'),
        "merra_aer": (aod_data_merra_aer, 'darkred', 'solid'),
        "modis": (aod_data_modis, 'black', 'solid'),
        "aladin_aer": (aod_data_aladin_aer, 'orange', 'dash'),
        "aladin_dust": (aod_data_aladin_dust_4s, 'green', 'solid'),
        "aladin_dust_3s": (aod_data_aladin_dust_3s, 'red', 'dashdot'),
        "aladin_dust_3s_mdr": (aod_data_aladin_dust_3s_mdr, 'purple', 'dash'),
        "merra_dust_mdr": (aod_data_merra_dust_mdr, 'darkgreen', 'solid')
    }

    # graph html interrractif 
    #plot_time_series_interactive(data_to_plot, output_file="Analyse_AOD_Atlantique.html")

    dict_clim_aer = {
            "MERRA-2 Aer": aod_data_merra_aer,
            "MODIS": aod_data_modis,
            "ALADIN Aer": aod_data_aladin_aer,
        }

    dict_clim_dust = {
            "MERRA-2 Dust": aod_data_merra_dust,
            "ALADIN Dust 4s": aod_data_aladin_dust_4s,
            "ALADIN Dust 3s": aod_data_aladin_dust_3s}
        
    dict_clim_dust_mdr = {
            #"ALADIN Dust MDR 4s": aod_data_aladin_dust_4s_mdr,
            "ALADIN-REF Dust MDR": aod_data_aladin_dust_3s_mdr,
            "MERRA-2 Dust MDR": aod_data_merra_dust_mdr
        }

    # Appel graph bar histo
    #plot_climatology_bars(dict_clim_dust, title=f"Climatologie mensuelle dust ({an_min}-{an_max})")
   # plot_climatology_bars(dict_clim_aer, title=f"Climatologie mensuelle aer ({an_min}-{an_max})")
    plot_climatology_bars(dict_clim_dust_mdr, title=f"Climatologie mensuelle dust sur MDR ({an_min}-{an_max})")

    plt.show()