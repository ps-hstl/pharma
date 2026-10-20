-- Q4: Product revenue, share of total, H1 vs H2 growth
SELECT p.product_name, p.therapy_area,
       SUM(s.revenue) AS revenue,
       ROUND(100.0*SUM(s.revenue)/SUM(SUM(s.revenue)) OVER (), 1) AS revenue_share_pct,
       SUM(CASE WHEN s.month <= '2025-06' THEN s.revenue END) AS h1_revenue,
       SUM(CASE WHEN s.month >  '2025-06' THEN s.revenue END) AS h2_revenue,
       ROUND(100.0*(SUM(CASE WHEN s.month > '2025-06' THEN s.revenue END)*1.0 /
                    SUM(CASE WHEN s.month <= '2025-06' THEN s.revenue END) - 1), 1) AS h2_vs_h1_pct
FROM sales s JOIN products p USING(product_id)
GROUP BY p.product_name, p.therapy_area ORDER BY revenue DESC;
