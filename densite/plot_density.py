import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import sys
from func import fichier_source, indice_global_cyclogenese, get_density

# param
file = 'aladin_ref'
yearmin = 1960
yearmax = 2000
FONT_SIZE = 21

filename = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv' if file == 'aladin_norad' else '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'

if len(sys.argv) > 2: yearmin = int(sys.argv[2])
if len(sys.argv) > 3: yearmax = int(sys.argv[3])

lonmin, lonmax, latmin, latmax = -105, 5, 5, 30
xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]

#load_data et tratement dans get_density
zi, x, y, long_x = get_density(filename, yearmin, yearmax, xi, yi, svent=26, spress=1005)

#plot
proj = ccrs.PlateCarree()
clon = -50 
projcl = ccrs.PlateCarree(central_longitude=clon)

fig = plt.figure(figsize=(14, 10))
ax = plt.axes(projection=projcl)

ax.set_title(f'Densité de trajectoire : {file} [{yearmin}-{yearmax}]', fontsize=FONT_SIZE, pad=20)
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)

ax.coastlines(resolution='50m', color='black', linewidth=1.2)

gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.3)
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': FONT_SIZE}
gl.ylabel_style = {'size': FONT_SIZE}
gl.xformatter = LongitudeFormatter()
gl.yformatter = LatitudeFormatter()

levels = np.linspace(0, 75, 26)

cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='max')


cs = ax.contour(xi, yi, zi, levels=levels, colors='black', linewidths=0.7, alpha=0.5, transform=proj)

ax.clabel(cs, inline=True, fontsize=12, fmt='%1.0f')


cbar = plt.colorbar(cf, ax=ax, orientation='horizontal', pad=0.15, aspect=40)
cbar.set_label('Relative Density Scale', fontsize=FONT_SIZE)
cbar.ax.tick_params(labelsize=FONT_SIZE)

plt.show()