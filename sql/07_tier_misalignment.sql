-- Q7: Rep-assigned tier vs actual potential tertile (mis-tiering matrix)
WITH b AS (SELECT assigned_tier,
    CASE NTILE(3) OVER (ORDER BY est_monthly_potential) WHEN 1 THEN 'Low' WHEN 2 THEN 'Mid' ELSE 'High' END AS true_potential
    FROM doctors)
SELECT assigned_tier,
       SUM(true_potential='High') AS high_pot, SUM(true_potential='Mid') AS mid_pot, SUM(true_potential='Low') AS low_pot,
       COUNT(*) AS total
FROM b GROUP BY assigned_tier ORDER BY assigned_tier;
