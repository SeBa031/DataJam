import requests
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from pathlib import Path
import urllib

# ============================================================
# CONFIGURACIÓN
# ============================================================
SERVER   = r".\SQLEXPRESS"   # <-- cambiá esto a tu servidor
DATABASE = "DataJam"

# Ruta absoluta a la carpeta de CSVs, relativa al propio script
# Si los CSVs están EN LA MISMA carpeta que el script, usá: Path(__file__).parent
CSV_PATH = Path(__file__).parent / "dataset_group_categories"

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

print("✅ Conexión establecida correctamente.\n")


# ============================================================
# 1. COUNTRIES
#    El CSV usa códigos de texto (ej. "AR"), pero la tabla SQL
#    define country_code como INT PRIMARY KEY.
#    Generamos un ID numérico y guardamos el mapeo para las
#    tablas que dependen de countries.
# ============================================================
print("📦 Cargando countries...")

df_countries = pd.read_csv(f"{CSV_PATH}/countries.csv")

# Creamos el mapeo: "AR" -> 1, "AU" -> 2, etc.
df_countries = df_countries.reset_index(drop=True)
df_countries["country_code"] = df_countries.index + 1          # ID numérico autoincremental
code_to_id = dict(zip(df_countries["code"], df_countries["country_code"]))

df_countries_db = df_countries[["country_code", "name", "population"]]

df_countries_db.to_sql(
    "countries",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_countries_db)} filas insertadas en 'countries'.\n")


# ============================================================
# 2. CATEGORIES
#    El CSV tiene la columna 'name' vacía.
#    Completamos con los datos de la API de dummyjson.
# ============================================================
print("📦 Completando categories desde la API...")

response = requests.get("https://dummyjson.com/products/categories/")
response.raise_for_status()
api_categories = response.json()  # lista de {"slug": ..., "name": ...}

# Diccionario slug -> name proveniente de la API
slug_to_name = {c["slug"]: c["name"] for c in api_categories}

df_categories = pd.read_csv(f"{CSV_PATH}/categories.csv")   # columnas: id, slug, name

# Rellenar los nombres faltantes usando el slug como clave
df_categories["name"] = df_categories.apply(
    lambda row: slug_to_name.get(row["slug"], row["name"])
    if pd.isna(row["name"]) or row["name"] == ""
    else row["name"],
    axis=1,
)

df_categories_db = df_categories.rename(columns={"id": "category_id"})[
    ["category_id", "slug", "name"]
]

df_categories_db.to_sql(
    "categories",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_categories_db)} filas insertadas en 'categories'.\n")


# ============================================================
# 3. SHIPPING_REGIONS
#    Reemplazamos el código de texto por el ID numérico de countries.
# ============================================================
print("📦 Cargando shipping_regions...")

df_shipping = pd.read_csv(f"{CSV_PATH}/shipping_regions.csv")

# Mapear el código de texto al ID numérico
df_shipping["country_code"] = df_shipping["country_code"].map(code_to_id)

# Generar un PK propio para shipping_regions
df_shipping.insert(0, "shipping_regions_id", range(1, len(df_shipping) + 1))

df_shipping_db = df_shipping[
    ["shipping_regions_id", "region", "shipping_zone", "estimated_days", "country_code"]
]

df_shipping_db.to_sql(
    "shipping_regions",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_shipping_db)} filas insertadas en 'shipping_regions'.\n")


# ============================================================
# 4. USERS
#    Reemplazamos el código de texto por el ID numérico de countries.
# ============================================================
print("📦 Cargando users...")

df_users = pd.read_csv(f"{CSV_PATH}/users.csv")

# Mapear código de texto -> ID numérico
df_users["country_code"] = df_users["country_code"].map(code_to_id)

# Convertir la fecha al tipo correcto
df_users["created_at"] = pd.to_datetime(df_users["created_at"])

df_users_db = df_users.rename(columns={"id": "user_id"})[
    ["user_id", "email", "created_at", "country_code"]
]

df_users_db.to_sql(
    "users",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_users_db)} filas insertadas en 'users'.\n")


# ============================================================
# 5. PRODUCTS
# ============================================================
print("📦 Cargando products...")

df_products = pd.read_csv(f"{CSV_PATH}/products.csv")

df_products_db = df_products.rename(columns={"id": "product_id"})[
    ["product_id", "name", "price", "category_id"]
]

df_products_db.to_sql(
    "products",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_products_db)} filas insertadas en 'products'.\n")


# ============================================================
# 6. PRODUCT_DETAILS
# ============================================================
print("📦 Cargando product_details...")

df_pd = pd.read_csv(f"{CSV_PATH}/product_details.csv")

# Generar PK
df_pd.insert(0, "product_details_id", range(1, len(df_pd) + 1))

df_pd_db = df_pd[["product_details_id", "product_id", "stock", "rating", "weight"]]

df_pd_db.to_sql(
    "product_details",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_pd_db)} filas insertadas en 'product_details'.\n")


# ============================================================
# 7. ORDERS
# ============================================================
print("📦 Cargando orders...")

df_orders = pd.read_csv(f"{CSV_PATH}/orders.csv")

df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])

df_orders_db = df_orders.rename(columns={"id": "order_id", "order_date": "created_at"})[
    ["order_id", "created_at", "total_amount", "user_id"]
]

df_orders_db.to_sql(
    "orders",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_orders_db)} filas insertadas en 'orders'.\n")


# ============================================================
# 8. ORDER_ITEMS
# ============================================================
print("📦 Cargando order_items...")

df_items = pd.read_csv(f"{CSV_PATH}/order_items.csv")

df_items_db = df_items.rename(columns={"id": "order_items_id"})[
    ["order_items_id", "quantity", "unit_price", "order_id", "product_id"]
]

df_items_db.to_sql(
    "order_items",
    engine,
    if_exists="append",
    index=False,
)
print(f"   ✅ {len(df_items_db)} filas insertadas en 'order_items'.\n")


# ============================================================
# RESUMEN FINAL
# ============================================================
print("=" * 50)
print("🎉 Carga completada exitosamente.")
print("=" * 50)