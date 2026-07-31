import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

###############
# CONFIGURATION
###############
JJASO = True
plev = 85000  # 850 hPa

# Variables de période temporelle
yearmin = '1960'
yearmax = '2000'

# Chemin du fichier
file_ext = "/home/puyf/Documents/data/ext_aladin/ext550dust_ref_3weeks_monthly_1960-2023.nc"
var_name = 'ext550dust' 

def get_ext_mean(path, plev, is_jjaso, ymin, ymax):
    """Charge le fichier, sélectionne le niveau et la période, calcule la moyenne."""
    ds = xr.open_mfdataset(path, combine='by_coords')
    
    # Sélection de la période basée sur les variables yearmin et yearmax
    ds = ds.sel(time=slice(ymin, ymax))
    
    # Sélection du niveau de pression
    ext = ds[var_name].sel(plev=plev, method='nearest')
    
    # Filtrage saisonnier
    if is_jjaso:
        # Mois : Juin(6) à Octobre(10)
        ext = ext.sel(time=ds.time.dt.month.isin([6, 7, 8, 9, 10]))
    
    return ext.mean(dim='time').compute()

# Calcul de la moyenne avec les nouvelles variables
ext_mean = get_ext_mean(file_ext, plev, JJASO, yearmin, yearmax)

lons, lats = ext_mean.lon.values, ext_mean.lat.values

# 5. Configuration de la projection Lambert
map_proj = ccrs.LambertConformal(central_longitude=-49.0, 
                                 central_latitude=9.5, 
                                 standard_parallels=(9.5,))

# 6. Création de la figure
fig = plt.figure(figsize=(12, 8))
ax = plt.axes(projection=map_proj)

ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor='none', edgecolor='black')

import matplotlib.ticker as mticker # Import supplémentaire pour le contrôle des labels

# ... (reste de ton code au-dessus) ...

# 7. Affichage de l'extinction
# On s'assure que les niveaux couvrent bien la plage de données
levels = np.linspace(ext_mean.min(), ext_mean.max(), 21)

cf = ax.contourf(lons, lats, ext_mean, levels=levels, 
                 cmap='YlOrBr', transform=ccrs.PlateCarree(), extend='both')

# 8. Ajout des isolignes
# On prend un intervalle plus large [::4] pour ne pas surcharger la carte
cs = ax.contour(lons, lats, ext_mean, levels=levels[::4], 
                colors='black', linewidths=0.3, alpha=0.5, transform=ccrs.PlateCarree())

# --- CORRECTION : Écriture scientifique sur les isolignes ---
plt.clabel(cs, inline=True, fontsize=8, fmt='%.1e')

# 9. Barre de couleur avec formatage scientifique
# On utilise 'format' directement dans plt.colorbar ou via un formatter
cbar = plt.colorbar(cf, orientation='horizontal', pad=0.05, aspect=50, 
                    format=mticker.ScalarFormatter(useMathText=True))

# On force l'affichage de la puissance de 10 (ex: x10^-4)
cbar.formatter.set_powerlimits((0, 0))
cbar.update_ticks()

cbar.set_label('Extinction à 550nm ($m^{-1}$)', fontsize=12)

# Mise à jour du titre
saison_str = "JJASO" if JJASO else "Annuel"
plt.title(f"Extinction (550nm) à {plev/100:.0f} hPa\nPériode : {yearmin}-{yearmax} ({saison_str})", 
          loc='left', fontsize=14)

plt.show()