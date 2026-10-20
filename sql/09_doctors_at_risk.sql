-- Q9: High-potential doctors with declining sales (H2 vs H1) - churn-risk list
WITH h AS (SELECT doctor_id,
   SUM(CASE WHEN month<='2025-06' THEN revenue ELSE 0 END) AS h1,
   SUM(CASE WHEN month> '2025-06' THEN revenue ELSE 0 END) AS h2 FROM sales GROUP BY 1)
SELECT d.doctor_id, d.specialty, d.est_monthly_potential AS potential, d.assigned_tier, h.h1, h.h2,
       ROUND(100.0*(h.h2-h.h1)/h.h1,1) AS change_pct
FROM h JOIN doctors d USING(doctor_id)
WHERE h.h1>0 AND h.h2<h.h1*0.9 AND d.est_monthly_potential >= (SELECT est_monthly_potential FROM doctors ORDER BY est_monthly_potential LIMIT 1 OFFSET 800)
ORDER BY h.h1-h.h2 DESC LIMIT 25;
