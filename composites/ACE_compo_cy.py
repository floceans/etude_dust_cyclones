import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


fichier_entree = "/cnrm/mosca/USERS/puyf/NO_SAVE/composites/compo_cy_aod_1960-2024.nc"
Nombre_Top_X = 458

print(f"📂 Chargement du fichier : {fichier_entree}")
ds = xr.open_dataset(fichier_entree)

numrec = ds["numrec"].values
numdat = ds["numdat"].values


indices_cyclones = np.where(numrec == 1)[0]
indices_limites = np.append(indices_cyclones, len(numrec))

print(f"🌪️ {len(indices_cyclones)} cyclones identifiés. Calcul de l'ACE en cours...")

cyclone_stats = []
year_counter = {}


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


cyclone_stats.sort(key=lambda x: x["ace"], reverse=True)
top_X = cyclone_stats[:Nombre_Top_X]

print(f"\n🔥 TOP {Nombre_Top_X} des cyclones les plus intenses :")
for c in top_X:
    print(f"   {c['nom']} : ACE = {c['ace']:.2f}")


print(f"\n🌍 Calcul de l'AOD moyen sur les pas de temps des {Nombre_Top_X} cyclones...")
indices_top_x_temps = []
for c in top_X:
    indices_top_x_temps.extend(range(c["start_idx"], c["end_idx"]))

aod_top_x_moyen = ds["aod"].isel(time=indices_top_x_temps).mean(dim="time")


fig = plt.figure(figsize=(16, 6))

ax1 = fig.add_subplot(1, 2, 1)
noms = [c["nom"] for c in top_X]
aces = [c["ace"] for c in top_X]

ax1.bar(noms, aces, color="crimson", edgecolor="black")
ax1.set_title(f"Top {Nombre_Top_X} : Cyclones les plus intenses (ACE)", fontsize=14, fontweight="bold")
ax1.set_ylabel("Accumulated Cyclone Energy ($10^4$ knots$^2$)", fontsize=12)
ax1.set_xlabel("Identifiant du cyclone", fontsize=12)


ax1.set_ylim(0, 110)

ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis="y", linestyle="--", alpha=0.7)

ax2 = fig.add_subplot(1, 2, 2)
lons = ds["lon"].values
lats = ds["lat"].values


niveaux_aod = np.linspace(0, 0.1, 21)
carte_aod = ax2.contourf(lons, lats, aod_top_x_moyen, levels=niveaux_aod, cmap="YlOrBr", extend="both")


cbar = fig.colorbar(carte_aod, ax=ax2)
cbar.set_label("Aerosol Optical Depth (Dust) Moyen", fontsize=12)
cbar.set_ticks(np.linspace(0, 0.1, 6)) # Graduations propres de 0 à 0.1 tous les 0.02

ax2.set_title(f"AOD Moyen associé au Top {Nombre_Top_X}", fontsize=14, fontweight="bold")
ax2.set_xlabel("Longitude", fontsize=12)
ax2.set_ylabel("Latitude", fontsize=12)

plt.tight_layout()
plt.show()

ds.close()