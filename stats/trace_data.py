from fonc import plot_relation, load_data, plot_bar_charts, plot_vmax_pmin_time, load_data_max
import matplotlib.pyplot as plt

DATA_1 = 'ibtracs' 
DATA_2 = 'aladin' 
SEUIL_VORTICITE = 0
SEUIL_VENT = 28
SEUIL_PRESSION = 1005



filename_1 = 'ibtracs_transformed_1960_2024.csv'
svort_1 = 0
spress_1 = 2000
svent_1 = 0

filename_2 = 'ALADIN_rel10_1960_2024.csv'
svort_2 = SEUIL_VORTICITE
spress_2 = SEUIL_PRESSION
svent_2 = SEUIL_VENT


###################PRENDRE EN COMPTE SEUIL VORT #########################


#vmax_1, pmin_1, vomax_1 = load_data(filename_1, svort_1, spress_1, svent_1)
#vmax_2, pmin_2, vomax_2 = load_data(filename_2, svort_2, spress_2, svent_2)


vmax_max_1, pmin_min_1 = load_data_max(filename_1, svent_1, spress_1)
vmax_max_2, pmin_min_2 = load_data_max(filename_2, svent_2, spress_2)

"""
print(f"Nombre de données valides : {len(vmax)}")
print(f"nbr pmin valides : {len(pmin)}")
print(f"nbr vomax valides : {len(vomax)}")
"""

if False:
    print("Attention : Aucune donnée ne correspond aux critères (pmin présent et vomax != 0).")
else:
    # 1. Diagrammes bâtons
    #plot_bar_charts(vmax, pmin, vomax, DATA)
    
    # 2. Relation Pmin / Vmax
    

    fig, my_ax = plt.subplots(figsize=(10, 6))
    plot_relation(pmin_min_1, vmax_max_1, "ibtracs", ax=my_ax, color='blue')
    plot_relation(pmin_min_2, vmax_max_2, "Aladin", ax=my_ax, color='red')
    plt.show()
    
    
    # 3. Relation Vorticité / Vmax
    #plot_relation(vomax, vmax, "Vorticité (vomax)", "Vitesse Vent (vmax)", DATA)
    
    # 4. Relation Vorticité / Pmin
    #plot_relation(vomax, pmin, "Vorticité (vomax)", "Pression Minimale (hPa)", DATA)

    #plot_vmax_pmin_time(filename, an_min=2020, an_max=2020)
    plt.show()