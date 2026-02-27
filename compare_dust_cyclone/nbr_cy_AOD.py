import numpy as np
import matplotlib.pyplot as plt
from func_dust_cy import load_data, plot_time_series_multi, nbr_cyclones_mois


'''
# chemin du dossier courant du script
current_dir = os.path.dirname(__file__)

# chemin vers le dossier frère
aerosols_path = os.path.abspath(os.path.join(current_dir, "../aerosols"))

sys.path.append(aerosols_path)

from func import plot_time_series_multi, load_data
'''

################## OBS -> IBTRACS + MODIS #######################


YEAR_MIN = 2003
YEAR_MAX = 2010
juin_sept = False

merra = '/home/puyf/Documents/dust_brut_1/merra/AOT_MERRA2_198001-202012.nc'
modis = '/home/puyf/Documents/dust_brut_1/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc'

aod_data_1 = load_data(merra, "DUEXTTAU", YEAR_MIN, YEAR_MAX, juin_sept)
aod_data_2 = load_data(modis, None, YEAR_MIN, YEAR_MAX,juin_sept)


#plot_time_series_multi(aod_data_1, "merra")
plot_time_series_multi(aod_data_2, 'medis')
#plot_time_series_multi(aod_data_3, 'aladin_dust')
#plot_time_series_multi(aod_data_4, 'aladin_aer')

ibtracs = '/home/puyf/Documents/git/etude_dust_cyclones/ibtracs_transformed_1960_2024.csv'

nbr_cyclones_mois(ibtracs, YEAR_MIN, YEAR_MAX, juin_sept, "Nombre de cyclones observés (ibtracs)")


plt.show()

############################## SIMU -> ALADIN ###########################################

aladin_dust = '/home/puyf/Documents/dust_brut_1/aladin/od550dust_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc'
aladin_aer = '/home/puyf/Documents/dust_brut_1/aladin/od550aer_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_200101-201012.nc'

aod_data_3 = load_data(aladin_aer, "od550aer", YEAR_MIN, YEAR_MAX,juin_sept)
aod_data_4 = load_data(aladin_dust, 'od550dust', YEAR_MIN, YEAR_MAX,juin_sept)

plot_time_series_multi(aod_data_4, 'aladin_dust')


aladin_cy = '/home/puyf/Documents/git/etude_dust_cyclones/ALADIN_rel10_1960_2024.csv'

nbr_cyclones_mois(aladin_cy, YEAR_MIN, YEAR_MAX, juin_sept, "Nombre de cyclones Aladin")

plt.show()

