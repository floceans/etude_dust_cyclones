import numpy as np
import matplotlib.pyplot as plt
from func_dust_cy import load_data, plot_time_series_multi, nbr_cyclones_mois, plot_cyclones_vs_aod, nbr_cyclones_an



################## OBS -> IBTRACS + MODIS #######################


YEAR_MIN = 1960
YEAR_MAX = 2020
JJSO = False

merra = '/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/merra/AOT_MERRA2_198001-202012.nc'
modis = '/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/modis/AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean_200207-202312.nc'

aod_data_1 = load_data(merra, "DUEXTTAU", YEAR_MIN, YEAR_MAX, JJSO)
aod_data_2 = load_data(modis, None, YEAR_MIN, YEAR_MAX,JJSO)


plot_time_series_multi(aod_data_1, "merra")
plot_time_series_multi(aod_data_2, 'modis')
#plot_time_series_multi(aod_data_3, 'aladin_dust')
#plot_time_series_multi(aod_data_4, 'aladin_aer')

ibtracs = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ibtracs_transformed_1960_2024.csv'

nbr_cyclones_mois(ibtracs, YEAR_MIN, YEAR_MAX, JJSO, "Nombre de cyclones observés (ibtracs)")


plt.show()

############################## SIMU -> ALADIN ###########################################

aladin_dust = '/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/aladin_dust_mensuel_1960-2024.nc'
aladin_aer = '/mnt/nfs/d10/mosca/USERS/puyf/stage/data/data_dust/aladin/aladin_aer_mensuel_1960-2024.nc'

aod_data_3 = load_data(aladin_aer, "od550aer", YEAR_MIN, YEAR_MAX,JJSO)
aod_data_4 = load_data(aladin_dust, 'od550dust', YEAR_MIN, YEAR_MAX,JJSO)

#plot_time_series_multi(aod_data_4, 'aladin_dust')


aladin_cy = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
aladin_cy_norad = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv'

nbr_cyclones_an(aladin_cy, YEAR_MIN, YEAR_MAX, JJSO, "Nombre de cyclones Aladin", svent = 0)
plt.show()

plot_cyclones_vs_aod(aod_data_4, aladin_cy, YEAR_MIN, YEAR_MAX, JJSO, 'aladin')
plot_cyclones_vs_aod(aod_data_1, ibtracs, YEAR_MIN, YEAR_MAX, JJSO, 'ibtracs/merra')


plt.show()

