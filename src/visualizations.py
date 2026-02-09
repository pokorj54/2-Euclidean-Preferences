import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch
import os
import seaborn as sns
import numpy as np
import math
import sys

imgs = "../imgs/"
os.makedirs(os.path.dirname(imgs), exist_ok=True)
map_names = {
    "hull++": "Hull",
    "valtr": "EST",
    "TMC": "3-8",
    "IR": "ILP"
}

def defaults():
    plt.rcParams['figure.figsize'] = [12.0, 7.0]
    plt.rcParams['figure.dpi'] = 140
    plt.rcParams.update({'font.size': 70})
    sns.set(font_scale = 2, style="whitegrid")
    plt.close()

def is_val(row, val):
    return val in list(row)

def fastest_sol(row):
    if not pd.isnull(row["trivial"]):
        return ("trivial", 0)
    best = None
    best_time = None
    for column in row.index:
        if "_val" in column and not pd.isnull(row[column]):
            name = column[:-4]
            time = row[name+"_time"]
            if best_time is None or best_time > time:
                best_time = time
                best = name
    if best is None:
        best = "not solved"
    return (best, best_time)

def all_solved_string(row):
    if not pd.isnull(row["trivial"]):
        return "trivial"
    solved = []
    for column in row.index:
        if "_val" in column and not pd.isnull(row[column]):
            name = column[:-4]
            solved.append(name)
    return ",".join(solved)

def erase_unsolved_time(df):
    for column in time_clmns(df):
        clmn = column[:column.index("_")]
        df.loc[df[clmn+"_val"].isna(), column] = np.nan

def extra_cols(df):
    if "?" in df.columns:
        df.drop(["yes", "no", "?", "dataset", "solved_by", "solve_time"], axis=1, inplace=True)
    extra_df = df.apply(fastest_sol, axis=1)
    y = df.apply(lambda r: is_val(r, True), axis=1)
    n = df.apply(lambda r: is_val(r, False), axis=1)
    q = ~y&~n
    df["yes"] = y
    df["no"] = n
    df["?"] = q
    df[['solved_by', 'solve_time']] = pd.DataFrame(extra_df.to_list())
    df['dataset'] = df['instance'].apply(lambda x: os.path.basename(os.path.dirname(x)))
    all_solved = df.apply(lambda r: all_solved_string(r), axis = 1)
    df['all_solved'] = all_solved

def drop_suffix(name):
    if "_" in name:
        return name[:name.index("_")]
    return name

def drop_suffix_from_index(df):
    index = list(df.index)
    for i,name in enumerate(index):
        name = drop_suffix(name)
        index[i] = name
    df.index = index


def res_clmns(df):
    return ['trivial'] + [c for c in df.columns if '_val' in c]

def time_clmns(df):
    return [c for c in df.columns if '_time' in c and c != 'solve_time']


def get_dataframe(csv_path):
    df = pd.read_csv(csv_path)
    # hull and hull++ solve exactly the same instances and take the same time, just the more generalized version is kept
    df.drop(["hull_val","hull_time"],axis=1, inplace=True)
    columns = list(df.columns)
    for i,c in enumerate(columns):
        for name in map_names:
            c = c.replace(name, map_names[name])
            columns[i] = c
    df.columns = columns
    extra_cols(df)
    erase_unsolved_time(df)
    return df

def parse_reductions(reductions_string):
    reductions = []
    if reductions_string == "":
        return reductions
    for rule in reductions_string.split("|"):
        name = rule[:rule.index('(')]
        n = int(rule[rule.index('(')+1:rule.index(';')])
        m = int(rule[rule.index(';')+1:rule.index(')')])
        reductions.append((name, (n, m)))
    return reductions

def get_reductions_datasets(df):
    usage = []
    reductions = []
    for index, row in df.iterrows():
        if isinstance(row['reductions'], float) and math.isnan(row['reductions']):
            continue
        c = row['candidates']
        reduced = c
        for name, (n, m) in parse_reductions(row['reductions']):
            usage.append((row['instance'], name, reduced, m))
            reduced = m
        reductions.append((row['instance'], c, reduced))
    return pd.DataFrame(usage, columns=['instance', 'rule', 'original', 'reduced']), pd.DataFrame(reductions, columns=['instance',  'original', 'reduced'])

def group_datasets(df):
    datasets =  df[['dataset', 'yes', 'no','?']].groupby('dataset').sum()
    datasets = datasets.pivot_table(index='dataset',
               margins=True,
               margins_name='total',  # defaults to 'All'
               aggfunc="sum")
    return datasets


def plot_unsolved(df):
    sns.set(font_scale = 2, style="whitegrid")
    ax= df[df["?"] & (df['candidates'] < 50)].plot(kind='scatter', x='votes', y='candidates', s=200)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.figure.savefig(imgs+"unsolved.pdf")
    defaults()

def plot_who_solved(df, name):
    sns.set(font_scale = 3, style="white")
    fig = sns.lmplot(x='votes', y='candidates', data=df, hue='solved_by', fit_reg=False,height=10, aspect=17/10, scatter_kws={"s": 100}).fig #.set(title=f'Fastest solver for {name}')
    fig.savefig(imgs+"scatter_plot.pdf")
    defaults()

def plot_subsets_solved(df):
    sns.set(font_scale=2, style="white")

    value_counts = df['all_solved'].value_counts()

    # replace '' with 'not solved'
    index = list(value_counts.index)
    for i in range(len(index)):
        if index[i] == '':
            index[i] = "not solved"
    value_counts.index = index

    # ---- Colors for bars based on commas ----
    def color_for_label(label):
        if label == "trivial":
            return "darkgreen", "trivial"       # treat "not solved" as 0 commas
        if label == "not solved":
            return "tab:gray", "not solved"       # treat "not solved" as 0 commas
        colors = ["error_happened", "tab:red","tab:orange","tab:olive", "tab:green"]
        solvers = len(label.split(","))
        return colors[solvers], f"{solvers} solved"

    colors = []
    handles = set()
    for label in value_counts.index:
        color,legend_label = color_for_label(label)
        colors.append(color)
        handles.add((color,legend_label))
    handles = [Patch(color=color, label=label) for color,label in sorted(handles, key=lambda x: x[1] if x[1] != "not solved" else "0")]
        
    ax = value_counts.plot(kind='bar', logy=True, color=colors)

    # ---- Add numeric values above bars ----
    for idx, value in enumerate(value_counts):
        ax.text(idx, value, str(value),
                ha='center', va='bottom', color='black', fontsize=15)

    # ---- Add x-axis labels inside or above bars ----
    for idx, (label, value) in enumerate(zip(value_counts.index, value_counts.values)):

        if value >= 2:
            # Label inside bar in white
            ax.text(
                idx,
                1,       # low inside the bar
                label,
                ha='center', va='bottom',
                rotation=90,
                color='white', fontsize=15
            )
        else:
            # Label above the bar in black
            ax.text(
                idx,
                value * 1.6,      # just above
                label,
                ha='center', va='bottom',
                rotation=90,
                color='black', fontsize=15
            )
    ax.legend(handles=handles)
    
    # Hide the original x-axis tick labels
    ax.set_xticklabels([""] * len(value_counts))

    plt.tight_layout()
    ax.figure.savefig(imgs + "powersets.pdf")
def plot_times(df):
    sns.set(font_scale = 2, style="whitegrid")
    lw =3
    fig, ax = plt.subplots()
    df[df['solved_by']!= 'trivial']['solve_time'].sort_values(ignore_index=True).plot(logy=True, label="Best", legend=True, linewidth=lw)
    for c in time_clmns(df):
        df[c].sort_values(ignore_index=True).plot(logy=True, legend=True, label = drop_suffix(c), linewidth=lw)
    ax.set_xlabel("number of solved instances")
    ax.set_ylabel("maximum time of run in seconds")
    plt.legend(ncol=3,loc='lower right',bbox_to_anchor=(1.015, -0.02),prop={'family': 'monospace'})
    ax.figure.savefig(imgs+"solved_per_time.pdf")
    defaults()

def print_tables(df):
    print("===================================")
    print("Solver information")
    print("===================================")
    non_nan_counts = df[res_clmns].notna().sum()
    drop_suffix_from_index(non_nan_counts)
    max_time = df[time_clmns].max()
    drop_suffix_from_index(max_time)
    median_time = df[time_clmns].median()
    drop_suffix_from_index(median_time)
    solved_by_counts = df[df['solved_by'] != "not solved"]['solved_by'].value_counts()
    cdf = pd.DataFrame({"solved":non_nan_counts, "fastest":solved_by_counts, "max time": max_time, "median time":  median_time})
    print(cdf.to_latex())
    
    print("===================================")
    print("Dataset information")
    print("===================================")
    datasets = group_datasets(df)
    print(datasets.to_latex())
    
def main():
    if len(sys.argv) == 1:
        print(f"Run this as {sys.argv[0]} path/to/data.csv")
        exit(1)
    defaults()
    csv_path = sys.argv[1]
    df = get_dataframe(csv_path)
    print_tables(df)
    plot_unsolved(df)
    plot_who_solved(df[(df['votes'] < 70) & (df['candidates'] < 50)], 'Preflib')
    plot_subsets_solved(df)
    plot_times(df)

if __name__ == "__main__":
    main()