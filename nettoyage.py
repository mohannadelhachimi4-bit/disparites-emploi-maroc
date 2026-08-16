import pandas as pd
import os


def load_bds_table(path, value_name, id_col_name):
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = ["milieu", id_col_name] + list(df.columns[2:])
    df = df.iloc[1:].reset_index(drop=True)      # supprime la ligne d'en-tête parasite
    df["milieu"] = df["milieu"].ffill()           # comble le forward-fill du milieu
    year_cols = list(df.columns[2:])
    df_long = df.melt(
        id_vars=["milieu", id_col_name],
        value_vars=year_cols,
        var_name="annee",
        value_name=value_name,
    )
    df_long["annee"] = df_long["annee"].astype(int)
    df_long = df_long.dropna(subset=[value_name]).reset_index(drop=True)
    return df_long

activite = load_bds_table("data/raw/activite_province_milieu.csv", "taux_activite", "province")
emploi   = load_bds_table("data/raw/emploi_province_milieu.csv", "taux_emploi", "province")
chomage  = load_bds_table("data/raw/chomage_province_milieu.csv", "taux_chomage", "province")
chomage_diplome = load_bds_table("data/raw/chomage_diplome_milieu.csv", "taux_chomage", "diplome")

for name, df in [("activite", activite), ("emploi", emploi), ("chomage", chomage), ("chomage_diplome", chomage_diplome)]:
    print(f"\n{name} : {df.shape}")
    print("Milieux :", df['milieu'].unique())
    print(df.head(3))

# Fusion activite + emploi + chomage sur (province, milieu, annee)
marche_travail = (
    activite
    .merge(emploi, on=["milieu", "province", "annee"], how="outer")
    .merge(chomage, on=["milieu", "province", "annee"], how="outer")
    .sort_values(["province", "milieu", "annee"])
    .reset_index(drop=True)
)

print(marche_travail.shape)
print(marche_travail.isna().sum())
print(marche_travail.head(10))

# Vérifier les catégories de diplôme réelles
print(chomage_diplome["diplome"].unique())
print(marche_travail.groupby("milieu")["taux_chomage"].apply(lambda s: s.isna().mean()))

chomage_diplome_clean = chomage_diplome[chomage_diplome["diplome"] != "Total"]

os.makedirs("data/clean", exist_ok=True)
marche_travail.to_csv("data/clean/marche_travail.csv", index=False)
chomage_diplome.to_csv("data/clean/chomage_diplome.csv", index=False)
