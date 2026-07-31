import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


fichier_entree = "/cnrm/mosca/USERS/puyf/stage/data/composites/compo_cy_aod_1960-2024.nc"

print(f"📂 Chargement du fichier : {fichier_entree}")
ds = xr.open_dataset(fichier_entree)

numrec = ds["numrec"].values
numdat = ds["numdat"].values

indices_cyclones = np.where(numrec == 1)[0]
indices_limites = np.append(indices_cyclones, len(numrec))

print(f"🌪️ {len(indices_cyclones)} cyclones identifiés.")
print("⏳ Calcul de l'ACE et de l'AOD moyen pour CHAQUE cyclone...")

cyclone_stats = []
year_counter = {}

# 1. Boucle globale : Calcul ACE et AOD pour chaque cyclone
for i in range(len(indices_cyclones)):
    start_idx = indices_limites[i]
    end_idx = indices_limites[i+1]
    
    # --- Gestion de l'année ---
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

    # --- Calcul de l'ACE ---
    wind_cyclone = ds["wind_module"].isel(time=slice(start_idx, end_idx))
    v_max_ms = wind_cyclone.max(dim=["plev", "lat", "lon"]).values
    v_max_knots = v_max_ms * 1.94384
    ace = np.sum(v_max_knots**2) * 1e-4
    
    aod_moyen_cyclone = ds["aod"].isel(time=slice(start_idx, end_idx)).mean().values
    
    cyclone_stats.append({
        "nom": nom_cyclone, 
        "ace": ace,
        "aod": float(aod_moyen_cyclone)
    })
    
    
    if (i + 1) % 50 == 0 or (i + 1) == len(indices_cyclones):
        print(f"   -> {i + 1}/{len(indices_cyclones)} cyclones traités")


cyclone_stats.sort(key=lambda x: x["aod"], reverse=True)


max_cyclones = len(cyclone_stats)
paliers_X = list(range(10, max_cyclones + 1, 10))

valeurs_ace_moyen = []

print("\n📈 Calcul de l'ACE moyen par paliers de 10 cyclones les plus chargés en AOD...")

for X in paliers_X:
    top_X = cyclone_stats[:X]
    
    # On fait simplement la moyenne des valeurs d'ACE de ces X cyclones
    ace_moyen_groupe = np.mean([c["ace"] for c in top_X])
    valeurs_ace_moyen.append(ace_moyen_groupe)


fig, ax = plt.subplots(figsize=(10, 6))


ax.plot(paliers_X, valeurs_ace_moyen, marker='D', linestyle='-', color='steelblue', linewidth=2.5, markersize=6, markerfacecolor='navy')


ax.set_title("Évolution de l'ACE moyen en fonction de la charge en AOD (Poussières)", fontsize=14, fontweight="bold")
ax.set_xlabel("Nombre de cyclones pris en compte (Top X triés par AOD décroissant)", fontsize=12)
ax.set_ylabel("ACE Moyen ($10^4$ knots$^2$)", fontsize=12)


ax.set_ylim(bottom=0)


ax.grid(axis='both', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

ds.close()