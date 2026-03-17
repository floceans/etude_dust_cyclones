import matplotlib.pyplot as plt
from func_dust_cy import load_data, get_aod_climatology_xr, get_cyclone_climatology, plot_climatology, plot_combined_climatology

YEAR_MIN = 1980
YEAR_MAX = 2020
juin_sept = False
file_1 = 'obs' #'aladin'

merra = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'
modis = '/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc'
aladin_dust = '/home/puyf/Documents/dust_brut_1/aladin/aladin_dust_mensuel_1960-2024.nc'
aladin_aer = '/home/puyf/Documents/dust_brut_1/aladin/aladin_aer_mensuel_1960-2024.nc'

aladin_cy = '/home/puyf/Documents/git/etude_dust_cyclones/ALADIN_rel10_1960_2024.csv'
ibtracs = '/home/puyf/Documents/git/etude_dust_cyclones/ibtracs_transformed_1960_2024.csv'


filename = 'merra - ibtracs'if file_1 == 'obs' else 'aladin'

# --- 1. Chargement des données OBS ---
aod_merra = load_data(merra, "DUEXTTAU", YEAR_MIN, YEAR_MAX, False)
aod_clim_merra = get_aod_climatology_xr(aod_merra)
cy_clim_ibtracs = get_cyclone_climatology(ibtracs, YEAR_MIN, YEAR_MAX)

# --- 2. Chargement des données ALADIN ---
aod_aladin = load_data(aladin_dust, "od550dust", YEAR_MIN, YEAR_MAX, False)
aod_clim_aladin = get_aod_climatology_xr(aod_aladin)
cy_clim_aladin = get_cyclone_climatology(aladin_cy, YEAR_MIN, YEAR_MAX)

# --- 3. Plot unique ---
plot_combined_climatology(aod_clim_merra, cy_clim_ibtracs, 
                          aod_clim_aladin, cy_clim_aladin, 
                          YEAR_MIN, YEAR_MAX)

plt.show()