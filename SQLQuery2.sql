
-- NIVEL BÁSICO



-- 1. volumen
SELECT 
    COUNT(*) AS total_pedidos,
    SUM(total_amount) AS monto_total_usd
FROM dbo.orders;

-- 2. Top 15 productos más caros



SELECT TOP 15
    product_id,
    name,
    price
FROM dbo.products
ORDER BY price DESC;


-- 3. Primer pedido de cada usuario

SELECT 
    u.name,
    MIN(o.order_date) AS primer_pedido
FROM dbo.users u
JOIN dbo.orders o ON u.user_id = o.user_id
GROUP BY u.name;




-- NIVEL INTERMEDIO
-- 4. Ticket promedio 2024
SELECT 
    AVG(total_amount) AS ticket_promedio_2024
FROM dbo.orders
WHERE YEAR(order_date) = 2024;





-- 5. Top 5 productos más vendidos
SELECT TOP 5
    p.product_id,
    p.name,
    SUM(oi.quantity) AS total_unidades
FROM dbo.order_items oi
JOIN dbo.products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name
ORDER BY total_unidades DESC;


-- 6. Usuarios que nunca compraron
SELECT 
    u.name,
    u.email
FROM dbo.users u
LEFT JOIN dbo.orders o ON u.user_id = o.user_id
WHERE o.order_id IS NULL;






-- NIVEL AVANZADO
-- -- 7. Análisis de líneas — validación matemática
SELECT 
    o.order_id,
    COUNT(DISTINCT oi.product_id) AS items_distintos,
    SUM(oi.quantity * oi.unit_price) AS suma_lineas,
    o.total_amount,
    CASE 
        WHEN ABS(SUM(oi.quantity * oi.unit_price) - o.total_amount) < 0.01 
        THEN 'OK' 
        ELSE 'DISCREPANCIA' 
    END AS validacion
FROM dbo.orders o
JOIN dbo.order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.total_amount;
-- 8. Impacto de la integración — ventas por categoría
SELECT 
    c.name AS categoria,
    COUNT(oi.order_item_id) AS total_ventas,
    SUM(oi.quantity) AS unidades_vendidas
FROM dbo.order_items oi
JOIN dbo.products p ON oi.product_id = p.product_id
JOIN dbo.categories c ON p.category_id = c.category_id
GROUP BY c.name
ORDER BY total_ventas DESC;
-- 9. Top 3 usuarios que más gastaron + su categoría favorita
SELECT TOP 3
    u.name AS usuario,
    SUM(o.total_amount) AS total_gastado,
    (
        SELECT TOP 1 c.name
        FROM dbo.order_items oi2
        JOIN dbo.products p2 ON oi2.product_id = p2.product_id
        JOIN dbo.categories c ON p2.category_id = c.category_id
        WHERE oi2.order_id IN (
            SELECT order_id FROM dbo.orders WHERE user_id = u.user_id
        )
        GROUP BY c.name
        ORDER BY SUM(oi2.quantity) DESC
    ) AS categoria_favorita
FROM dbo.users u
JOIN dbo.orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.name
ORDER BY total_gastado DESC;
-- 10. La Métrica Definitiva — revenue por categoría por año

SELECT 
    c.name AS categoria,
    YEAR(o.order_date) AS anio,
    COUNT(DISTINCT o.order_id) AS pedidos,
    SUM(oi.quantity) AS unidades,
    SUM(oi.quantity * oi.unit_price) AS revenue_usd
FROM dbo.orders o
JOIN dbo.order_items oi ON o.order_id = oi.order_id
JOIN dbo.products p ON oi.product_id = p.product_id
JOIN dbo.categories c ON p.category_id = c.category_id
GROUP BY c.name, YEAR(o.order_date)
ORDER BY anio, revenue_usd DESC;
