import matplotlib.pyplot as plt
from func_dust_cy import load_data, get_aod_climatology_xr, get_cyclone_climatology, plot_climatology

YEAR_MIN = 1980
YEAR_MAX = 2020
juin_sept = False

merra = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'
modis = '/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc'
aladin_dust = '/home/puyf/Documents/dust_brut_1/aladin/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc'
aladin_aer = '/home/puyf/Documents/dust_brut_1/aladin/od550aer_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc'

aladin_cy = '/home/puyf/Documents/git/etude_dust_cyclones/ALADIN_rel10_1960_2024.csv'
ibtracs = '/home/puyf/Documents/git/etude_dust_cyclones/ibtracs_transformed_1960_2024.csv'

file_dust = [merra, "DUEXTTAU"]
file_cy = ibtracs

aod_merra = load_data(file_dust[0], file_dust[1], YEAR_MIN, YEAR_MAX, False)
aod_clim_merra = get_aod_climatology_xr(aod_merra)

# Cyclones (Sans pandas)
cy_clim_ibtracs = get_cyclone_climatology(file_cy, YEAR_MIN, YEAR_MAX)

# Affichage
plot_climatology(aod_clim_merra, cy_clim_ibtracs, f"Climatologie OBS ({YEAR_MIN}-{YEAR_MAX})")
plt.show()

# --- Données ALADIN ---
aod_aladin = load_data(aladin_dust, "od550dust", YEAR_MIN, YEAR_MAX, False)
aod_clim_aladin = get_aod_climatology_xr(aod_aladin)
cy_clim_aladin = get_cyclone_climatology(aladin_cy, YEAR_MIN, YEAR_MAX)

plot_climatology(aod_clim_aladin, cy_clim_aladin, f"Climatologie ALADIN ({YEAR_MIN}-{YEAR_MAX})")
plt.show()