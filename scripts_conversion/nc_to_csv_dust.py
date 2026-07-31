import netCDF4 as nc
import csv
import os

# --- CONFIGURATION ---
# Liste des périodes (les parties qui changent dans le nom du fichier)
dates_a_traiter = ["196001-196012", "196101-197012", "197101-198012", '198101-199012', "199101-200012", "200101-201012", "201101-202012", "202101-202312"] 

# Template du nom de fichier (on utilise {} pour insérer la date)
template_nom = "/home/puyf/Documents/dust_brut_1/aladin/od550aer_CAM-25_ERA5_evaluation_r1i1p1f1_CNRM_CNRM-ALADIN64C1_v1-r1_mon_{}.nc"
fichier_final = "aladin_aer_mensuel_1960-2024.nc"


def concatener_netcdf_correct(liste_dates, nom_sortie):
    f_out = None
    time_idx_offset = 0

    for i, date_str in enumerate(liste_dates):
        nom_entree = template_nom.format(date_str)
        
        if not os.path.exists(nom_entree):
            print(f"⚠️ Fichier manquant : {nom_entree}")
            continue

        print(f"⏳ Traitement de : {nom_entree}...")
        ds_in = nc.Dataset(nom_entree, 'r')

        if f_out is None:
            # 1. INITIALISATION DU FICHIER DE SORTIE (au premier fichier)
            f_out = nc.Dataset(nom_sortie, 'w', format='NETCDF4')
            
            # Copie des attributs globaux
            f_out.setncatts({k: ds_in.getncattr(k) for k in ds_in.ncattrs()})

            # Copie des dimensions
            for name, dim in ds_in.dimensions.items():
                # On rend la dimension 'time' illimitée pour la concaténation
                f_out.createDimension(name, (None if name == 'time' else len(dim)))

            # Création de TOUTES les variables avec leurs attributs
            for name, var_in in ds_in.variables.items():
                var_out = f_out.createVariable(name, var_in.datatype, var_in.dimensions)
                var_out.setncatts({k: var_in.getncattr(k) for k in var_in.ncattrs()})
                
                # Si la variable ne dépend PAS du temps (ex: lat, lon, bnds), on la copie tout de suite
                if 'time' not in var_in.dimensions:
                    var_out[:] = var_in[:]

        # 2. REMPLISSAGE DES DONNÉES TEMPORELLES
        t_len = len(ds_in.dimensions['time'])
        
        # On cherche toutes les variables qui ont 'time' comme dimension
        for name, var_in in ds_in.variables.items():
            if 'time' in var_in.dimensions:
                var_out = f_out.variables[name]
                
                # Gestion de l'index de départ selon le nombre de dimensions
                # Fonctionne pour 'time', 'time_bnds' (2D) et 'od550dust' (3D)
                if len(var_in.dimensions) == 1: # ex: time
                    var_out[time_idx_offset : time_idx_offset + t_len] = var_in[:]
                elif len(var_in.dimensions) == 2: # ex: time_bnds
                    var_out[time_idx_offset : time_idx_offset + t_len, :] = var_in[:]
                elif len(var_in.dimensions) == 3: # ex: od550dust (time, lat, lon)
                    var_out[time_idx_offset : time_idx_offset + t_len, :, :] = var_in[:]
        
        time_idx_offset += t_len
        ds_in.close()

    if f_out:
        f_out.close()
        print(f"✨ Concaténation réussie : {nom_sortie}")

# Lancement
concatener_netcdf_correct(dates_a_traiter, fichier_final)