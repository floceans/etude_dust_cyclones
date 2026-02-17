import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import sys
import os

# --- Configuration ---
aladin = 'ALADIN_rel10_1960_2024.csv'
ibtracs = 'ibtracs_transformed_1960_2024.csv'

filename = ibtracs  # Par défaut, on peut aussi choisir ibtracs

yearmin = int(sys.argv[1]) if len(sys.argv) > 1 else 2018
yearmax = int(sys.argv[2]) if len(sys.argv) > 2 else 2022 

# --- 1. Chargement et filtrage des données ---
df = pd.read_csv(filename)
df['date'] = pd.to_datetime(df['date'])

# Filtrage par années
mask = (df['date'].dt.year >= yearmin) & (df['date'].dt.year <= yearmax)
df_filtered = df.loc[mask]

x = df_filtered['lon'].values
y = df_filtered['lat'].values

if len(x) < 10:
    raise ValueError("Pas assez de points pour estimer une densité KDE")

# --- 2. Calcul de la densité (KDE) ---
# Paramètres du domaine pour la grille de calcul
lonmin, lonmax = -105, 5
latmin, latmax = 5, 35

# Création de la grille
xi, yi = np.mgrid[lonmin:lonmax:200j, latmin:latmax:200j]
coords = np.vstack([xi.flatten(), yi.flatten()])

# Estimation KDE
k = gaussian_kde(np.vstack([x, y]))
zi = k(coords)

# Facteur d'échelle (conservé selon votre formule originale)
nech = len(x)
coef = nech / 4 * 25
zi = zi.reshape(xi.shape) * coef

# --- 3. Plotting ---
proj = ccrs.PlateCarree()
# On centre la carte sur la zone d'intérêt
clon = -50 
projcl = ccrs.PlateCarree(central_longitude=clon)

fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection=projcl)

ax.set_title(f'Track Density ibtracs [{yearmin}-{yearmax}]', fontsize=12, pad=15)
ax.set_extent([lonmin, lonmax, latmin, latmax], crs=proj)

# Ajout des côtes et grille
ax.coastlines(resolution='50m', color='black', linewidth=1)

# Tracé de la densité avec la colormap 'turbo'
levels = np.linspace(0, zi.max(), 25)
cf = ax.contourf(xi, yi, zi, levels=levels, cmap='turbo', transform=proj, extend='max')

cs = ax.contour(xi, yi, zi, levels=levels, colors='black', linewidths=0.5, alpha=0.4, transform=ccrs.PlateCarree())
ax.clabel(cs, inline=True, fontsize=8, fmt='%1.1f')

# Barre d'échelle
cbar = plt.colorbar(cf, ax=ax, orientation='horizontal', pad=0.1, aspect=40)
cbar.set_label('Relative Density Scale')

plt.tight_layout()
plt.show()