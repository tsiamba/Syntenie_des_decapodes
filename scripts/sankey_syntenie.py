import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 1. GESTION DES DOSSIERS
# ==========================================
BUSCO_BASE_DIR = "../busco_metaeuk/busco_output"
LINEAGE_DIR = "run_arthropoda_odb10"

SANKEY_BASE_DIR = "../Diagramme_Sankey/Metaeuk"
DIR_OUTPUT = os.path.join(SANKEY_BASE_DIR, "output")
DIR_CHR = os.path.join(SANKEY_BASE_DIR, "busco_chr_organisme")

os.makedirs(DIR_OUTPUT, exist_ok=True)
os.makedirs(DIR_CHR, exist_ok=True)

# --- PARAMÈTRES DE NETTOYAGE ---
MIN_GENES_POUR_CHR = 1
AFFICHER_PETITS_SCAFFOLDS = True

# ==========================================
# 2. EXTRACTION, RENOMMAGE ET CRÉATION DES CSV
# ==========================================
genome_names = []
all_genomes_data = []

print("Extraction et assignation des chromosomes...")
for folder in sorted(os.listdir(BUSCO_BASE_DIR)):
    if not folder.startswith("resultats_busco_"):
        continue
        
    genome_name = folder.replace("resultats_busco_", "")
    full_table_path = os.path.join(BUSCO_BASE_DIR, folder, LINEAGE_DIR, "full_table.tsv")
    
    if not os.path.exists(full_table_path):
        continue
        
    df = pd.read_csv(full_table_path, sep='\t', comment='#', header=None, 
                     names=['Busco_id', 'Status', 'Sequence', 'Start', 'End', 'Strand', 'Score', 'Length', 'OrthoDB', 'Desc'])
    
    df_comp = df[df['Status'] == 'Complete'].copy()
    
    counts = df_comp['Sequence'].value_counts()
    
    mapping = {}
    chr_idx = 1
    for seq, count in counts.items():
        if count >= MIN_GENES_POUR_CHR:
            mapping[seq] = f"Chr {chr_idx}"
            chr_idx += 1
        else:
            mapping[seq] = "Autres scaffolds"
            
    df_comp['Chromosome'] = df_comp['Sequence'].map(mapping)
    df_comp['Organisme'] = genome_name
    
    df_csv = df_comp[['Organisme', 'Chromosome', 'Sequence', 'Busco_id', 'Start', 'End', 'Strand']]
    
    csv_individuel = os.path.join(DIR_CHR, f"{genome_name}_chromosomes.csv")
    df_csv.to_csv(csv_individuel, index=False)
    
    if not AFFICHER_PETITS_SCAFFOLDS:
        df_csv = df_csv[df_csv['Chromosome'] != "Autres scaffolds"]
        
    all_genomes_data.append(df_csv)
    genome_names.append(genome_name)
    print(f" -> {genome_name} : {chr_idx-1} chromosomes identifiés.")

if len(all_genomes_data) < 2:
    print("Erreur : Au moins 2 génomes complets sont requis.")
    exit()

df_master = pd.concat(all_genomes_data, ignore_index=True)
master_csv_path = os.path.join(DIR_OUTPUT, "master_positions_busco.csv")
df_master.to_csv(master_csv_path, index=False)
print(f"\nMaster CSV sauvegardé : {master_csv_path}")

# ==========================================
# 3. PROPAGATION DES COULEURS ET SANKEY
# ==========================================
print("\nAnalyse de la conservation pour propagation des couleurs...")

base_colors = px.colors.qualitative.Alphabet + px.colors.qualitative.Dark24 

node_dict = {}
labels = []
node_colors = []
current_node_id = 0

def add_node(genome, chromosome, color):
    global current_node_id
    node_name = f"{genome}_{chromosome}"
    if node_name not in node_dict:
        node_dict[node_name] = current_node_id
        labels.append(f"{chromosome}")
        node_colors.append(color)
        current_node_id += 1
    return node_dict[node_name]

# Fonction pour trier les chromosomes proprement (Chr 1, Chr 2, ..., Chr 10)
def sort_chromosomes(chrs):
    def chr_key(c):
        if c.startswith('Chr '):
            return int(c.replace('Chr ', ''))
        return 9999
    return sorted(chrs, key=chr_key)

sources = []
targets = []
values = []
link_colors = []

# Stockage global des couleurs de chaque noeud pour héritage
node_color_map = {}

for i in range(len(genome_names)):
    gen_current = genome_names[i]
    chrs_current = sort_chromosomes(df_master[df_master['Organisme'] == gen_current]['Chromosome'].unique())
    
    if i == 0:
        # Espèce racine : On attribue les couleurs de base
        for c_idx, chrom in enumerate(chrs_current):
            node_name = f"{gen_current}_{chrom}"
            color = base_colors[c_idx % len(base_colors)]
            if chrom == "Autres scaffolds":
                color = "rgb(80, 80, 80)"
                
            node_color_map[node_name] = color
            add_node(gen_current, chrom, color)
    else:
        # Espèces suivantes : Héritage de la couleur majoritaire
        gen_prev = genome_names[i-1]
        df_prev = df_master[df_master['Organisme'] == gen_prev]
        df_curr = df_master[df_master['Organisme'] == gen_current]
        
        transitions = pd.merge(df_prev[['Busco_id', 'Chromosome']], 
                               df_curr[['Busco_id', 'Chromosome']], 
                               on='Busco_id', suffixes=('_prev', '_curr'))
        link_counts = transitions.groupby(['Chromosome_prev', 'Chromosome_curr']).size().reset_index(name='count')
        
        # Assigner les couleurs aux noeuds actuels
        for chrom in chrs_current:
            node_name = f"{gen_current}_{chrom}"
            
            if chrom == "Autres scaffolds":
                node_color_map[node_name] = "rgb(80, 80, 80)"
            else:
                incoming = link_counts[link_counts['Chromosome_curr'] == chrom]
                if not incoming.empty:
                    # Trouver le chromosome parent qui donne le plus de gènes
                    best_source = incoming.loc[incoming['count'].idxmax(), 'Chromosome_prev']
                    source_node_name = f"{gen_prev}_{best_source}"
                    # Hériter de sa couleur
                    node_color_map[node_name] = node_color_map.get(source_node_name, "rgb(150, 150, 150)")
                else:
                    node_color_map[node_name] = "rgb(150, 150, 150)"
                    
            add_node(gen_current, chrom, node_color_map[node_name])
            
        # Créer les liens physiques entre i-1 et i
        for _, row in link_counts.iterrows():
            src_name = f"{gen_prev}_{row['Chromosome_prev']}"
            tgt_name = f"{gen_current}_{row['Chromosome_curr']}"
            
            src_id = node_dict.get(src_name)
            tgt_id = node_dict.get(tgt_name)
            
            if src_id is not None and tgt_id is not None:
                sources.append(src_id)
                targets.append(tgt_id)
                values.append(row['count'])
                
                # Le lien prend la couleur de sa source (transparente)
                sc = node_color_map[src_name]
                if sc.startswith('#'):
                    h = sc.lstrip('#')
                    lc = f"rgba({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}, 0.4)"
                elif sc.startswith('rgb('):
                    lc = sc.replace('rgb(', 'rgba(').replace(')', ', 0.4)')
                else:
                    lc = "rgba(150, 150, 150, 0.4)"
                link_colors.append(lc)

# ==========================================
# 4. TRACÉ ET SAUVEGARDE DE LA FIGURE
# ==========================================
fig = go.Figure(data=[go.Sankey(
    arrangement = "snap",
    node = dict(
      pad = 12,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = node_colors
    ),
    link = dict(
      source = sources, 
      target = targets,
      value = values,
      color = link_colors,
      hovertemplate = 'Conservation: %{value} gènes vers %{target.label}<extra></extra>'
    )
)])

fig.update_layout(
    title_text="Macrosynténie - Suivi évolutif des chromosomes",
    font_size=11,
    height=800,
    plot_bgcolor='white'
)

html_out = os.path.join(DIR_OUTPUT, "sankey_chromosomes.html")
fig.write_html(html_out)
print(f"Diagramme Sankey sauvegardé : {html_out}")
