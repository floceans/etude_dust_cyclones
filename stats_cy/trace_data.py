import matplotlib.pyplot as plt
from fonc import (
    diff_bar_chart,
    load_data,
    load_data_max,
    plot_bar_charts,
    plot_relation,
    plot_vmax_pmin_time,
)

# --- CONFIGURATION GLOBALE DE LA POLICE ---
plt.rcParams.update({
    'font.size': 23,          # Taille pour tout le texte (titres, axes, graduations)
    'legend.fontsize': 18     # Exception : Taille réduite à 18 uniquement pour la légende
})
# ------------------------------------------

DATA_1 = "ALADIN NoRadDust"
DATA_2 = "ALADIN Ref"
SEUIL_VORTICITE = 0
SEUIL_VENT = 26
SEUIL_PRESSION = 1005

filename_1 = "/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv"
svort_1 = 0
spress_1 = 1005
svent_1 = 26

filename_2 = "/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv"
svort_2 = SEUIL_VORTICITE
spress_2 = SEUIL_PRESSION
svent_2 = SEUIL_VENT

################### PRENDRE EN COMPTE SEUIL VORT #########################

vmax_1, pmin_1, vomax_1 = load_data(
    filename_1, svort_1, spress_1, svent_1, 1960, 2000
)
vmax_2, pmin_2, vomax_2 = load_data(
    filename_2, svort_2, spress_2, svent_2, 1960, 2000
)

vmax_max_1, pmin_min_1 = load_data_max(filename_1, svent_2, spress_2)
vmax_max_2, pmin_min_2 = load_data_max(filename_2, svent_2, spress_2)

"""
print(f"Nombre de données valides : {len(vmax)}")
print(f"nbr pmin valides : {len(pmin)}")
print(f"nbr vomax valides : {len(vomax)}")
"""

if False:
    print(
        "Attention : Aucune donnée ne correspond aux critères (pmin présent et vomax != 0)."
    )
else:
    # 1. Diagrammes bâtons
    # plot_bar_charts(vmax_2, pmin_2, vomax=vomax_2, filename = 'ALADIN_NoRadDust')

    diff_bar_chart(
        vmax_1,
        pmin_1,
        vomax_1,
        vmax_2,
        pmin_2,
        vomax_2,
        labela="ALADIN NoRadDust - ALADIN Ref",
    )

    # 2. Relation Pmin / Vmax

    fig, my_ax = plt.subplots(figsize=(10, 6))
    plot_relation(pmin_min_2, vmax_max_2, "ALADIN Ref", ax=my_ax, color="blue")
    plot_relation(
        pmin_min_1, vmax_max_1, "ALADIN NoRadDust", ax=my_ax, color="red"
    )
    
    plt.show()

    # 3. Relation Vorticité / Vmax
    # plot_relation(vomax, vmax, "Vorticité (vomax)", "Vitesse Vent (vmax)", DATA)

    # 4. Relation Vorticité / Pmin
    # plot_relation(vomax, pmin, "Vorticité (vomax)", "Pression Minimale (hPa)", DATA)

    # plot_vmax_pmin_time(filename, an_min=2020, an_max=2020)
    plt.show()