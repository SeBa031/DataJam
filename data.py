import requests

response = requests.get('https://dummyjson.com/products/categories/')
data = response.json()

categories = [{"slug": c["slug"], "name": c["name"]} for c in data]
print(categories)