import requests
import pyodbc
# obetener datos de la api
response = requests.get('https://dummyjson.com/products/categories/')
data = response.json()

# fromatear para obtener los datos deseados
categories = [{"slug": c["slug"], "name": c["name"]} for c in data]
print(categories)


# aca se concecta a la base de datos
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=CYANIDE\SQLEXPRESS;'#aca tenes que cambiar a tu propio server
    r'DATABASE=group_categories;'
    r'Trusted_Connection=yes;'  
)

cursor = conn.cursor()