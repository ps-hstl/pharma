-- Q2: Monthly revenue with MoM growth (window function LAG)
WITH m AS (
  SELECT month, SUM(revenue) AS revenue, SUM(units) AS units FROM sales GROUP BY month)
SELECT month, revenue, units,
       ROUND(100.0*(revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM m ORDER BY month;
