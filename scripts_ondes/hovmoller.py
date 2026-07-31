import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

def plot_hovmuller_expert(file_path, year=1980, 
                          lat_min=5, lat_max=20, 
                          lon_min=-100, lon_max=15):

    # 1. Configuration globale de la taille de la police
    plt.rcParams.update({'font.size': 21, 'axes.titlesize': 24, 'axes.labelsize': 21})

    # 2. Chargement et filtrage temporel (JJASO)
    ds = xr.open_dataset(file_path)
    start_date = f"{year}-05-25"
    end_date = f"{year}-10-31"
    ds_sel = ds.sel(time=slice(start_date, end_date))

    if len(ds_sel.time) == 0:
        print(f"Erreur : Aucune donnée pour l'année {year}.")
        return

    # 3. Masquage géographique combiné (Latitude + Longitude)
    # On crée un masque booléen sur la grille 2D (y, x)
    geo_mask = (ds_sel.lat >= lat_min) & (ds_sel.lat <= lat_max) & \
               (ds_sel.lon >= lon_min) & (ds_sel.lon <= lon_max)

    # 4. Extraction et moyenne
    # On applique le masque, puis on moyenne sur 'y'
    # .dropna(dim='x', how='all') permet de supprimer les zones hors 'lon_min/max'
    data_band = ds_sel.va700.where(geo_mask).mean(dim='y').dropna(dim='x', how='all')
    lon_1d = ds_sel.lon.where(geo_mask).mean(dim='y').dropna(dim='x', how='all')

    # 5. Création du graphique
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Niveaux de couleurs centrés sur 0 pour le vent méridien
    levels = np.linspace(-10, 10, 21)
    
    # Tracé (X=longitude, Y=temps)
    # On utilise lon_1d.values pour s'assurer que matplotlib gère bien l'axe X
    cf = ax.contourf(lon_1d, ds_sel.time, data_band, 
                     levels=levels, cmap='RdBu_r', extend='both')
    
    # 6. Mise en forme
    ax.invert_yaxis()  # Temps descendant
    
    # Formatage des dates sur l'axe Y (tous les 15 jours pour ne pas surcharger)
    ax.yaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.yaxis.set_major_locator(mdates.DayLocator(interval=15))
    
    # Barre de couleur
    cbar = plt.colorbar(cf, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label('Vent méridien (m/s)')

    # Titres et labels
    plt.title(f'Simu Ref | va700 | JJASO {year} | {lat_min}°N-{lat_max}°N', pad=20)
    plt.xlabel('Longitude (°E)')
    plt.ylabel('Période')
    
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    
    plt.show()

plot_hovmuller_expert("/cnrm/mosca/USERS/puyf/NO_SAVE/vents_aladin/ref/va700_ref_dayly_4s_1960-2000_MJJASO_filtered.nc")