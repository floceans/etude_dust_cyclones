import numpy as np 
import xarray as xr 
import matplotlib.pyplot as plt 
import os 


fichier_entree = "/cnrm/mosca/USERS/puyf/NO_SAVE/composites/compo_cy_aod_1960-2024.nc" 
seuil_aod = 0.0515  # Seuil d'AOD minimal pour conserver un cyclone

print(f"📂 Chargement du fichier : {fichier_entree}") 
ds = xr.open_dataset(fichier_entree) 

# Récupération des variables 
numrec = ds["numrec"].values 
numdat = ds["numdat"].values 

# 1. Identification des frontières de chaque cyclone 
indices_cyclones = np.where(numrec == 1)[0] 
indices_limites = np.append(indices_cyclones, len(numrec)) 

print(f"🌪️ {len(indices_cyclones)} cyclones identifiés au total. Filtrage et calcul de l'ACE en cours...") 

cyclone_stats = [] 
year_counter = {} 

# 2. Boucle sur chaque cyclone avec filtrage par l'AOD
for i in range(len(indices_cyclones)): 
    start_idx = indices_limites[i] 
    end_idx = indices_limites[i+1] 
     
    # 2a. Calcul de l'AOD moyen pour CE cyclone (temporel + spatial)
    aod_cyclone = ds["aod"].isel(time=slice(start_idx, end_idx)) 
    aod_moyen_cyclone = float(aod_cyclone.mean(dim=["time", "lat", "lon"]).values)
    
    # Filtrage : si l'AOD moyen ne dépasse pas le seuil, on néglige le cyclone
    if aod_moyen_cyclone <= seuil_aod:
        continue

    # 2b. Identification de l'année (uniquement pour les cyclones conservés)
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

    # 2c. Calcul de l'ACE
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

print(f"✅ {len(cyclone_stats)} cyclones conservés après filtrage (AOD > {seuil_aod}).")

# 3. Tri des résultats du plus fort au plus faible ACE 
cyclone_stats.sort(key=lambda x: x["ace"], reverse=True) 


max_cyclones = len(cyclone_stats) 
paliers_X = list(range(10, max_cyclones + 1, 10)) 

valeurs_aod_moyen = [] 
valeurs_ace_moyen = [] # Nouvelle liste pour stocker l'ACE

print("\n📈 Calcul de l'AOD moyen et de l'ACE moyen par paliers cumulatifs...") 

for X in paliers_X: 
    top_X = cyclone_stats[:X] 
      
    # Calcul de l'ACE moyen pour ce groupe de cyclones
    ace_moyen_groupe = np.mean([c["ace"] for c in top_X])
    valeurs_ace_moyen.append(ace_moyen_groupe)
    
    indices_temps = [] 
    for c in top_X: 
        indices_temps.extend(range(c["start_idx"], c["end_idx"])) 
          
    aod_scalaire = ds["aod"].isel(time=indices_temps).mean(dim=["time", "lat", "lon"]).values 
    valeurs_aod_moyen.append(aod_scalaire) 
      
    print(f"   Top {X:03d} cyclones -> ACE moyen = {ace_moyen_groupe:.2f} | AOD spatial moyen = {float(aod_scalaire):.5f}") 


if len(valeurs_ace_moyen) > 0:
    fig, ax = plt.subplots(figsize=(12, 8)) # Taille augmentée pour accommoder la grande police

    ax.plot(valeurs_ace_moyen, valeurs_aod_moyen, marker='o', linestyle='-', 
            color='darkorange', linewidth=2.5, markersize=8, 
            markerfacecolor='crimson') 

    # Application de la taille 21 aux textes
    ax.set_title(f"Évolution de l'AOD en fonction de l'ACE moyen des cyclones\n(Groupes cumulatifs, Seuil AOD > {seuil_aod})", fontsize=21, fontweight="bold", pad=20) 
    ax.set_xlabel("ACE moyen du groupe de cyclones", fontsize=21, labelpad=15) 
    ax.set_ylabel("AOD moyen (moyenne spatio-temporelle)", fontsize=21, labelpad=15) 

    # Application de la taille 21 aux valeurs des graduations (ticks)
    ax.tick_params(axis='both', which='major', labelsize=21)

    # Inverser l'axe X : les ACE les plus forts s'affichent à gauche
    ax.invert_xaxis() 

    # Imposer l'échelle de l'axe Y de 0.4 à 0.9
    ax.set_ylim(0.05, 0.15) 

    ax.grid(axis='both', linestyle='--', alpha=0.7) 

    plt.tight_layout() 
    plt.show() 
else:
    print("\nPas assez de cyclones restants pour générer le graphique.")

ds.close()