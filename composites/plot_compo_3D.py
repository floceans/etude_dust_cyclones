#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
import numpy as np
import netCDF4 as nc
import scipy.stats as stats
import xarray as xr
import matplotlib.axes as pax
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
from matplotlib.ticker import ScalarFormatter

import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

yearmin = 1960
yearmax = 1965

data_name="wa"

#
# Fonction trouvée sur stackoverflow
def radial_profile(data, center):
    y, x = np.indices((data.shape))
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    r = r.astype(np.int64)

    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile


###################################################

# Some configuration for the plot
# longitude must be within 0 and 360

domain = 'ATL'
#domain = 'EP'
#domain = 'NI'
#domain = 'SI'

path_track = "/cnrm/amacs/USERS/chauvin/NO_SAVE/scenario/cyclones/tracks/SOCLE/Control"
path_data = "/cnrm/amacs/USERS/chauvin/NO_SAVE/scenario/cyclones/tracks/COMPO/SOCLE/Control"


# Reading composites

for year in np.arange(yearmin,yearmax+1):
  print(year)
  yp1=year+1
  file_data=path_data+'/compo_3D_'+data_name+'_'+str(year)+'-'+str(yp1)+'.ERA5_evaluation_rel10.nc'
  g=nc.Dataset(file_data)
  var=g.variables['tccmp']
  time=g.variables['time']
  lon=g.variables['lon']
  lat=g.variables['lat']
  plev=g.variables['plev']
  
  if (year == yearmin):
      varmean=np.average(var,axis=0)
  else:
      varmean=varmean+np.average(var,axis=0)

nyears=yearmax-yearmin+1
varmean=varmean/nyears

nlon=len(lon)
nlat=len(lat)
nlev=len(plev)
ntim=len(time)


#varad=np.zeros((nlev,int(np.max(radius))))
 

varad=[]
center=([int(nlat/2),int(nlon/2)])
for il in np.arange(nlev):
  xp=radial_profile(np.array(varmean[il,:,:]),center)
  varad.append(xp-np.average(xp))
#  varad.append(xp)

varad=np.array(varad)
radius=np.arange(10)


xi = radius
yi=np.array(plev)
zi = varad[:,0:10]

# Plot config

clon=0

xticks = radius # Tricks for the longitude labels
yticks = np.array(plev[::-1])
xticklabels = np.array([0, 20, 40, 60, 80, 100, 120, 140, 160, 180])
yticklabels = np.array([1000,  925,  850,  750,  700,  600,  500,  400,  300, 250,  200])


ax = plt.axes()

cs=ax.contourf(xi,yi, zi, cmap='turbo')
#
## Add a title to the plot
ax.set_title('Composite for {0} [{1}-{2}]'.format(data_name,yearmin,yearmax))
#
#
ax.set_xticks(xticks)
ax.set_yticks(yticks)
ax.set_xlabel('Radius', fontsize=12, labelpad=10);
ax.set_ylabel('Pressure (hPa)', fontsize=12, labelpad=15);
ax.set_xticklabels(xticklabels)
#ax.set_yticklabels(yticklabels)
ax.invert_yaxis()

plt.colorbar(cs,ax=ax,shrink=0.5)
plt.show()

# Save the plot in a pdf file
#plt.savefig('PDF/compo_3D_{0}_{1}-{2}_{3}.pdf'.format(data_name,yearmin,yearmax,domain))
# Erase the plot
#plt.close()

