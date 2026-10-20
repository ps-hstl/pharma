-- Q8: Rep productivity, ranked within territory (PARTITION BY)
WITH rv AS (SELECT rep_id, COUNT(*) AS visits, ROUND(AVG(duration_min),1) AS avg_min FROM visits GROUP BY 1),
rs AS (SELECT d.rep_id, SUM(s.revenue) AS revenue FROM sales s JOIN doctors d USING(doctor_id) GROUP BY 1)
SELECT t.territory_name, r.rep_id, r.tenure_years, rv.visits, rv.avg_min, rs.revenue,
       ROUND(1.0*rs.revenue/rv.visits,0) AS revenue_per_visit,
       RANK() OVER (PARTITION BY r.territory_id ORDER BY rs.revenue DESC) AS rank_in_territory
FROM reps r JOIN rv USING(rep_id) JOIN rs USING(rep_id) JOIN territories t USING(territory_id)
ORDER BY t.territory_name, rank_in_territory;
