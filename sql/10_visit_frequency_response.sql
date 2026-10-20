-- Q10: Diminishing returns - revenue per doctor by visit-frequency band (controlling for potential group)
WITH dv AS (SELECT doctor_id, COUNT(*) AS visits FROM visits GROUP BY 1),
ds AS (SELECT doctor_id, SUM(revenue) AS revenue FROM sales GROUP BY 1),
b AS (SELECT d.doctor_id, COALESCE(dv.visits,0) AS visits, COALESCE(ds.revenue,0) AS revenue,
      CASE NTILE(3) OVER (ORDER BY d.est_monthly_potential) WHEN 1 THEN 'Low' WHEN 2 THEN 'Mid' ELSE 'High' END AS pot
      FROM doctors d LEFT JOIN dv USING(doctor_id) LEFT JOIN ds USING(doctor_id))
SELECT pot AS potential_group,
       CASE WHEN visits<=6 THEN 'a) 0-6' WHEN visits<=12 THEN 'b) 7-12' WHEN visits<=24 THEN 'c) 13-24' ELSE 'd) 25+' END AS visit_band,
       COUNT(*) AS doctors, ROUND(AVG(revenue),0) AS avg_revenue
FROM b GROUP BY 1,2 ORDER BY 1,2;
