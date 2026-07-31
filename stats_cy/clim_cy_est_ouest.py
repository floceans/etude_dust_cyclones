
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# Fichiers à modifier selon ton arborescence
file_ref = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN_rel10_1960_2024.csv'
file_norad = '/cnrm/mosca/USERS/puyf/stage/data/tracks/ALADIN-NoRadDust-rel10_1960_2000.csv'


YEAR_MIN, YEAR_MAX = 1960, 2000
FS = 22  # Taille de police globale fixée à 22


def analyze_cyclogenesis(input_csv, year_min, year_max, sim_name, threshold=26, cat3_threshold=49.4, lat_max=25, lon_min=-60):
    if not os.path.exists(input_csv):
        print(f"ATTENTION : Fichier introuvable - {input_csv}")
        return None, None

    df = pd.read_csv(input_csv)
    
    step_col = 'step' if 'step' in df.columns else df.columns[1]
    df['cyclone_id'] = (df[step_col] == 1).cumsum()

    if 'date' in df.columns:
        df['year'] = pd.to_datetime(df['date']).dt.year
    else:
        print(f"ATTENTION : Colonne 'date' introuvable dans {input_csv}.")
        return None, None

    stats = {
        'East_Weak': 0, 'East_Strong': 0,
        'West_Weak': 0, 'West_Strong': 0
    }
    
    points_map = [] 

    for cid, group in df.groupby('cyclone_id'):
        genesis_points = group[group['vmax'] > threshold]
        
        if genesis_points.empty:
            continue
            
        first_point = genesis_points.iloc[0]
        
        genesis_year = first_point['year']
        if not (year_min <= genesis_year <= year_max):
            continue
        
        lon = first_point['lon']
        lat = first_point['lat']
        if lon > 180:
            lon -= 360  
            
        if lat > lat_max or lon < lon_min:
            continue

        max_vmax = group['vmax'].max()

        is_east = lon > -30
        is_strong = max_vmax >= cat3_threshold

        if is_east:
            if is_strong: stats['East_Strong'] += 1
            else: stats['East_Weak'] += 1
        else:
            if is_strong: stats['West_Strong'] += 1
            else: stats['West_Weak'] += 1
            
        points_map.append({
            'lon': lon,
            'lat': lat,
            'is_strong': is_strong,
            'is_east': is_east,
            'sim': sim_name
        })

    return stats, points_map


def plot_cyclogenesis_comparison(stats_ref, stats_norad, years_count):
    labels = [
        "Est\n(Cat $\leq$ 2)",
        "Est\n(Cat $\geq$ 3)",
        "Ouest\n(Cat $\leq$ 2)",
        "Ouest\n(Cat $\geq$ 3)"
    ]
    keys = ['East_Weak', 'East_Strong', 'West_Weak', 'West_Strong']

    ref_vals = [stats_ref[k] / years_count for k in keys]
    norad_vals = [stats_norad[k] / years_count for k in keys]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(x - width/2, ref_vals, width, color='steelblue', label='REF')
    ax.bar(x + width/2, norad_vals, width, color='indianred', label='NoRadDust')

    ax.set_ylabel("Nb moyen / an", fontsize=FS)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=FS)
    ax.tick_params(axis='y', labelsize=FS)
    ax.legend(fontsize=FS)
    ax.grid(axis='y', linestyle='--', alpha=0.4)

    for i, (v_ref, v_norad) in enumerate(zip(ref_vals, norad_vals)):
        ax.text(x[i] - width/2, v_ref + 0.05, f"{v_ref:.2f}", ha='center', va='bottom', fontsize=FS, fontweight='bold', color='steelblue')
        ax.text(x[i] + width/2, v_norad + 0.05, f"{v_norad:.2f}", ha='center', va='bottom', fontsize=FS, fontweight='bold', color='indianred')

    ax.set_ylim(0, max(max(ref_vals), max(norad_vals)) * 1.2)
    plt.tight_layout()
    plt.show()


def plot_cyclogenesis_map(points_ref, points_norad):
    fig, ax = plt.subplots(figsize=(16, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    
    ax.set_extent([-100, 20, 0, 45], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax.add_feature(cfeature.BORDERS, linewidth=1, linestyle=':')
    ax.add_feature(cfeature.LAND, facecolor='whitesmoke')
    ax.add_feature(cfeature.OCEAN, facecolor='aliceblue')

    gl = ax.gridlines(draw_labels=True, linestyle='--', color='gray', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': FS}
    gl.ylabel_style = {'size': FS}

    ax.axhline(25, color='darkgreen', linestyle='-', linewidth=3, zorder=3, label='Limite N (25°N)')
    ax.axvline(-60, color='darkviolet', linestyle='-', linewidth=3, zorder=3, label='Limite W (-60°W)')
    ax.axvline(-30, color='black', linestyle='--', linewidth=3, zorder=3, label='Limite E/W (-30°W)')

    legends_done = set()
    all_points = points_ref + points_norad

    for p in all_points:
        marker = 'o' if p['sim'] == 'REF' else '^'
        color = 'firebrick' if p['is_strong'] else 'royalblue'
        
        sim_label = "REF" if p['sim'] == 'REF' else "NoRadDust"
        cat_label = "Cat $\geq$ 3" if p['is_strong'] else "Cat $\leq$ 2"
        label = f"{sim_label} ({cat_label})"
        
        if label not in legends_done:
            ax.scatter(p['lon'], p['lat'], marker=marker, color=color, s=120, alpha=0.7, 
                       transform=ccrs.PlateCarree(), label=label, zorder=4, edgecolor='k', linewidth=1)
            legends_done.add(label)
        else:
            ax.scatter(p['lon'], p['lat'], marker=marker, color=color, s=120, alpha=0.7, 
                       transform=ccrs.PlateCarree(), zorder=4, edgecolor='k', linewidth=1)

    ax.legend(loc='lower left', fontsize=FS, framealpha=0.9)
    plt.tight_layout()
    plt.show()


def plot_difference_comparison(stats_ref, stats_norad, years_count):
    labels = [
        "Est\n(Cat $\leq$ 2)",
        "Est\n(Cat $\geq$ 3)",
        "Ouest\n(Cat $\leq$ 2)",
        "Ouest\n(Cat $\geq$ 3)"
    ]
    keys = ['East_Weak', 'East_Strong', 'West_Weak', 'West_Strong']

    diff_vals = [(stats_norad[k] - stats_ref[k]) / years_count for k in keys]

    x = np.arange(len(labels))
    width = 0.5

    fig, ax = plt.subplots(figsize=(14, 8))
    
    colors = ['seagreen' if v >= 0 else 'crimson' for v in diff_vals]
    ax.bar(x, diff_vals, width, color=colors, edgecolor='black', linewidth=1.2)

    ax.set_ylabel("Différence (NoRadDust - REF)\nNb moyen / an", fontsize=FS)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=FS)
    ax.tick_params(axis='y', labelsize=FS)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.axhline(0, color='black', linewidth=2)

    for i, v in enumerate(diff_vals):
        va = 'bottom' if v >= 0 else 'top'
        offset = 0.05 if v >= 0 else -0.05
        ax.text(x[i], v + offset, f"{v:+.2f}", ha='center', va=va, fontsize=FS, fontweight='bold', color=colors[i])

    y_min, y_max = ax.get_ylim()
    margin = max(abs(y_min), abs(y_max)) * 0.2
    ax.set_ylim(y_min - margin if y_min < 0 else 0, y_max + margin if y_max > 0 else 0)

    plt.tight_layout()
    plt.show()


def plot_proportions(stats_ref, stats_norad):
    """
    Trace un diagramme en barres empilées à 100% montrant la proportion
    de cyclones puissants vs peu puissants pour chaque simulation et zone.
    """
    # Calcul des totaux par zone et par simulation
    tot_ref_east = stats_ref['East_Weak'] + stats_ref['East_Strong']
    tot_norad_east = stats_norad['East_Weak'] + stats_norad['East_Strong']
    tot_ref_west = stats_ref['West_Weak'] + stats_ref['West_Strong']
    tot_norad_west = stats_norad['West_Weak'] + stats_norad['West_Strong']

    # Sécurité pour éviter les divisions par zéro
    pct_ref_east_w = (stats_ref['East_Weak'] / tot_ref_east * 100) if tot_ref_east > 0 else 0
    pct_ref_east_s = (stats_ref['East_Strong'] / tot_ref_east * 100) if tot_ref_east > 0 else 0
    
    pct_norad_east_w = (stats_norad['East_Weak'] / tot_norad_east * 100) if tot_norad_east > 0 else 0
    pct_norad_east_s = (stats_norad['East_Strong'] / tot_norad_east * 100) if tot_norad_east > 0 else 0
    
    pct_ref_west_w = (stats_ref['West_Weak'] / tot_ref_west * 100) if tot_ref_west > 0 else 0
    pct_ref_west_s = (stats_ref['West_Strong'] / tot_ref_west * 100) if tot_ref_west > 0 else 0
    
    pct_norad_west_w = (stats_norad['West_Weak'] / tot_norad_west * 100) if tot_norad_west > 0 else 0
    pct_norad_west_s = (stats_norad['West_Strong'] / tot_norad_west * 100) if tot_norad_west > 0 else 0

    labels = ['Est\n(REF)', 'Est\n(NoRad)', 'Ouest\n(REF)', 'Ouest\n(NoRad)']
    weak_pcts = [pct_ref_east_w, pct_norad_east_w, pct_ref_west_w, pct_norad_west_w]
    strong_pcts = [pct_ref_east_s, pct_norad_east_s, pct_ref_west_s, pct_norad_west_s]

    x = np.arange(len(labels))
    width = 0.5

    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Barres empilées
    ax.bar(x, weak_pcts, width, label='Cat $\leq$ 2', color='royalblue', edgecolor='black')
    ax.bar(x, strong_pcts, width, bottom=weak_pcts, label='Cat $\geq$ 3', color='firebrick', edgecolor='black')

    ax.set_ylabel("Proportion (%)", fontsize=FS)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=FS)
    ax.tick_params(axis='y', labelsize=FS)
    ax.set_ylim(0, 100)
    
    # Écriture des pourcentages au milieu de chaque bloc
    for i in range(len(labels)):
        if weak_pcts[i] > 5: # On n'affiche le texte que si la barre est visible
            ax.text(x[i], weak_pcts[i]/2, f"{weak_pcts[i]:.1f}%", ha='center', va='center', fontsize=FS, fontweight='bold', color='white')
        if strong_pcts[i] > 5:
            ax.text(x[i], weak_pcts[i] + strong_pcts[i]/2, f"{strong_pcts[i]:.1f}%", ha='center', va='center', fontsize=FS, fontweight='bold', color='white')

    # Légende placée en haut, au centre, en dehors du graphe pour ne rien masquer
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fontsize=FS, frameon=False)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    years_count = YEAR_MAX - YEAR_MIN + 1

    print("Analyse de la simulation REF...")
    stats_ref, pts_ref = analyze_cyclogenesis(file_ref, YEAR_MIN, YEAR_MAX, sim_name="REF", lat_max=25, lon_min=-60)
    
    print("\nAnalyse de la simulation NoRadDust...")
    stats_norad, pts_norad = analyze_cyclogenesis(file_norad, YEAR_MIN, YEAR_MAX, sim_name="NoRadDust", lat_max=25, lon_min=-60)

    if stats_ref and stats_norad:
        print(f"\nTotal REF retenus : {sum(stats_ref.values())} | Total NoRad retenus : {sum(stats_norad.values())}")
        
        # 1. Tracé de l'histogramme classique
        plot_cyclogenesis_comparison(stats_ref, stats_norad, years_count)
        
        # 2. Tracé de la carte
        plot_cyclogenesis_map(pts_ref, pts_norad)
        
        # 3. Tracé de la différence (NoRadDust - REF)
        plot_difference_comparison(stats_ref, stats_norad, years_count)
        
        # 4. Tracé des proportions (Empilé 100%)
        plot_proportions(stats_ref, stats_norad)