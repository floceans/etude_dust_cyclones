import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def mask_time(da, year_min=2021, year_max=2024):
    """Masque les données en dehors de la plage temporelle spécifiée."""
    if "time" not in da.dims:
        print("Attention : La variable n'a pas de dimension temporelle.")
        return da
    mask = (da.time.dt.year >= year_min) & (da.time.dt.year <= year_max)
    return da.where(mask, drop=True)

def mask_atlantic(da):
    """
    Applique un masque sur une grille 2D (curvilinéaire).
    """
    lat_min, lat_max = 5, 35
    lon_min, lon_max = -105, 5
    
    # On identifie les noms réels des coordonnées de latitude et longitude
    # Dans ton fichier ALADIN, c'est probablement 'lat' et 'lon' (ou 'latitude'/'longitude')
    # On crée un masque booléen 2D
    mask = (da.lat >= lat_min) & (da.lat <= lat_max) & (da.lon >= lon_min) & (da.lon <= lon_max)
    
    # .where(mask, drop=True) masque les valeurs hors zone ET 
    # réduit les dimensions x et y au plus petit rectangle englobant.
    da_masked = da.where(mask, drop=True)
    
    return da_masked

def load_data(path, var_name=None):
    """Charge le dataset et gère les coordonnées 2D d'ALADIN."""
    ds = xr.open_dataset(path)
    
    if var_name is None:
        var_name = list(ds.data_vars)[0]
    da = ds[var_name]
    
    # 1. Correction des longitudes (0-360 -> -180-180) AVANT le masque
    if da.lon.max() > 180:
        # Pour les grilles 2D, on modifie les valeurs directement
        new_lon = ((da.lon + 180) % 360) - 180
        da = da.assign_coords(lon=new_lon)
    
    # 2. Application du masque spécifique 2D
    aod_masked = mask_atlantic(da)
    
    # 3. Application du masque temporel
    aod_masked = mask_time(aod_masked)
    
    return aod_masked

def print_stats(da, filename):
    """Affiche les stats en ignorant les NaNs du masque."""
    print("\n" + "="*30)
    print(f" STATISTIQUES : {da.name} ({filename})")
    print("="*30)
    # On utilise np.nanmean car xarray.mean gère déjà les NaNs par défaut
    print(f"Moyenne : {da.mean().item():.4f}")
    print(f"Ecart-type: {da.std().item():.4f}")
    print(f"Min / Max : {da.min().item():.4f} / {da.max().item():.4f}")

def plot_aod_map(da, filename):
    """Carte adaptée aux grilles 2D."""
    # Moyenne temporelle si nécessaire
    data_to_plot = da.mean(dim="time") if "time" in da.dims else da
    
    fig = plt.figure(figsize=(11, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Pour les grilles 2D, on doit passer les coordonnées explicitement à xarray.plot
    im = data_to_plot.plot(
        ax=ax, 
        x="lon", y="lat", # Indispensable pour les grilles curvilinéaires
        transform=ccrs.PlateCarree(),
        add_colorbar=True,
        vmin=0, vmax=0.75,  # Ajuste selon tes données
        cbar_kwargs={'label': 'AOD', 'pad': 0.02, 'shrink': 0.8},
        cmap="YlOrBr", robust=True
    )

    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, zorder=3)
    ax.add_feature(cfeature.LAND, facecolor='#f0f0f0', zorder=2)
    
    # Définition auto des limites basées sur les données masquées
    lon_min, lon_max = da.lon.min().item(), da.lon.max().item()
    lat_min, lat_max = da.lat.min().item(), da.lat.max().item()
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
    gl.top_labels = gl.right_labels = False

    plt.title(f"Carte AOD moyenne (zone Atlantique - {filename})", pad=15, fontweight='bold')
    plt.tight_layout()
    return fig

def plot_time_series(da, filename):
    """Série temporelle sur les dimensions x, y."""
    if "time" not in da.dims: return
    
    plt.figure(figsize=(12, 4))
    # Moyenne spatiale sur les dimensions x et y (et non lat/lon)
    if filename == 'aladin':
        da.mean(dim=["x", "y"]).plot(color='#d95f02', linewidth=1.5)
    else:
        da.mean(dim=["lat", "lon"]).plot(color='#d95f02', linewidth=1.5)
    plt.title(f"Série temporelle AOD (Moyenne zone Atlantique - {filename})", fontweight='bold')
    plt.ylim(0,0.35)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

def plot_histogram(da, filename):
    """Histogramme des valeurs non-NaN."""
    plt.figure(figsize=(8, 4))
    # On aplatit les données et on enlève les NaNs explicitement pour l'histogramme
    vals = da.values.flatten()
    plt.hist(vals[~np.isnan(vals)], bins=100, color='#e6ab02', alpha=0.7)
    plt.title(f"Distribution de l'AOD ({filename})", fontweight='bold')
    plt.yscale('log')
    plt.xlim(0,1.8)

    plt.tight_layout()