from fonc import plot_relation, load_data, plot_bar_charts

DATA = 'ibtracs' #'aladin' 

if DATA == 'ibtracs':
    filename = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/ibtracs_transformed_1960_2024.csv'
elif DATA == 'aladin':
    filename = '/home/florent/Documents/CNRM/git/etude_dust_cyclones/aladin_transformed_1960_2024.csv'

vmax, pmin, vomax = load_data(filename)

print(f"Nombre de données valides : {len(vmax)}")
print(f"nbr pmin valides : {len(pmin)}")
print(f"nbr vomax valides : {len(vomax)}")

if not vmax:
    print("Attention : Aucune donnée ne correspond aux critères (pmin présent et vomax != 0).")
else:
    # 1. Diagrammes bâtons
    plot_bar_charts(vmax, pmin, vomax, DATA)
    
    # 2. Relation Pmin / Vmax
    plot_relation(pmin, vmax, "Pression Minimale (hPa)", "Vitesse Vent (vmax)", DATA)
    
    # 3. Relation Vorticité / Vmax
    plot_relation(vomax, vmax, "Vorticité (vomax)", "Vitesse Vent (vmax)", DATA)
    
    # 4. Relation Vorticité / Pmin
    plot_relation(vomax, pmin, "Vorticité (vomax)", "Pression Minimale (hPa)", DATA)