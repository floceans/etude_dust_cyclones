import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# ================= CONFIGURATION =================
JJASO = True  
LAT_MIN, LAT_MAX = 0, 30
LON_MIN, LON_MAX = -105, 10
FONT_SIZE = 28
# Liste des niveaux de pression en Pa (du sol vers la haute altitude)
P_LEVELS = [100000, 92500, 85000, 75000, 70000, 60000, 50000, 40000, 30000, 25000, 20000]
# =================================================

dossier_ref = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/ref/"
dossier_norad = "/cnrm/mosca/USERS/puyf/stage/data/vents_aladin/NoRadDust/"

file_list_ref = [dossier_ref + "ua_concat_ref_3weeks_monthly_1960-2000.nc"]
file_list_norad = [dossier_norad + "ua_concat_norad_3weeks_monthly_1960-2000.nc"]

def compute_total_shear_map(files, is_jjaso):
    """
    Calcule la somme de |U_i - U_{i-1}| sur les niveaux de pression définis.
    """
    ds = xr.open_mfdataset(files, combine='by_coords', chunks={'time': 12}).sel(time=slice('1960', '2000'))
    
    if is_jjaso:
        ds = ds.sel(time=ds.time.dt.month.isin([7, 8, 9]))
    
    u_levels = ds['ua'].sel(plev=P_LEVELS, method='nearest').sortby('plev', ascending=False)
    total_shear = abs(u_levels.diff(dim='plev')).sum(dim='plev')
    
    return total_shear.where(total_shear < 1e10).mean(dim='time').compute()

print("Calcul des sommes de cisaillement vertical...")
shear_ref = compute_total_shear_map(file_list_ref, JJASO)
shear_norad = compute_total_shear_map(file_list_norad, JJASO)

# Différence entre les deux simulations
diff_shear = shear_norad - shear_ref

lon, lat = diff_shear.lon, diff_shear.lat

# ================= FIGURE 1 (INCHANGÉE) =================
fig1 = plt.figure(figsize=(15, 10))
ax1 = plt.axes(projection=ccrs.PlateCarree())

v_limit = max(abs(diff_shear.min()), abs(diff_shear.max())) * 0.8
vmin, vmax = -float(v_limit), float(v_limit)



cf1 = ax1.contourf(
    lon, lat, diff_shear,
    levels=np.linspace(vmin, vmax, 21),
    cmap='RdBu_r', extend='both',
    transform=ccrs.PlateCarree()
)

cs1 = ax1.contour(
    lon, lat, diff_shear,
    levels=np.linspace(vmin, vmax, 11),
    colors='black', linewidths=0.5, alpha=0.3,
    transform=ccrs.PlateCarree()
)
plt.clabel(cs1, inline=True, fontsize=10, fmt='%1.1f')

ax1.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
ax1.coastlines(resolution='110m', color='black', linewidth=1.2)
ax1.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.6)

gl1 = ax1.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
gl1.top_labels = False
gl1.right_labels = False

cbar1 = plt.colorbar(cf1, ax=ax1, orientation='horizontal', pad=0.08, aspect=40, fraction=0.04)
cbar1.set_label(r'$\Delta \sum |U_{i} - U_{i-1}|$ (m/s)', fontsize=FONT_SIZE)

plt.title(
    f"Différence de cisaillement total cumulé (1000-200 hPa)\nNoRadDust - Ref | JAS 1960-2000",
    fontsize=FONT_SIZE, pad=20
)


# ================= FIGURE 2 (4 COUCHES SPECIFIQUES - ÉCHELLE FIXE) =================
print("Calcul des cisaillements par couches spécifiques...")

def compute_layer_shear_map(files, p1, p2, is_jjaso):
    """
    Calcule le cisaillement absolu entre deux niveaux spécifiques |U_p1 - U_p2|
    """
    ds = xr.open_mfdataset(files, combine='by_coords', chunks={'time': 12}).sel(time=slice('1960', '2000'))
    
    if is_jjaso:
        ds = ds.sel(time=ds.time.dt.month.isin([7, 8, 9]))
        
    u_p1 = ds['ua'].sel(plev=p1, method='nearest')
    u_p2 = ds['ua'].sel(plev=p2, method='nearest')
    
    layer_shear = abs(u_p1 - u_p2)
    return layer_shear.where(layer_shear < 1e10).mean(dim='time').compute()

# Définition des paires de niveaux (en Pa) demandées
layers = [
    (100000, 92500, "1000 - 925 hPa"),
    (85000,  75000, "850 - 750 hPa"),
    (60000,  50000, "600 - 500 hPa"),
    (40000,  30000, "400 - 300 hPa")
]

# Création de la grille 2x2
fig2, axes = plt.subplots(2, 2, figsize=(20, 16), subplot_kw={'projection': ccrs.PlateCarree()})
axes_flat = axes.flatten()

# --- CONFIGURATION DE L'ÉCHELLE COMMUNE ---
VMIN_FIXED = -1.5
VMAX_FIXED = 1.5
LEVELS_CF = np.linspace(VMIN_FIXED, VMAX_FIXED, 21)
LEVELS_CS = np.linspace(VMIN_FIXED, VMAX_FIXED, 11)

for i, (p1, p2, label) in enumerate(layers):
    ax = axes_flat[i]
    
    # Calcul pour la couche courante
    shear_layer_ref = compute_layer_shear_map(file_list_ref, p1, p2, JJASO)
    shear_layer_norad = compute_layer_shear_map(file_list_norad, p1, p2, JJASO)
    diff_layer = shear_layer_norad - shear_layer_ref
    
    # 1. Remplissage des couleurs (Échelle forcée entre -1.5 et 1.5)
    cf_l = ax.contourf(
        lon, lat, diff_layer,
        levels=LEVELS_CF,
        cmap='RdBu_r', extend='both',
        transform=ccrs.PlateCarree()
    )
    
    # 2. Contours linéaires
    cs_l = ax.contour(
        lon, lat, diff_layer,
        levels=LEVELS_CS,
        colors='black', linewidths=0.5, alpha=0.3,
        transform=ccrs.PlateCarree()
    )
    ax.clabel(cs_l, inline=True, fontsize=9, fmt='%1.2f')
    
    # 3. Habillage de la carte
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax.coastlines(resolution='110m', color='black', linewidth=1.2)
    ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.6)
    
    # Gestion des étiquettes de grille
    gl_l = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
    gl_l.top_labels = False
    gl_l.right_labels = False
    if i % 2 != 0: 
        gl_l.left_labels = False # Enlève les latitudes au milieu
    if i < 2:        
        gl_l.bottom_labels = False # Enlève les longitudes au milieu
    
    ax.set_title(f"Couche : {label}", fontsize=FONT_SIZE - 2, pad=10)

# 4. Ajout d'une UNIQUE barre de couleur pour les 4 cartes
# On utilise ax=axes_flat.tolist() pour que la colorbar s'aligne proprement avec toute la grille
cbar_global = fig2.colorbar(cf_l, ax=axes_flat.tolist(), orientation='horizontal', pad=0.06, aspect=50, fraction=0.05)
cbar_global.set_label(r'$\Delta |U_{p1} - U_{p2}|$ (m/s)', fontsize=FONT_SIZE - 2)
cbar_global.ax.tick_params(labelsize=14)

# Titre général
fig2.suptitle(
    "Différence de cisaillement vertical par couche consécutive\nNoRadDust - Ref | JAS 1960-2000",
    fontsize=FONT_SIZE, y=0.96
)

plt.show()