from fonc import plot_relation, load_data, plot_bar_charts, plot_vmax_pmin_time, load_data_max

DATA = 'ibtracs' #'ibtracs'
SEUIL_VORTICITE = 0
SEUIL_VENT = 28
SEUIL_PRESSION = 1005


if DATA == 'ibtracs':
    filename = 'ibtracs_transformed_1960_2024.csv'
    svort = 0
    spress = 2000
    svent = 0
elif DATA == 'aladin':
    filename = 'ALADIN_rel10_1960_2024.csv'
    svort = SEUIL_VORTICITE
    spress = SEUIL_PRESSION
    svent = SEUIL_VENT


###################PRENDRE EN COMPTE SEUIL VORT #########################


vmax, pmin, vomax = load_data(filename, svort, spress, svent)
vmax_max, pmin_min = load_data_max(filename, svent, spress)

print(f"Nombre de données valides : {len(vmax)}")
print(f"nbr pmin valides : {len(pmin)}")
print(f"nbr vomax valides : {len(vomax)}")

if not vmax:
    print("Attention : Aucune donnée ne correspond aux critères (pmin présent et vomax != 0).")
else:
    # 1. Diagrammes bâtons
    #plot_bar_charts(vmax, pmin, vomax, DATA)
    
    # 2. Relation Pmin / Vmax
    
    plot_relation(pmin_min, vmax_max, DATA)
    
    # 3. Relation Vorticité / Vmax
    #plot_relation(vomax, vmax, "Vorticité (vomax)", "Vitesse Vent (vmax)", DATA)
    
    # 4. Relation Vorticité / Pmin
    #plot_relation(vomax, pmin, "Vorticité (vomax)", "Pression Minimale (hPa)", DATA)

    #plot_vmax_pmin_time(filename, an_min=2020, an_max=2020)