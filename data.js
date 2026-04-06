
fetch('https://dummyjson.com/products/categories/')
.then(res => res.json())
.then(data => console.log(data.map(c => ({slug : c.slug, name: c.name}))));

