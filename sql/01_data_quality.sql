-- Q1: Row counts + integrity checks (orphans, duplicates, nulls)
SELECT 'doctors' AS tbl, COUNT(*) AS n,
       0 AS orphans FROM doctors
UNION ALL SELECT 'visits', COUNT(*), SUM(doctor_id NOT IN (SELECT doctor_id FROM doctors)) FROM visits
UNION ALL SELECT 'sales',  COUNT(*), SUM(doctor_id NOT IN (SELECT doctor_id FROM doctors)) FROM sales
UNION ALL SELECT 'duplicate_visit_ids', COUNT(*) - COUNT(DISTINCT visit_id), 0 FROM visits
UNION ALL SELECT 'null_potential', SUM(est_monthly_potential IS NULL), 0 FROM doctors;
