-- Q6: Core business question - does visit effort match doctor potential?
-- Potential tertile vs average visits per doctor and revenue per doctor
WITH dv AS (SELECT doctor_id, COUNT(*) AS visits FROM visits GROUP BY 1),
ds AS (SELECT doctor_id, SUM(revenue) AS revenue FROM sales GROUP BY 1),
base AS (
  SELECT d.doctor_id, d.est_monthly_potential AS potential, d.assigned_tier,
         COALESCE(dv.visits,0) AS visits, COALESCE(ds.revenue,0) AS revenue,
         NTILE(3) OVER (ORDER BY d.est_monthly_potential) AS pot_tertile
  FROM doctors d LEFT JOIN dv USING(doctor_id) LEFT JOIN ds USING(doctor_id))
SELECT CASE pot_tertile WHEN 1 THEN '1-Low' WHEN 2 THEN '2-Mid' ELSE '3-High' END AS potential_group,
       COUNT(*) AS doctors,
       ROUND(AVG(visits),1) AS avg_visits_yr,
       ROUND(AVG(revenue),0) AS avg_revenue,
       ROUND(1.0*SUM(revenue)/SUM(visits),0) AS revenue_per_visit
FROM base GROUP BY pot_tertile ORDER BY pot_tertile;
