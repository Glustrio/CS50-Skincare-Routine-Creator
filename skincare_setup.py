# skincare/setup_dataset.py
import os
from pathlib import Path
import sqlite3
import ast  # safer than eval for list-like strings
import kagglehub
import pandas as pd

# Download (or reuse cache) and wrap as Path
data_dir = Path(kagglehub.dataset_download("eward96/skincare-products-clean-dataset"))

csv_path = data_dir / "skincare_products_clean.csv"

# Load dataset
df = pd.read_csv(csv_path)

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print(df.head())

exchange_rate = 1.32  # 1 GBP = 1.32 USD

# First clean the price column: remove currency symbol and convert to float
df["price_usd"] = (
    df["price"]
      .astype(str)
      .str.replace("£", "", regex=False)
      .str.replace(",", "", regex=False)
      .astype(float)
      * exchange_rate
)

# Round to 2 decimals
df["price_usd"] = df["price_usd"].round(2)

df = df.drop(columns=["price"])

all_ingredients = (
    df["clean_ingreds"]
    .dropna()                     # remove missing values
    .apply(lambda x: eval(x) if isinstance(x, str) else x)  # convert string to list if needed
    .explode()                    # flatten lists into rows
    .str.strip()                  # remove whitespace
    .str.lower()                  # normalize casing
    .drop_duplicates()            # unique ingredients only
    .tolist()                     # convert to Python list
)

if "id" not in df.columns:
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

product_cols = ["id", "product_name", "product_url", "product_type", "price_usd"]
products_df = df[product_cols].copy()

conn = sqlite3.connect("skincare.db")

products_df.to_sql("products", conn, if_exists="replace", index=False)

ingredients_df = pd.DataFrame({
    "ingredient_id": range(1, len(all_ingredients) + 1),
    "name": all_ingredients
})

ingredients_df.to_sql("ingredients", conn, if_exists="replace", index=False)

name_to_id = {name: i+1 for i, name in enumerate(all_ingredients)}

rows = []

for _, row in df[["id", "clean_ingreds"]].iterrows():
    product_id = row["id"]
    ingreds = row["clean_ingreds"]

    # If clean_ingreds is stored as a stringified list, parse it
    if isinstance(ingreds, str):
        try:
            ingreds = ast.literal_eval(ingreds)
        except Exception:
            continue  # skip if badly formatted

    if not isinstance(ingreds, (list, tuple)):
        continue

    for ing in ingreds:
        ing_norm = ing.strip().lower()
        if ing_norm in name_to_id:
            rows.append({
                "product_id": product_id,
                "ingredient_id": name_to_id[ing_norm]
            })

product_ingredients_df = pd.DataFrame(rows)

product_ingredients_df.to_sql(
    "product_ingredients",
    conn,
    if_exists="replace",
    index=False
)

with conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            product_id INTEGER
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS routine (
            user_id INTEGER,
            product_id INTEGER
        );
    """)

conn.close()
