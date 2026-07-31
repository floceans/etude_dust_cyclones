import matplotlib.pyplot as plt
import numpy as np
from func import load_data, print_stats, plot_aod_map, plot_time_series, plot_histogram, plot_aod_map_years, plot_aod_diff_map_year

### PLOT AOD pour années les +/- fortes en ACE ###

# --- CONFIGURATION ---
FILE_PATH = "/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_3s_mensuel_1960-2024.nc.nc"

# On peut spécifier la variable si on veut être précis
VAR_AOD = "od550dust"

if __name__ == "__main__":
    # 1. Chargement et Masquage (la correction lon est incluse dedans)
    aod_data = load_data(FILE_PATH, var_name=VAR_AOD, an_min=1960, an_max=2000, JJASO=True)
    
    # 2. Statistiques
    print_stats(aod_data, "aladin")
    
    # 3. Visualisations
    # La carte
    plot_aod_map(aod_data, "dust aladin")

    annees_plus_intenses = np.sort([2005,1960, 2003, 1995, 1971, 1999, 1978, 2010, 1965, 2012])
    annees_moins_intenses = np.sort([1994, 1972, 2014, 1982, 1986, 1984, 1977, 1996, 1979, 1973])

    annees_plus_intenses_jjaso = np.sort([2005,1965, 2003, 2012, 1962, 2006, 1995, 1987, 2009, 1999])
    annees_moins_intenses_jjaso = np.sort([2018, 2001, 1994, 1961, 1990, 1991, 2016, 2007, 2013, 1996])

    plot_aod_map_years(aod_data, "dust aladin 10 années ACE - fortes", annees_moins_intenses_jjaso)

    plot_aod_diff_map_year(aod_data, annees_plus_intenses, aod_data, annees_moins_intenses_jjaso)
    
    # La série temporelle (moyenne mensuelle)
    #plot_time_series(aod_data, 'aladin')
    
    # L'histogramme
    #plot_histogram(aod_data, 'aladin')
    
    plt.show()