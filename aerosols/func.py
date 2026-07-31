import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import plotly.graph_objects as go
from scipy.interpolate import griddata
import pandas as pd

import matplotlib.ticker as mticker
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


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
    lon_min, lon_max = -105, 15
    
    # On identifie les noms réels des coordonnées de latitude et longitude
    # Dans ton fichier ALADIN, c'est probablement 'lat' et 'lon' (ou 'latitude'/'longitude')
    # On crée un masque booléen 2D
    
    mask = (da.lat >= lat_min) & (da.lat <= lat_max) & (da.lon >= lon_min) & (da.lon <= lon_max)
    
    # .where(mask, drop=True) masque les valeurs hors zone ET 
    # réduit les dimensions x et y au plus petit rectangle englobant.

    
    da_masked = da.where(mask, drop=True)
    
    return da_masked

def load_data(path, var_name, an_min, an_max, JJASO=False):
    """
    Charge le dataset, gère les coordonnées 2D et applique les masques spatiaux, 
    temporels et saisonniers.
    """
    ds = xr.open_dataset(path)
    
    if var_name is None:
        var_name = list(ds.data_vars)[0]
    da = ds[var_name]

    # 1. Correction des longitudes (0-360 -> -180-180)
    if da.lon.max() > 180:
        new_lon = ((da.lon + 180) % 360) - 180
        da = da.assign_coords(lon=new_lon)
    
    # 2. Application du masque spécifique 2D (Atlantique)
    aod_masked = mask_atlantic(da)
    
    # 3. Application du masque temporel (années)
    aod_masked = mask_time(aod_masked, an_min, an_max)

    # 4. Nouveau : Filtre saisonnier JJASO
    if JJASO:
        # On vérifie quand même que la dimension 'time' est présente
        if "time" in aod_masked.dims:
            # .isin([6, 7, 8, 9, 10]) sélectionne Juin à Octobre
            aod_masked = aod_masked.sel(time=aod_masked.time.dt.month.isin([6, 7, 8, 9, 10]))
        else:
            print("Attention : Impossible d'appliquer le filtre JJASO (pas de dimension temporelle).")

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
    """Carte AOD avec échelle non-linéaire pour faire ressortir les faibles valeurs (> 0.05)."""
    # --- 1. PRÉPARATION DES DONNÉES ---
    data_to_plot = da.mean(dim="time") if "time" in da.dims else da

    # --- 2. TRACÉ ET FIGURE ---
    fig = plt.figure(figsize=(14, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Norme étirant les faibles valeurs (gamma=0.5 rend 0.05 bien distinct de 0)
    #norm = mcolors.PowerNorm(gamma=0.5, vmin=0, vmax=0.65)

    # Affichage des données
    im = data_to_plot.plot(
        ax=ax, 
        x="lon", y="lat", 
        transform=ccrs.PlateCarree(),
        add_colorbar=False,  
        #norm=norm,            # Applique l'étalement dynamique des couleurs
        cmap="jet", 
        robust=True
    )

    # --- 3. AJOUT DES ISOLIGNES ---
    levels = np.arange(0, 0.65 + 0.001, 0.05)
    linestyles = ['--' if val < 0 else '-' for val in levels]
    
    cs = ax.contour(
        data_to_plot["lon"], data_to_plot["lat"], data_to_plot,
        levels=levels,
        colors='black',
        linestyles=linestyles,
        linewidths=1.2,
        transform=ccrs.PlateCarree(),
        alpha = 0.5,
        zorder=4
    )
    ax.clabel(cs, inline=True, fontsize=12, fmt='%.2f', colors='black')

    # --- 4. COSMÉTIQUE DE LA CARTE ---
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=3)
    
    lon_min, lon_max = da.lon.min().item(), da.lon.max().item()
    lat_min, lat_max = da.lat.min().item(), da.lat.max().item()
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

    # --- 5. CONFIGURATION DES AXES ET GRILLE ---
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4, zorder=2)
    gl.top_labels = gl.right_labels = False
    
    gl.xlocator = mticker.MultipleLocator(20)
    gl.ylocator = mticker.MultipleLocator(5)
    
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    
    gl.xlabel_style = {'size': 25}
    gl.ylabel_style = {'size': 25}

    # --- 6. COLORBAR HORIZONTALE AVEC GRADUATIONS CIBLÉES ---
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.12, shrink=0.85, aspect=35)
    cbar.set_label('Dust-AOD', fontsize=24)
    cbar.ax.tick_params(labelsize=24)
    
    # Graduations explicites sur la colorbar pour bien repérer 0, 0.05, 0.1, etc.
    cbar.set_ticks([0, 0.05, 0.1, 0.2, 0.35, 0.5, 0.65])

    # --- 7. TITRE ---
    plt.title(f"Carte AOD moyenne (zone Atlantique - {filename})", pad=15, fontweight='bold', fontsize=24)
    
    return fig

def plot_aod_diff_map(da1, da2, name1, name2, vlimit=0.1):
    # 1. Préparation des données (Moyenne temporelle)
    m1 = da1.mean(dim="time").squeeze() if "time" in da1.dims else da1.squeeze()
    m2 = da2.mean(dim="time").squeeze() if "time" in da2.dims else da2.squeeze()

    # 2. REGRIDDING (Interpolation de m2 sur la grille y, x de m1)
    try:
        m2_resampled = m2.interp(y=m1.y, x=m1.x, method="linear")
    except Exception:
        m2_resampled = m2.interp(lat=m1.lat, lon=m1.lon, method="linear")

    # 3. Calcul de la différence
    diff_total = m1*0.9 - m2_resampled
    diff_total = diff_total.assign_coords(lat=m1["lat"], lon=m1["lon"])

    # --- SÉLECTION DE LA ZONE (0N-40N, 120W-40E) ---
    lat_min, lat_max = 5, 30
    lon_min, lon_max = -100, 5

    mask = (diff_total["lat"] >= lat_min) & (diff_total["lat"] <= lat_max) & \
           (diff_total["lon"] >= lon_min) & (diff_total["lon"] <= lon_max)
    
    diff_zone = diff_total.where(mask, drop=True)

    # --- CALCUL DU RMSE ---
    rmse_val = np.sqrt((diff_zone**2).mean(skipna=True)).values
    print(f"--- Statistiques [{name1} vs {name2}] ---")
    print(f"RMSE Zone ({lat_min}, {lat_max}N - {lon_min}, {lon_max}W): {rmse_val:.4f}")

    # 4. TRACÉ
    fig = plt.figure(figsize=(14, 8)) # Légèrement agrandi pour accueillir la colorbar en bas
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Affichage principal (sans colorbar automatique)
    im = diff_zone.plot.pcolormesh(
        ax=ax, 
        x="lon", y="lat", 
        transform=ccrs.PlateCarree(),
        add_colorbar=False, # Désactivé pour la gérer manuellement ci-dessous
        vmin=-vlimit, vmax=vlimit,
        cmap="RdBu_r", 
        robust=True
    )

    # --- AJOUT DES ISOLIGNES (Tous les 0.05) ---
    # Génération des niveaux de -vlimit à +vlimit par pas de 0.05
    levels = np.arange(-vlimit, vlimit + 0.001, 0.05)
    # Définition des styles : '--' (dashed) pour le négatif, '-' (solid) pour le reste
    linestyles = ['--' if val < 0 else '-' for val in levels]
    
    cs = ax.contour(
        diff_zone["lon"], diff_zone["lat"], diff_zone,
        levels=levels,
        colors='black',
        linestyles=linestyles,
        linewidths=1.2,
        transform=ccrs.PlateCarree(),
        zorder=4
    )
    # Affichage des valeurs sur les isolignes
    ax.clabel(cs, inline=True, fontsize=12, fmt='%.2f', colors='black')

    # Cosmétique de la carte
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, zorder=3)
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5, zorder=3)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    # --- CONFIGURATION DES AXES (Police taille 25) ---
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4, zorder=2)
    gl.top_labels = gl.right_labels = False
    
    # Configuration des intervalles (ex: pas de 20° en long, 10° en lat)
    gl.xlocator = mticker.MultipleLocator(20)
    gl.ylocator = mticker.MultipleLocator(5)
    
    # Formatage des étiquettes (N/S, E/W)
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    
    # Application de la taille de police 25 sur les axes
    gl.xlabel_style = {'size': 25}
    gl.ylabel_style = {'size': 25}

    # --- COLORBAR HORIZONTALE (Police taille 24) ---
    # 'pad' augmenté à 0.12 pour éviter que la colorbar chevauche les étiquettes de l'axe X
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.12, shrink=0.85, aspect=35)
    cbar.set_label(f'Différence AOD ({name1} - {name2})', fontsize=24)
    cbar.ax.tick_params(labelsize=24)

    # --- TITRE (Police taille 24) ---
    plt.title(f"Différence AOD : {name1} - {name2}\nRMSE: {rmse_val:.4f}", pad=15, fontweight='bold', fontsize=24)
    
    return fig

def plot_aod_map_years(da, filename, years_list):
    """
    Carte adaptée aux grilles 2D.
    Filtre et moyenne l'AOD uniquement pour une liste d'années spécifiée.
    Ajoute des isolignes et applique une taille de police de 21.
    """
    # --- 1. Filtrage sur les années sélectionnées ---
    if "time" in da.dims:
        # Sélection des données où l'année appartient à la liste passée en argument
        da_filtered = da.sel(time=da.time.dt.year.isin(years_list))
        data_to_plot = da_filtered.mean(dim="time")
    else:
        data_to_plot = da
        print(" Attention : Pas de dimension 'time' détectée. Filtrage par année impossible.")
    
    # --- 2. Configuration de la figure et de la police ---
    font_size = 21
    # On agrandit légèrement la figure (13, 8) pour que la police 21 respire
    fig = plt.figure(figsize=(13, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # --- 3. Affichage du fond (AOD) ---
    im = data_to_plot.plot(
        ax=ax, 
        x="lon", y="lat", 
        transform=ccrs.PlateCarree(),
        add_colorbar=False,  # On désactive la colorbar auto pour mieux la gérer en taille 21
        vmin=0, vmax=0.65,  
        cmap="YlOrBr", robust=True
    )

    # --- 4. Ajout des isolignes (Contours) ---
    # On utilise la méthode contour de xarray adaptée aux grilles 2D
    contours = data_to_plot.plot.contour(
        ax=ax,
        x="lon", y="lat",
        transform=ccrs.PlateCarree(),
        colors="black",       # Couleur des lignes
        linewidths=1.0,       # Épaisseur des lignes
        levels=5,             # Nombre d'isolignes automatiques (tu peux passer une liste ex: [0.1, 0.3, 0.5])
    )
    # Optionnel : Ajouter les étiquettes de valeurs sur les isolignes
    ax.clabel(contours, inline=True, fmt='%.2f', fontsize=font_size - 6)

    # --- 5. Habillage de la carte ---
    ax.add_feature(cfeature.COASTLINE, linewidth=1.0, zorder=3)
    
    # Définition auto des limites basées sur les données
    lon_min, lon_max = da.lon.min().item(), da.lon.max().item()
    lat_min, lat_max = da.lat.min().item(), da.lat.max().item()
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    # Gestion des lignes de grille et de leur taille de police
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = {'size': font_size}
    gl.ylabel_style = {'size': font_size}

    # --- 6. Ajout de la Colorbar personnalisée ---
    cbar = fig.colorbar(im, ax=ax, pad=0.03, shrink=0.8, orientation='vertical')
    cbar.set_label('AOD', fontsize=font_size)
    cbar.ax.tick_params(labelsize=font_size - 2)  # Graduations légèrement plus petites pour l'élégance

    # --- 7. Titre dynamique ---
    # Transforme la liste [1999, 2001] en chaîne "1999, 2001"
    years_str = ", ".join(map(str, sorted(years_list)))
    plt.title(f"Dust-AOD Moyenne \n{filename}", pad=20, fontweight='bold', fontsize=font_size)
    
    plt.tight_layout()
    return fig



def plot_aod_diff_map_year(da1, years_list1, da2, years_list2, label1="10y ACE + fort", label2="10y ACE + faible", vlimit=0.1):
    """
    Calcule et affiche la différence (Map1 - Map2) entre deux sélections d'années.
    Gère automatiquement l'alignement des grilles si les modèles sont différents.
    """
    # --- 1. Extraction et calcul des moyennes pour chaque période ---
    sub_da1 = da1.sel(time=da1.time.dt.year.isin(years_list1)).mean(dim="time")
    sub_da2 = da2.sel(time=da2.time.dt.year.isin(years_list2)).mean(dim="time")
    
    # --- 2. Sécurité : Alignement des grilles (si comparaison Aladin vs Merra) ---
    # Si les dimensions diffèrent (ex: (x,y) vs (lat,lon)), on rééchantillonne da2 sur la grille de da1
    if sub_da1.shape != sub_da2.shape:
        print("🔄 Grilles différentes détectées. Interpellation de la seconde carte sur la première...")
        # Si les coordonnées de da2 sont en 1D (comme Merra), on peut interpoler facilement
        if 'lat' in sub_da2.dims and 'lon' in sub_da2.dims:
            sub_da2 = sub_da2.interp(lat=sub_da1.lat, lon=sub_da1.lon, method="linear")
        else:
            # Cas des grilles curvilignes complexes
            sub_da2 = sub_da2.interp_like(sub_da1, method="linear")

    # --- 3. Calcul de la différence (Carte 1 - Carte 2) ---
    diff = sub_da1 - sub_da2

    # --- 4. Configuration graphique (Police 21) ---
    font_size = 21
    fig = plt.figure(figsize=(14, 9))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # --- 5. Affichage de la différence ---
    # 'center=0' force une échelle symétrique (ex: -0.2 à +0.2) et choisit un cmap divergent
    im = diff.plot(
        ax=ax, 
        x="lon", y="lat", 
        transform=ccrs.PlateCarree(),
        add_colorbar=False,
        center=0,          # IMPORTANT : centre la palette sur 0
        cmap="RdBu_r",     # Rouge = Positif (Plus d'AOD), Bleu = Négatif (Moins d'AOD)
        robust=True
    )

    # --- 6. Ajout des isolignes de la différence ---
    contours = diff.plot.contour(
        ax=ax,
        x="lon", y="lat",
        transform=ccrs.PlateCarree(),
        colors="black",
        linewidths=1.2,
        levels=5
    )
    ax.clabel(contours, inline=True, fmt='%.2f', fontsize=font_size - 6)

    # --- 7. Habillage de la carte ---
    ax.add_feature(cfeature.COASTLINE, linewidth=1.0, zorder=3)
    
    # Limites géographiques basées sur da1
    lon_min, lon_max = da1.lon.min().item(), da1.lon.max().item()
    lat_min, lat_max = da1.lat.min().item(), da1.lat.max().item()
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    
    # Grille et étiquettes axes
    gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.4)
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = {'size': font_size}
    gl.ylabel_style = {'size': font_size}

    # --- 8. Colorbar personnalisée ---
    cbar = fig.colorbar(im, ax=ax, pad=0.03, shrink=0.8)
    cbar.set_label('Δ dust-AOD', fontsize=font_size)
    cbar.ax.tick_params(labelsize=font_size - 2)

    # --- 9. Titre de la carte ---
    title_text = f"Δ dust-AOD : {label1} − {label2}"
    plt.title(title_text, pad=20, fontweight='bold', fontsize=font_size)
    
    plt.tight_layout()
    return fig


def plot_time_series(da, filename):
    """Série temporelle sur les dimensions x, y."""

    if "time" not in da.dims: 
        return
    
    plt.figure(figsize=(12, 4))
    # Moyenne spatiale sur x et y ou lat/lon selon nc
    if filename == 'aladin_dust' or filename == 'aladin_aer':
        da.mean(dim=["x", "y"]).plot(color='#d95f02', linewidth=1.5)
    else:
        da.mean(dim=["lat", "lon"]).plot(color='#d95f02', linewidth=1.5)
    plt.title(f"Série temporelle AOD (Moyenne zone Atlantique - {filename})", fontweight='bold')
    plt.ylim(0,0.35)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

def plot_time_series_multi(da, filename, linestyle = '-', color = 'orange'):

    if "time" not in da.dims: 
        print(f"Erreur : pas de dimension 'time' dans {filename}")
        return
    
    # 1. Sélection automatique des dimensions spatiales selon le nom du fichier
    if filename in ['aladin_dust', 'aladin_aer', 'aladin_dust_3s', 'aladin_dust_3s_mdr']:
        dims_to_mean = ["x", "y"]
    else:
        dims_to_mean = ["lat", "lon"]
        
    # 2. Tracé de la moyenne spatiale
    # On utilise 'label' pour que la légende s'affiche correctement
    # On ne fixe pas la couleur pour que Matplotlib change de couleur à chaque appel
        
    da.mean(dim=dims_to_mean).plot(label=filename, linewidth=1.5, linestyle=linestyle, color = color)

    
    # 3. Configuration du graphique (écrasée à chaque appel, donc seule la dernière compte)
    plt.title("Séries temporelles AOD (Moyenne zone Atlantique)", fontweight='bold')
    #plt.ylim(0, 0.35)
    plt.grid(True, alpha=0.3)
    
    # 4. Activation de la légende
    plt.legend()
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
    plt.ylim(0, 10**7)

    plt.tight_layout()


def plot_climatology_bars(datasets_dict, title="Climatologie Mensuelle de l'AOD"):
    """
    Trace un graphique à bâtons comparatif de la climatologie mensuelle
    avec de grandes polices synchronisées sur les cartes.
    datasets_dict : dict sous forme {'Nom du dataset': DataArray}
    """
    months = np.arange(1, 13)
    month_names = ['J', 'F', 'M', 'A', 'M', 'J', 
                   'J', 'A', 'S', 'O', 'N', 'D']
    
    # Figure agrandie à 14x8 pour accommoder les textes volumineux
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Paramètres pour les barres groupées
    n_datasets = len(datasets_dict)
    total_width = 0.8
    bar_width = total_width / n_datasets
    
    for i, (label, da) in enumerate(datasets_dict.items()):
        # 1. Moyenne spatiale (sur lat et lon)
        spatial_mean = da.mean(dim=da.dims[1:], skipna=True)
        
        # 2. Moyenne par mois (Climatologie)
        climatology = spatial_mean.groupby('time.month').mean()
        
        # S'assurer que tous les mois sont présents
        values = [climatology.sel(month=m).values if m in climatology.month else 0 for m in months]
        
        # 3. Positionnement des barres sur l'axe X
        pos = months - (total_width/2) + (i * bar_width) + (bar_width/2)
        
        ax.bar(pos, values, width=bar_width, label=label)

    # --- CONFIGURATION DES POLICES ET AXES ---
    # Graduations de l'axe X
    ax.set_xticks(months)
    ax.set_xticklabels(month_names)

    # Taille de police des chiffres/mois sur les axes (22 pt)
    ax.tick_params(axis='both', which='major', labelsize=28)

    # Noms des axes (24 pt)
    ax.set_xlabel('Mois', fontsize=28, labelpad=10)
    ax.set_ylabel('DAOD (550 nm)', fontsize=28, labelpad=10)

    # Titre principal (24 pt, gras)
    ax.set_title(title, fontsize=24, fontweight='bold', pad=15)

    # Légende (20 pt)
    ax.legend(fontsize=23, loc='best')

    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    return fig


def plot_time_series_interactive(datasets_dict, output_file="comparaison_aod.html"):
    """
    Crée un graphique interactif exportable en HTML.
    datasets_dict : dictionnaire { 'Nom': (DataArray, 'couleur', 'style') }
    """
    fig = go.Figure()

    for name, (da, color, dash) in datasets_dict.items():
        # Détection automatique des dimensions spatiales
        dims_to_mean = ["x", "y"] if any(d in da.dims for d in ["x", "y"]) else ["lat", "lon"]
        
        # Calcul de la moyenne spatiale
        ts = da.mean(dim=dims_to_mean, skipna=True)
        
        # Conversion en DataFrame pour Plotly
        df = ts.to_dataframe(name="AOD").reset_index()

        # Ajout de la courbe
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['AOD'],
            mode='lines',
            name=name,
            line=dict(color=color, dash=dash, width=2),
            hovertemplate='%{x|%Y-%m}: <b>%{y:.3f}</b><extra></extra>'
        ))

    # Mise en forme du graphique
    fig.update_layout(
        title="Séries temporelles AOD (Interactif)",
        xaxis_title="Temps",
        yaxis_title="AOD (550 nm)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(itemclick="toggle", itemdoubleclick="toggleothers") # Permet le clic pour masquer
    )

    # Export en fichier HTML autonome
    fig.write_html(output_file)
    print(f"Graphique interactif sauvegardé sous : {output_file}")
    
    # Affichage immédiat dans le navigateur/notebook
    fig.show()


def charger_et_moyenner(filepath, var_name, an_min, an_max, JJASO=False):
    """
    Charge, filtre (option JJASO), moyenne et réduit la résolution.
    """
    try:
        ds = xr.open_dataset(filepath)
        
        if 'time' not in ds.dims:
            raise ValueError(f"Pas de dimension 'time' dans {filepath}")

        # 1. Sélection de la période d'années
        ds_slice = ds[var_name].sel(time=slice(f"{an_min}-01-01", f"{an_max}-12-31"))
        
        # --- NOUVEAU : FILTRAGE SAISONNIER (Juin à Octobre) ---
        if JJASO:
            ds_slice = ds_slice.sel(time=ds_slice.time.dt.month.isin([6, 7, 8, 9, 10]))
            print(f"Filtrage JJASO appliqué pour {var_name}.")

        if ds_slice.time.size == 0:
            raise ValueError(f"Aucune donnée pour les critères sélectionnés ({an_min}-{an_max}, JJASO={JJASO})")

        # 2. Moyenne temporelle (Calculée sur les données filtrées)
        ds_mean = ds_slice.mean(dim='time')

        # 3. Réduction de résolution spatiale (Coarsening)
        dim_lat = 'lat' if 'lat' in ds_mean.dims else 'y'
        dim_lon = 'lon' if 'lon' in ds_mean.dims else 'x'

        ds_coarse = ds_mean.coarsen({dim_lat: 3, dim_lon: 3}, boundary='trim').mean()

        print(f"Traitement de {var_name} terminé. Grille : {ds_coarse.shape}")
        return ds_coarse

    except Exception as e:
        print(f"Erreur lors du traitement de {filepath} : {e}")
        return None


def calculer_module(u, v):
    """Calcule la vitesse du vent (norme)."""
    # xarray gère automatiquement l'alignement des grilles
    return np.sqrt(u**2 + v**2)

def tracer_carte_vent_regionale(u_avg, v_avg, module, titre, zonage):
    """
    Génère une carte régionale :
    - Option : Filtre les données de Juin à Octobre.
    - Fond coloré (module) + Flèches (quiver).
    """

    u_plot = u_avg.mean(dim='time') if 'time' in u_avg.dims else u_avg
    v_plot = v_avg.mean(dim='time') if 'time' in v_avg.dims else v_avg
    mod_plot = module.mean(dim='time') if 'time' in module.dims else module

    # --- 2. INITIALISATION CARTO ---
    fig = plt.figure(figsize=(14, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(zonage, crs=ccrs.PlateCarree())

    # Identification des coordonnées
    lon_name = 'lon' if 'lon' in mod_plot.coords else 'longitude'
    lat_name = 'lat' if 'lat' in mod_plot.coords else 'latitude'

    # --- 3. TRACÉ DU MODULE (COULEUR) ---
    im = mod_plot.plot.pcolormesh(
        ax=ax, 
        x=lon_name, y=lat_name,
        transform=ccrs.PlateCarree(),
        cmap='turbo',
        add_colorbar=False,
        shading='auto',
        zorder=1
    )

    # --- 4. HABILLAGE ---
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5, edgecolor='black', zorder=2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='black', alpha=0.8, zorder=2)
    
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.03, shrink=0.7)
    cbar.set_label('Vitesse du vent (m/s)', fontsize=12, fontweight='bold')

    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False,
                      linewidth=0.5, color='gray', alpha=0.5, zorder=3)
    gl.top_labels = False
    gl.right_labels = False

    # --- 5. FLÈCHES (QUIVER) ---
    if mod_plot[lon_name].ndim == 2:
        LON = mod_plot[lon_name].values
        LAT = mod_plot[lat_name].values
    else:
        LON, LAT = np.meshgrid(mod_plot[lon_name].values, mod_plot[lat_name].values)

    skip = 12
    U_sub = u_plot.values[::skip, ::skip]
    V_sub = v_plot.values[::skip, ::skip]
    LON_sub = LON[::skip, ::skip]
    LAT_sub = LAT[::skip, ::skip]

    ax.quiver(LON_sub, LAT_sub, U_sub, V_sub, 
              transform=ccrs.PlateCarree(), 
              color='black', edgecolor='black', linewidth=0.3,
              pivot='middle', scale=120, zorder=4)

    plt.title(titre, fontsize=15, fontweight='bold', pad=20)
    plt.show()