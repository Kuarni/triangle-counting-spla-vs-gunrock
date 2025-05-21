import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

GRAPH_DIR = Path("graphs")

def load_data(json_path: Path) -> pd.DataFrame:
    with json_path.open(encoding='utf-8') as f:
        data = json.load(f)

    records = []
    for b in data.get('benchmarks', []):
        name = b.get('name', '').split('/')
        if name[-1].find("_") != -1:
            continue
        algorithm = name[0].replace("_", " ")
        graph = name[1].split('.')[0]
        records.append({
            'algorithm': algorithm,
            'graph': graph,
            'time': b['real_time'],
            'family_index': b['family_index'],
            'triangles': b['triangles']
        })
    return pd.DataFrame.from_records(records)

def compute_stats(df: pd.DataFrame, confidence: float = 0.95) -> pd.DataFrame:
    out = []
    for (alg, fi), sub in df.groupby(['algorithm', 'graph']):
        arr = sub['time'].to_numpy()
        n = arr.size
        mean = arr.mean()
        se = stats.sem(arr, ddof=1)
        h = se * stats.t.ppf((1 + confidence) / 2, df=n - 1)
        out.append({
            'algorithm': alg,
            'graph': fi,
            'mean': mean,
            'ci_half': h,
            'triangles': int(sub['triangles'].to_numpy()[0]),
            'n': n,
        })
    return pd.DataFrame(out)


def plot_comparison(stats_df: pd.DataFrame):
    cats = list(stats_df['graph'].unique())
    x = np.arange(len(cats))
    algs = stats_df['algorithm'].unique()
    total_width = 0.8
    n = len(algs)
    width = total_width / n

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, alg in enumerate(algs):
        sub = stats_df[stats_df['algorithm'] == alg].set_index('graph')
        means = sub.loc[cats, 'mean'].values
        errs = sub.loc[cats, 'ci_half'].values
        pos = x - total_width / 2 + (i + 0.5) * width

        ax.bar(pos, means, width=width,
               label=alg, alpha=0.7, edgecolor='black',
               color=None)

        lower = errs
        upper = errs
        ax.errorbar(pos, means, yerr=[lower, upper],
                    fmt='none', capsize=3, ecolor='black')

        for xi, m, err in zip(pos, means, errs):
            top = (m + err) * 1.05
            ax.text(xi, top, f"{m:.1f}" if m < 10 else f"{m:.0f}",
                    ha='center', va='bottom', fontsize=9)

    ax.set_yscale('log')

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=0)
    for idx, lbl in enumerate(ax.get_xticklabels()):
        offset = 0.00 if idx % 2 == 0 else -0.05
        lbl.set_y(offset)

    ax.set_xlabel('Граф')
    ax.set_ylabel('Время выполнения (ms)')
    ax.set_title('Сравнение времени выполнения: mean ± 95% CI')

    ax.grid(axis='y', which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    ax.legend(frameon=False, loc='upper left')

    filename = f"results/{'_'.join(algs).replace(' ', '_')}_bench.png"
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"График сохранён в файл «{filename}»")


def check_triangles_consistency(df: pd.DataFrame):
    counts = df.groupby('graph')['triangles'].nunique()

    bad_graphs = counts[counts > 1]
    if not bad_graphs.empty:
        details = df[df['graph'].isin(bad_graphs.index)]
        raise AssertionError(
            f"Найдены графы с разными значениями 'triangles':\n"
            f"{bad_graphs.to_dict()}\n"
            f"Детали:\n{details.sort_values(['algorithm', 'graph', 'triangles'])}"
        )


def save_summary(stats_df: pd.DataFrame, out_dir: Path = Path("results")):
    out_dir.mkdir(exist_ok=True, parents=True)

    table = stats_df.pivot_table(
        index=['graph', 'triangles'],
        columns='algorithm',
        values='mean'
    ).reset_index()
    table.columns.name = None

    cols = ['graph', 'triangles'
        , *stats_df['algorithm'].unique()]
    table = table[cols]

    float_cols = [c for c in table.columns if c in stats_df['algorithm'].unique()]
    table[float_cols] = table[float_cols].round(1)

    csv_path = out_dir / "summary_table.csv"
    table.to_csv(csv_path, index=False)

    print(f"Таблица сохранена в: {csv_path}")


def analyze(*data_files):
    df = pd.concat([load_data(Path(data_file)) for data_file in data_files])
    check_triangles_consistency(df)
    stats_df = compute_stats(df)
    plot_comparison(stats_df)
    save_summary(stats_df)


if (__name__ == "__main__"):
    analyze(*sys.argv[1:])
