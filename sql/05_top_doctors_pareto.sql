-- Q5: Pareto - how concentrated is revenue? (cumulative share via window functions)
WITH d AS (SELECT doctor_id, SUM(revenue) AS revenue FROM sales GROUP BY 1),
r AS (SELECT doctor_id, revenue,
             ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn,
             SUM(revenue) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING) AS cum_rev,
             SUM(revenue) OVER () AS total FROM d)
SELECT rn AS doctor_rank, doctor_id, revenue,
       ROUND(100.0*cum_rev/total, 1) AS cum_revenue_pct,
       ROUND(100.0*rn/(SELECT COUNT(*) FROM d), 1) AS cum_doctor_pct
FROM r WHERE rn IN (12,60,120,240,360,600,1200) ORDER BY rn;
