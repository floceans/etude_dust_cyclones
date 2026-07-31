import os
import numpy as np
import xarray as xr


annee_min = 1960
annee_max = 1961

fichier_sortie = f"compo_cy_aod_{annee_min}-{annee_max}.nc"
# ==============================================================================


datasets_global = []

print(f"🚀 Début du traitement global de {annee_min} à {annee_max}...")


for annee in range(annee_min, annee_max):
    periode = f"{annee}-{annee + 1}"

    
    fichier_ua = f"/cnrm/mosca/USERS/puyf/stage/data/composites/vents/compo_3D_ua_{periode}.ERA5_evaluation_rel10.nc"
    fichier_va = f"/cnrm/mosca/USERS/puyf/stage/data/composites/vents/compo_3D_va_{periode}.ERA5_evaluation_rel10.nc"
    fichier_aod = f"/cnrm/mosca/USERS/puyf/stage/data/composites/dust/compo_2D_od550dust_{periode}.ERA5_evaluation_rel10.nc"

    
    if not (
        os.path.exists(fichier_ua)
        and os.path.exists(fichier_va)
        and os.path.exists(fichier_aod)
    ):
        print(
            f"⚠️ Période {periode} ignorée : un ou plusieurs fichiers manquants (UA, VA ou AOD)."
        )
        continue

    print(f"\n[Traitement] Période {periode} en cours...")

    try:
        
        ds_ua = xr.open_dataset(fichier_ua)
        ds_va = xr.open_dataset(fichier_va)
        ds_aod = xr.open_dataset(fichier_aod)

        
        numrec_ua = ds_ua["numrec"].values
        numrec_va = ds_va["numrec"].values
        numrec_aod = ds_aod["numrec"].values

        if not np.array_equal(numrec_ua, numrec_va):
            print(
                f"   ❌ Erreur de synchronisation UA/VA sur la période {periode} !"
            )

        if not np.array_equal(numrec_ua, numrec_aod):
            print(
                f"   ❌ Mismatch 'numrec' détecté sur la période {periode} entre le Vent et l'AOD !"
            )
            # Localisation des indices problématiques
            indices_diff = np.where(numrec_ua != numrec_aod)[0]
            print(
                f"   -> Désaccord sur {len(indices_diff)} pas de temps. Premiers indices : {indices_diff[:5]}"
            )

        #  Calcul du module du vent
        ua = ds_ua["tccmp"]
        va = ds_va["tccmp"]
        wind_module = np.sqrt(ua**2 + va**2)

        
        wind_module.attrs["long_name"] = "Module du vent (Wind speed module)"
        wind_module.attrs["units"] = ua.attrs.get("units", "m s-1")
        wind_module.attrs["_FillValue"] = ua.attrs.get("_FillValue", 1.e20)

        
        aod = ds_aod["tccmp"].rename("aod")
        aod.attrs["long_name"] = "Aerosol Optical Depth (Dust)"
        aod.attrs["units"] = ds_aod["tccmp"].attrs.get("units", "Unknown")

        
        ds_periode = xr.Dataset(
            data_vars={
                "wind_module": wind_module,  # 4D: (time, plev, lat, lon)
                "aod": aod,  # 3D: (time, lat, lon)
                "numrec": ds_ua["numrec"],  # On garde le numrec de cette période
                "numdat": ds_ua["numdat"],
                "tclon": ds_ua["tclon"],
                "tclat": ds_ua["tclat"],
            }
        )

        
        datasets_global.append(ds_periode)
        print(f"   ➔ Période {periode} traitée et mise en mémoire.")

    except Exception as e:
        print(f"   💥 Une erreur est survenue lors du traitement de {periode} : {e}")


if datasets_global:
    print("\n--- Concaténation de toutes les années chargées ---")
    # Concaténation
    ds_final = xr.concat(datasets_global, dim="time")

    
    ds_final.attrs["description"] = (
        f"Composites de cyclones fusionnés de {annee_min} à {annee_max}"
    )
    ds_final.attrs["history"] = (
        "Calcul du module du vent et fusion avec l'AOD via Xarray."
    )

    print(f"💾 Écriture du fichier final unique : '{fichier_sortie}'...")
    ds_final.to_netcdf(fichier_sortie)
    print("Opération terminée avec succès ! Le fichier est prêt.")
else:
    print("Erreur : Aucun fichier valide n'a pu être traité.")