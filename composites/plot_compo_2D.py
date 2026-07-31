#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
import numpy as np
import netCDF4 as nc
import scipy.stats as stats

import matplotlib.axes as pax
import matplotlib.pyplot as plt
from matplotlib import ticker, cm

import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

yearmin = 1960
yearmax = 1968

data_name="psl"


###################################################

# Some configuration for the plot
# longitude must be within 0 and 360

domain = 'ATL'
#domain = 'EP'
#domain = 'NI'
#domain = 'SI'

path_track = "/cnrm/amacs/USERS/chauvin/NO_SAVE/scenario/cyclones/tracks/SOCLE/Control"
path_data = "/cnrm/amacs/USERS/chauvin/NO_SAVE/scenario/cyclones/tracks/COMPO/SOCLE/Control"

LARG=50

clon=0
lonmin=-LARG*0.2
lonmax=LARG*0.2
lonlabels = [-10, -5, 0, 5, 10] # Tricks for the longitude labels
latmin=-LARG*0.2
latmax=LARG*0.2
latlabels = [-10, -5, 0, 5, 10] # Tricks for the latgitude labels

# Raeding composites

for year in np.arange(yearmin,yearmax+1):
  print(year)
  yp1=year+1
  file_data=path_data+'/compo_2D_'+data_name+'_'+str(year)+'-'+str(yp1)+'.ERA5_evaluation_rel10.nc'
  g=nc.Dataset(file_data)
  var=g.variables['tccmp']
  time=g.variables['time']
  lon=g.variables['lon']
  lat=g.variables['lat']

  nlon=len(lon)
  nlat=len(lat)
  
  if (year == yearmin):
      varmean=np.average(var,axis=0)
  else:
      varmean=varmean+np.average(var,axis=0)

nyears=yearmax-yearmin+1
varmean=varmean/nyears

# Plotting figure
xi, yi = np.mgrid[lonmin:lonmax+0.2:0.2,latmin:latmax+0.2:0.2]
zi = varmean
## Define used projection
proj = ccrs.PlateCarree()
projcl = ccrs.PlateCarree(central_longitude=clon)
#
ax = plt.axes(projection=projcl)
#
## Add a title to the plot
ax.set_title('Composite for {0} [{1}-{2}]'.format(data_name,yearmin,yearmax))
#
## Define domain of the plot
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=projcl)
#
 # Formatting of longitude/latitude labels
lon_formatter = LongitudeFormatter(zero_direction_label=False)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter) 
ax.yaxis.set_major_formatter(lat_formatter)
#
ax.set_xticks(lonlabels, crs=proj)
ax.set_yticks(lonlabels, crs=proj)

#plt.contourf(lon, lat, dgrid, 60, transform=proj)

#ax.pcolormesh(xi, yi, zi.reshape(xi.shape), alpha=0.5)
#plt.contourf(xi, yi, zi.reshape(xi.shape), alpha=1.0)
cs=ax.contourf(xi, yi, zi.reshape(xi.shape), 60, transform=proj, cmap='turbo')
plt.colorbar(cs,ax=ax,shrink=0.6)
plt.show()
# Save the plot in a pdf file
#plt.savefig('PDF/compo_2D_{0}_{1}-{2}_{3}.pdf'.format(data_name,yearmin,yearmax,domain))
# Erase the plot
#plt.close()

