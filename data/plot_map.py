import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# ================= CONFIGURATION =================
LAT_MIN, LAT_MAX = 10, 30
LON_MIN, LON_MAX = -10, 15
# =================================================

# 1. Création de la figure avec une projection géographique (PlateCarree)
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 2. Définir l'étendue de la carte (on donne du contexte en zoomant un peu plus large que le rectangle)
ax.set_extent([LON_MIN - 15, LON_MAX + 15, LAT_MIN - 10, LAT_MAX + 10], crs=ccrs.PlateCarree())

# 3. Ajout des éléments cartographiques de fond
ax.add_feature(cfeature.LAND, facecolor='#f9f9f9')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.6)
ax.add_feature(cfeature.COASTLINE, edgecolor='black', linewidth=1)
ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray', alpha=0.7)

# 4. Tracé du rectangle (on ferme la boucle en revenant au premier point)
lons = [LON_MIN, LON_MAX, LON_MAX, LON_MIN, LON_MIN]
lats = [LAT_MIN, LAT_MIN, LAT_MAX, LAT_MAX, LAT_MIN]

ax.plot(lons, lats, color='crimson', linewidth=3, linestyle='-',
        transform=ccrs.PlateCarree(), label="Zone d'étude")

# Optionnel : Ajouter un léger remplissage transparent à l'intérieur du rectangle
ax.fill(lons, lats, color='crimson', alpha=0.1, transform=ccrs.PlateCarree())

# 5. Ajout et configuration des lignes de grille (axes gradués)
gl = ax.gridlines(draw_labels=True, linestyle='--', color='gray', alpha=0.5)
gl.top_labels = False    # Désactive les étiquettes en haut
gl.right_labels = False  # Désactive les étiquettes à droite
gl.xlabel_style = {'size': 11}
gl.ylabel_style = {'size': 11}

# 6. Titre et légende
plt.title(f"Localisation de la zone d'étude\nLat: [{LAT_MIN}°N à {LAT_MAX}°N] | Lon: [{LON_MIN}°E à {LON_MAX}°E]", 
          fontsize=14, fontweight='bold', pad=20)
plt.legend(loc='lower left', fontsize=12)

plt.tight_layout()
plt.show()