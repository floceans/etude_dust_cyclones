#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
import numpy as np
import netCDF4 as nc
from scipy.stats import gaussian_kde

import matplotlib.pyplot as plt
from matplotlib import ticker, cm

import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

dirin = '.'

if not os.path.exists('images'):
    os.makedirs('images')

yearmin = 2004
yearmax = 2005

###################################################
# Domain selection

domain = 'NA'

if domain == 'global':
    clon = 180
    lonmin, lonmax = 0, 360
    latmin, latmax = -60, 60
    lonlabels = [0, 60, 120, 180, 240, 300, 360]
    latlabels = [-60, -30, 0, 30, 60]



elif domain == 'NA':
    clon = 300
    lonmin, lonmax = 280, 330
    latmin, latmax = 8, 30
    lonlabels = [280, 290, 300, 310, 320, 330]
    latlabels = [10, 15, 20, 25, 30]

###################################################
# Reading track files

data = {'lon': [], 'lat': [], 'vmax': [], 'pmin': []}

for iyear in range(yearmin, yearmax):
    yp1 = iyear + 1
    fin = f"suiamip_g359_{iyear}.vor5_res17_1_-2_-5.rel200"
    # local mettre :   f"suiATL_{iyear}-{yp1}.vor5_res17_1_-2_5.rel200"

    path = os.path.join(dirin, fin)
    if not os.path.exists(path):
        print(f"Fichier absent : {path}")
        continue

    with open(path) as f:
        lines = f.readlines()

    for line in lines:
        tmp = line.split()

        # Skip non-data lines
        if len(tmp) < 6:
            continue

        try:
            data['lon'].append(float(tmp[1]))
            data['lat'].append(float(tmp[2]))
            data['vmax'].append(float(tmp[4]))  # m/s
            data['pmin'].append(float(tmp[5]))  # hPa
        except:
            continue

x = np.array(data['lon'])
y = np.array(data['lat'])

if len(x) < 10:
    raise ValueError("Pas assez de points pour estimer une densité KDE")

# Coefficient scaling (your formula kept as-is)
nech = len(x)
coef = nech / 4 * 25

###################################################
# KDE density computation

k = gaussian_kde(np.vstack([x, y]))

# IMPORTANT: specify a step in mgrid
xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]

zi = k(np.vstack([xi.flatten(), yi.flatten()])) * coef
zi = zi.reshape(xi.shape)

###################################################
# Plotting

proj = ccrs.PlateCarree()
projcl = ccrs.PlateCarree(central_longitude=clon)

fig = plt.figure(figsize=(9, 6))
ax = plt.axes(projection=projcl)

ax.set_title(f'Track density [{yearmin}-{yearmax}]')

ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)

# Tick formatting
ax.set_xticks(lonlabels, crs=proj)
ax.set_yticks(latlabels, crs=proj)
ax.xaxis.set_major_formatter(LongitudeFormatter())
ax.yaxis.set_major_formatter(LatitudeFormatter())

# Density map
cs = ax.contourf(xi, yi, zi, 60, transform=proj, cmap="turbo")
plt.colorbar(cs, ax=ax, shrink=0.6)

# Coastlines
ax.coastlines(resolution="50m")

plt.savefig(f'images/density_{yearmin}-{yearmax}_{domain}.pdf', bbox_inches='tight')
plt.close()

print("Figure saved!")
