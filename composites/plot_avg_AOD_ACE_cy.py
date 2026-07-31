import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os

# ==============================================================================
# CONFIGURATION
# ==============================================================================
fichier_entree = "/cnrm/mosca/USERS/puyf/NO_SAVE/composites/compo_cy_aod_1960-2024.nc"

print(f"📂 Chargement du fichier : {fichier_entree}")
ds = xr.open_dataset(fichier_entree)

# Récupération des variables
numrec = ds["numrec"].values
numdat = ds["numdat"].values

# 1. Identification des frontières de chaque cyclone
indices_cyclones = np.where(numrec == 1)[0]
indices_limites = np.append(indices_cyclones, len(numrec))

print(f"🌪️ {len(indices_cyclones)} cyclones identifiés. Calcul de l'ACE en cours...")

cyclone_stats = []
year_counter = {}

# 2. Boucle sur chaque cyclone pour calculer l'ACE
for i in range(len(indices_cyclones)):
    start_idx = indices_limites[i]
    end_idx = indices_limites[i+1]
    
    year = "YYYY"
    try:
        val_dat = numdat[start_idx]
        dat_str = val_dat.decode('utf-8').strip() if isinstance(val_dat, bytes) else str(val_dat).strip()
        if len(dat_str) >= 4 and dat_str[:4].isdigit():
            year = dat_str[:4]
    except:
        pass

    if year == "YYYY":
        try:
            t_val = str(ds["time"].isel(time=start_idx).values).strip()
            if len(t_val) >= 4 and t_val[:4].isdigit():
                year = t_val[:4]
        except:
            pass

    if year not in year_counter:
        year_counter[year] = 1
    else:
        year_counter[year] += 1
        
    nom_cyclone = f"{year}-{year_counter[year]}"

    wind_cyclone = ds["wind_module"].isel(time=slice(start_idx, end_idx))
    v_max_ms = wind_cyclone.max(dim=["plev", "lat", "lon"]).values
    v_max_knots = v_max_ms * 1.94384
    ace = np.sum(v_max_knots**2) * 1e-4
    
    cyclone_stats.append({
        "nom": nom_cyclone, 
        "ace": ace,
        "start_idx": start_idx,
        "end_idx": end_idx
    })

# 3. Tri des résultats du plus fort au plus faible ACE
cyclone_stats.sort(key=lambda x: x["ace"], reverse=True)


valeurs_aod_individuel = []
rangs_cyclones = list(range(1, len(cyclone_stats) + 1))

print("\n📈 Calcul de l'AOD moyen pour chaque cyclone (par ordre décroissant d'ACE)...")

for i, c in enumerate(cyclone_stats):
    # Sélection du slice temporel propre à ce cyclone (plus rapide que range)
    slice_temps = slice(c["start_idx"], c["end_idx"])
    
    # Calcul de la moyenne spatio-temporelle uniquement pour CE cyclone
    aod_scalaire = ds["aod"].isel(time=slice_temps).mean(dim=["time", "lat", "lon"]).values
    valeurs_aod_individuel.append(aod_scalaire)
    
    # Suivi de l'avancement en console (tous les 50 cyclones pour éviter les spams)
    if (i + 1) % 50 == 0 or (i + 1) == len(cyclone_stats):
        print(f"   Cyclone {i+1:03d}/{len(cyclone_stats)} ({c['nom']}) -> AOD moyen = {float(aod_scalaire):.5f}")


fig, ax = plt.subplots(figsize=(12, 6))

# Tracé des points individuels (scatter)
# alpha=0.6 permet de voir les superpositions si des points sont proches
ax.scatter(rangs_cyclones, valeurs_aod_individuel, 
           color='darkorange', edgecolors='crimson', 
           s=25, alpha=0.6, linewidths=0.5, label="Cyclone individuel")

# Configuration des axes et du titre
ax.set_title("AOD moyen de chaque cyclone trié par intensité (ACE décroissant)", fontsize=14, fontweight="bold")
ax.set_xlabel("Rang du cyclone (Du plus énergétique [1] au moins énergétique [458])", fontsize=12)
ax.set_ylabel("AOD moyen du cyclone (Moyenne spatio-temporelle)", fontsize=12)

# Ajustement des limites pour un affichage propre
ax.set_xlim(0, len(cyclone_stats) + 5)
ax.set_ylim(bottom=0)

# Ajout d'une grille légère
ax.grid(axis='both', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()

ds.close()