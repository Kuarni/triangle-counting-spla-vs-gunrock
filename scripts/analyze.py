import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def load_data(json_path: Path) -> pd.DataFrame:
    with json_path.open(encoding='utf-8') as f:
        data = json.load(f)

    records = []
    for b in data.get('benchmarks', []):
        name = b.get('name', '').split('/')
        if name[-1].find("_") != -1:
            continue
        algorithm = name[0]
        graph = name[1].split('.')[0]
        records.append({
            'algorithm': algorithm,
            'graph': graph,
            'time': b['real_time'],  # в микросекундах
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
            'n': n,
        })
    return pd.DataFrame(out)

def plot_comparison(stats_df: pd.DataFrame, filename: str = 'results/bench_graphic.png'):
    cats = list(stats_df['graph'].unique())
    x = np.arange(len(cats))
    algs = stats_df['algorithm'].unique()
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, alg in enumerate(algs):
        sub = stats_df[stats_df['algorithm'] == alg].set_index('graph')
        means = sub.loc[cats, 'mean'].values
        errs  = sub.loc[cats, 'ci_half'].values
        pos = x - width/2 + i*width

        ax.bar(pos, means, width=width,
               label=alg, alpha=0.7, edgecolor='black',
               color=None)  # можно указать свои цвета

        lower = errs
        upper = errs
        ax.errorbar(pos, means, yerr=[lower, upper],
                    fmt='none', capsize=3, ecolor='black')

        for xi, m in zip(pos, means):
            ax.text(xi, m * 1.05, f"{m:.1f}",
                    ha='center', va='bottom', fontsize=8)

    ax.set_yscale('log')

    ax.set_xticks(x)
    ax.set_xticklabels(cats, rotation=0)
    for idx, lbl in enumerate(ax.get_xticklabels()):
        offset = 0.00 if idx % 2 == 0 else -0.05
        lbl.set_y(offset)

    ax.set_xlabel('Граф')
    ax.set_ylabel('Время выполнения (µs)')
    ax.set_title('Сравнение времени выполнения: mean ± 95% CI')

    ax.grid(axis='y', which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    ax.legend(frameon=False, loc='upper left')

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

def analyze():
    data_file = Path('results/spla_bench_result.json')
    df = load_data(data_file)
    check_triangles_consistency(df)
    stats_df = compute_stats(df)
    plot_comparison(stats_df)

if __name__ == '__main__':
    analyze()
