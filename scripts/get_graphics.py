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
    """
    Группирует по ['algorithm','family_index'] и для каждой группы
    считает mean и половину доверительного интервала (h = margin of error).
    Формула: h = t_{alpha/2, n-1} * (std(arr)/sqrt(n))
    """
    out = []
    for (alg, fi), sub in df.groupby(['algorithm', 'graph']):
        arr = sub['time'].to_numpy()
        n = arr.size
        mean = arr.mean()
        se = stats.sem(arr)
        h = se * stats.t.ppf((1 + confidence) / 2, df=n - 1)
        out.append({
            'algorithm': alg,
            'graph': fi,
            'mean': mean,
            'ci_half': h,
            'n': n,
        })
    return pd.DataFrame(out)


def plot_comparison(stats_df: pd.DataFrame):
    categories = list(stats_df['graph'].unique())
    x = np.arange(len(categories))

    # алгоритмы и цвета
    algs = stats_df['algorithm'].unique()
    colors = {'Burkhardt': '#ADD8E6', 'Sandia': '#FFA07A'}

    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, alg in enumerate(algs):
        sub = stats_df[stats_df['algorithm'] == alg]
        # y-координаты
        means = [sub[sub['graph'] == cat]['mean'].values[0] for cat in categories]
        errs  = [sub[sub['graph'] == cat]['ci_half'].values[0] for cat in categories]
        pos = x - width/2 + i*width

        bars = ax.bar(
            pos, means,
            width=width,
            yerr=errs,
            capsize=3,
            label=alg,
            color=colors.get(alg, None),
            edgecolor='black',
            alpha=0.7
        )

        # подписи значений
        for bar, m in zip(bars, means):
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2,
                h * 1.05,  # чуть выше вершины
                f"{m:.1f}",
                ha='center', va='bottom',
                fontsize=8
            )

    # стиль осей и сетки
    ax.set_yscale('log')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=0)

    labels = ax.get_xticklabels()
    for i, lbl in enumerate(labels):
        # сдвиг вниз/вверх в координатах оси: отрицательное смещение опускает метку ниже
        offset = 0 if i % 2 == 0 else -0.05
        lbl.set_y(offset)

    ax.set_xlabel('Граф')
    ax.set_ylabel('Время выполнения (µs)')
    ax.set_title('Сравнение времени выполнения: Burkhardt vs Sandia (mean ± 95% CI)')

    ax.grid(axis='y', which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    # легенда
    ax.legend(frameon=False, loc='upper left')

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    data_file = Path('bench_result.json')
    df = load_data(data_file)
    stats_df = compute_stats(df)
    plot_comparison(stats_df)
