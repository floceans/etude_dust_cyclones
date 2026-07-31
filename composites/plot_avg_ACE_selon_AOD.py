import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import os


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
    
    # --- Calcul de l'AOD moyen du cyclone ---
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
valeurs_aod_moyen_groupe = []

print("\n📈 Préparation des données pour les graphiques...")

# Pour le graphique 1 (Cumulatif)
for X in paliers_X:
    top_X = cyclone_stats[:X]
    ace_moyen_groupe = np.mean([c["ace"] for c in top_X])
    aod_moyen_groupe = np.mean([c["aod"] for c in top_X])
    
    valeurs_ace_moyen.append(ace_moyen_groupe)
    valeurs_aod_moyen_groupe.append(aod_moyen_groupe)

# Pour le graphique 2 (Individuel)
liste_aod = [c["aod"] for c in cyclone_stats]
liste_ace = [c["ace"] for c in cyclone_stats]


fig1, ax1 = plt.subplots(figsize=(14, 9))

ax1.plot(valeurs_aod_moyen_groupe, valeurs_ace_moyen, marker='D', linestyle='-', 
         color='steelblue', linewidth=2.5, markersize=8, markerfacecolor='navy')

ax1.set_title("Évolution de l'ACE moyen par groupes cumulatifs\n(Triés par AOD décroissant)", fontsize=21, fontweight="bold", pad=20)
ax1.set_xlabel("AOD moyen du groupe de cyclones", fontsize=21, labelpad=15)
ax1.set_ylabel("ACE moyen (10⁴ knots²)", fontsize=21, labelpad=15)

ax1.tick_params(axis='both', which='major', labelsize=21)
ax1.set_ylim(bottom=0)
ax1.invert_xaxis() # Les plus forts AOD (premiers paliers) à gauche
ax1.grid(axis='both', linestyle='--', alpha=0.7)

fig1.tight_layout()



if len(cyclone_stats) > 1:
    fig2, ax2 = plt.subplots(figsize=(14, 9))

    # Nuage de points
    ax2.scatter(liste_aod, liste_ace, color='mediumseagreen', edgecolors='black', 
                s=70, alpha=0.5, linewidths=1, label="Cyclones")

    # Calcul de la régression (ACE en fonction de l'AOD)
    pente, ordonnee = np.polyfit(liste_aod, liste_ace, 1)
    
    # Calcul du R²
    y_pred = pente * np.array(liste_aod) + ordonnee
    ss_res = np.sum((np.array(liste_ace) - y_pred) ** 2)
    ss_tot = np.sum((np.array(liste_ace) - np.mean(liste_ace)) ** 2)
    r_deux = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    # Impression dans la console
    print("\n Paramètres de la régression linéaire (ACE = a * AOD + b) :")
    print(f"   Pente (a) = {pente:.2e}")
    print(f"   Ordonnée (b) = {ordonnee:.3f}")
    print(f"   R² = {r_deux:.3f}")

    # Tracé de la régression
    x_regression = np.linspace(min(liste_aod), max(liste_aod), 100)
    y_regression = pente * x_regression + ordonnee
    
    texte_loi = f"Régression : y = {pente:.2e}x + {ordonnee:.3f}\nR² = {r_deux:.3f}"
    ax2.plot(x_regression, y_regression, color='darkred', linestyle='--', 
             linewidth=3, label=texte_loi)

    # Configuration des textes
    ax2.set_title("ACE en fonction de l'AOD pour chaque cyclone", fontsize=21, fontweight="bold", pad=20)
    ax2.set_xlabel("AOD moyen du cyclone", fontsize=21, labelpad=15)
    ax2.set_ylabel("ACE du cyclone (10⁴ knots²)", fontsize=21, labelpad=15)

    ax2.tick_params(axis='both', which='major', labelsize=21)
    ax2.legend(fontsize=21, loc="upper left")
    
    ax2.set_ylim(bottom=0)
    ax2.invert_xaxis() # Conserver la même dynamique de lecture (Forts AOD à gauche)
    ax2.grid(axis='both', linestyle='--', alpha=0.5)

    fig2.tight_layout()


plt.show()

ds.close()