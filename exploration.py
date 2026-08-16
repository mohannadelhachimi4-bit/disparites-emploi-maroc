import pandas as pd

files = {
    "activite": "data/raw/activite_province_milieu.csv",
    "emploi": "data/raw/emploi_province_milieu.csv",
    "chomage_province": "data/raw/chomage_province_milieu.csv",
    "chomage_diplome": "data/raw/chomage_diplome_milieu.csv",
}

for name, path in files.items():
    print(f"\n{'='*60}\n{name.upper()} — {path}\n{'='*60}")
    df = pd.read_csv(path, sep=None, engine="python")  # détecte le séparateur automatiquement
    print("Shape :", df.shape)
    print("\nColonnes :", list(df.columns))
    print("\nTypes :\n", df.dtypes)
    print("\nAperçu (head) :\n", df.head(10))
    print("\nAperçu (tail) :\n", df.tail(5))
    print("\nValeurs manquantes :\n", df.isna().sum())
