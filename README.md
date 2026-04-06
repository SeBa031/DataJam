# DataJam

Pipeline de carga de datos desde archivos CSV y una API externa hacia una base de datos SQL Server. El proyecto construye el esquema relacional completo de una tienda online, incluyendo usuarios, productos, categorías, órdenes y regiones de envío.

---

## Estructura del proyecto

```
DataJam/
├── dataset_group_categories/
│   ├── categories.csv
│   ├── countries.csv
│   ├── order_items.csv
│   ├── orders.csv
│   ├── product_details.csv
│   ├── products.csv
│   ├── shipping_regions.csv
│   └── users.csv
├── SQLQuery1.sql       # Script DDL para crear la base de datos y tablas
├── load_data.py        # Script principal de carga
└── README.md
```

---

## Esquema de la base de datos

```
countries ──────────┬──── shipping_regions
                    │
                    └──── users ──────────── orders ──── order_items
                                                               │
categories ─── products ─── product_details ─────────────────┘
```

| Tabla             | Filas   | Descripción                              |
|-------------------|---------|------------------------------------------|
| `countries`       | 24      | Países con código, nombre y población    |
| `categories`      | 24      | Categorías de productos                  |
| `shipping_regions`| 24      | Zonas y tiempos de envío por país        |
| `users`           | 3.500   | Usuarios registrados                     |
| `products`        | 194     | Productos con precio y categoría         |
| `product_details` | 194     | Stock, rating y peso por producto        |
| `orders`          | 22.000  | Órdenes de compra                        |
| `order_items`     | 45.965  | Ítems individuales por orden             |

---

## Requisitos

- Python 3.8+
- SQL Server con ODBC Driver 17
- Las siguientes librerías de Python:

```bash
pip install pandas sqlalchemy pyodbc requests
```

---

## Configuración

Antes de ejecutar el script, ajustá las siguientes variables al inicio de `load_data.py`:

```python
SERVER   = r".\SQLEXPRESS"          # Tu instancia de SQL Server
DATABASE = "DataJam"                 # Nombre de la base de datos
CSV_PATH = Path(__file__).parent / "dataset_group_categories"  # Ruta a los CSVs
```

Si los CSVs están en otra carpeta, modificá `CSV_PATH` según corresponda:

```python
# En la misma carpeta que el script
CSV_PATH = Path(__file__).parent

# Con ruta absoluta
CSV_PATH = Path(r"C:\ruta\absoluta\a\los\csvs")
```

---

## Uso

**1. Crear la base de datos y las tablas** ejecutando el script DDL en SQL Server Management Studio:

```sql
-- SQLQuery1.sql
CREATE DATABASE DataJam;
-- ... (ver archivo completo)
```

**2. Ejecutar el script de carga:**

```bash
python load_data.py
```

---

## Decisiones de diseño

### country_code como INT

El CSV de países usa códigos ISO de texto (`"AR"`, `"BR"`, etc.), pero la tabla SQL define `country_code` como `INT PRIMARY KEY`. El script genera un ID numérico autoincremental y construye un mapeo interno para aplicarlo de forma consistente en `users` y `shipping_regions`.

### Nombres de categorías desde la API

El archivo `categories.csv` no incluye los nombres de las categorías. El script los obtiene en tiempo de ejecución desde la API de [dummyjson.com](https://dummyjson.com/products/categories/) usando el campo `slug` como clave de coincidencia.

### PKs generados en runtime

Las tablas `shipping_regions` y `product_details` no tienen una columna de ID en sus CSVs. El script genera automáticamente claves primarias con `range(1, n+1)` antes de insertar.

### Orden de inserción

Para respetar las restricciones de clave foránea, las tablas se insertan en el siguiente orden:

1. `countries` y `categories` (sin dependencias)
2. `shipping_regions` y `users` (dependen de `countries`)
3. `products` (depende de `categories`)
4. `product_details` (depende de `products`)
5. `orders` (depende de `users`)
6. `order_items` (depende de `orders` y `products`)

---

## Fuente de datos

Los datos de categorías se obtienen de la API pública de [DummyJSON](https://dummyjson.com/):

```
GET https://dummyjson.com/products/categories/
```
