import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    marche_travail = pd.read_csv("data/clean/marche_travail.csv")
    chomage_diplome = pd.read_csv("data/clean/chomage_diplome.csv")
    chomage_diplome_clean = chomage_diplome[chomage_diplome["diplome"] != "Total"]
    return marche_travail, chomage_diplome_clean


def plot_evolution_nationale(marche_travail: pd.DataFrame) -> None:
    """Graphique 1 : évolution nationale 2017-2025 (activité/emploi/chômage).
    Moyenne simple inter-provinces, non pondérée par population — à titre indicatif.
    """
    moyenne_provinciale = marche_travail[
        marche_travail["milieu"] == "National"]
    evolution = moyenne_provinciale.groupby("annee")[
        ["taux_activite", "taux_emploi", "taux_chomage"]
    ].mean()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(evolution.index, evolution["taux_activite"], marker="o", label="Taux d'activité", linewidth=2)
    ax.plot(evolution.index, evolution["taux_emploi"], marker="o", label="Taux d'emploi", linewidth=2)
    ax.plot(evolution.index, evolution["taux_chomage"], marker="o", label="Taux de chômage", linewidth=2)

    ax.set_title("Évolution du marché du travail au Maroc (2017-2025)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Année")
    ax.set_ylabel("Taux (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(evolution.index)

    plt.tight_layout()
    plt.savefig("outputs/01_evolution_nationale.png", dpi=150)
    plt.close(fig)


def plot_classement_provinces(marche_travail: pd.DataFrame) -> None:
    """Graphique 2 : top 15 / bottom 15 des provinces par taux de chômage (2025)."""
    data_2025 = (
        marche_travail[(marche_travail["milieu"] == "National") & (marche_travail["annee"] == 2025)]
        .dropna(subset=["taux_chomage"])
        .sort_values("taux_chomage")
    )

    top15 = data_2025.tail(15)
    bottom15 = data_2025.head(15)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), sharex=True)

    axes[0].barh(bottom15["province"], bottom15["taux_chomage"], color="#2ca02c")
    axes[0].set_title("15 provinces à plus faible chômage")
    axes[0].set_xlabel("Taux de chômage (%)")

    axes[1].barh(top15["province"], top15["taux_chomage"], color="#d62728")
    axes[1].set_title("15 provinces à plus fort chômage")
    axes[1].set_xlabel("Taux de chômage (%)")

    fig.suptitle("Disparités provinciales du taux de chômage — 2025 (Milieu National)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("outputs/02_classement_provinces_chomage.png", dpi=150)
    plt.close(fig)


def plot_ecart_urbain_rural(marche_travail: pd.DataFrame) -> None:
    """Graphique 3 : écart de chômage urbain vs rural par province (2025).
    Limité aux provinces disposant des deux valeurs (le HCP ne publie pas
    systématiquement le taux rural pour toutes les provinces).
    """
    pivot_milieu = (
        marche_travail[(marche_travail["annee"] == 2025) & (marche_travail["milieu"].isin(["Urbain", "Rural"]))]
        .pivot(index="province", columns="milieu", values="taux_chomage")
        .dropna()
    )

    pivot_milieu["ecart"] = pivot_milieu["Urbain"] - pivot_milieu["Rural"]
    pivot_milieu = pivot_milieu.sort_values("ecart")

    fig, ax = plt.subplots(figsize=(10, 12))
    y_pos = range(len(pivot_milieu))

    ax.hlines(y_pos, pivot_milieu["Rural"], pivot_milieu["Urbain"], color="gray", alpha=0.5)
    ax.scatter(pivot_milieu["Rural"], y_pos, color="#2ca02c", label="Rural", zorder=3)
    ax.scatter(pivot_milieu["Urbain"], y_pos, color="#1f77b4", label="Urbain", zorder=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(pivot_milieu.index, fontsize=8)
    ax.set_xlabel("Taux de chômage (%)")
    ax.set_title("Écart de chômage Urbain vs Rural par province — 2025", fontsize=13, fontweight="bold")
    ax.legend()
    ax.grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig("outputs/03_ecart_urbain_rural.png", dpi=150)
    plt.close(fig)


def plot_chomage_diplome(chomage_diplome_clean: pd.DataFrame) -> None:
    """Graphique 4 : taux de chômage selon le niveau de diplôme (2025, National)."""
    diplome_2025 = chomage_diplome_clean[
        (chomage_diplome_clean["milieu"] == "National") & (chomage_diplome_clean["annee"] == 2025)
        ].sort_values("taux_chomage")

    fig, ax = plt.subplots(figsize=(15, 6))
    bars = ax.barh(diplome_2025["diplome"], diplome_2025["taux_chomage"], color="#ff7f0e")

    ax.set_title("Taux de chômage selon le niveau de diplôme — 2025 (National)", fontsize=12, fontweight="bold", pad=15)
    ax.set_xlabel("Taux de chômage (%)")

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.3, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%", va="center")

    plt.tight_layout()
    plt.savefig("outputs/04_chomage_diplome.png", dpi=150)
    plt.close(fig)


def plot_diplome_milieu(chomage_diplome_clean: pd.DataFrame) -> None:
    """Graphique 5 : chômage par diplôme x milieu, barres groupées (2025)."""
    diplome_milieu_2025 = chomage_diplome_clean[
        (chomage_diplome_clean["milieu"].isin(["Urbain", "Rural"])) & (chomage_diplome_clean["annee"] == 2025)
        ]

    pivot_diplome = diplome_milieu_2025.pivot(index="diplome", columns="milieu", values="taux_chomage")
    pivot_diplome = pivot_diplome.sort_values("Urbain")

    x = np.arange(len(pivot_diplome))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(x - width / 2, pivot_diplome["Urbain"], width, label="Urbain", color="#1f77b4")
    ax.bar(x + width / 2, pivot_diplome["Rural"], width, label="Rural", color="#2ca02c")

    ax.set_xticks(x)
    ax.set_xticklabels(pivot_diplome.index, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Taux de chômage (%)")
    ax.set_title("Chômage par diplôme et milieu — 2025", fontsize=13, fontweight="bold", pad=15)
    ax.legend()

    plt.tight_layout()
    plt.savefig("outputs/05_diplome_milieu.png", dpi=150)
    plt.close(fig)


def plot_activite_vs_chomage(marche_travail: pd.DataFrame) -> None:
    """Graphique 6 : taux d'activité vs taux de chômage par province, avec
    coefficient de corrélation affiché (2025, National).
    """
    scatter_data = marche_travail[
        (marche_travail["milieu"] == "National") & (marche_travail["annee"] == 2025)
        ].dropna(subset=["taux_activite", "taux_chomage"])

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(scatter_data["taux_activite"], scatter_data["taux_chomage"], alpha=0.6, s=60, color="#9467bd")

    extremes = pd.concat([
        scatter_data.nlargest(3, "taux_chomage"),
        scatter_data.nsmallest(3, "taux_chomage"),
    ])
    for _, row in extremes.iterrows():
        ax.annotate(
            row["province"],
            (row["taux_activite"], row["taux_chomage"]),
            fontsize=8,
            xytext=(5, 5),
            textcoords="offset points",
        )

    ax.set_xlabel("Taux d'activité (%)")
    ax.set_ylabel("Taux de chômage (%)")
    ax.set_title("Taux d'activité vs taux de chômage par province — 2025", fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, alpha=0.3)

    corr = scatter_data["taux_activite"].corr(scatter_data["taux_chomage"])
    ax.text(
        0.02, 0.98, f"Corrélation : {corr:.2f}",
        transform=ax.transAxes, va="top", fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig("outputs/06_activite_vs_chomage.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    marche_travail, chomage_diplome_clean = load_data()

    plot_evolution_nationale(marche_travail)
    plot_classement_provinces(marche_travail)
    plot_ecart_urbain_rural(marche_travail)
    plot_chomage_diplome(chomage_diplome_clean)
    plot_diplome_milieu(chomage_diplome_clean)
    plot_activite_vs_chomage(marche_travail)

    print("6 graphiques générés dans outputs/")