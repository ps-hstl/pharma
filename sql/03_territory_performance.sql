-- Q3: Territory scorecard: revenue, visits, doctors, revenue per visit, rank
WITH s AS (SELECT d.territory_id, SUM(sa.revenue) AS revenue FROM sales sa JOIN doctors d USING(doctor_id) GROUP BY 1),
     v AS (SELECT d.territory_id, COUNT(*) AS visits FROM visits vi JOIN doctors d USING(doctor_id) GROUP BY 1),
     c AS (SELECT territory_id, COUNT(*) AS doctors FROM doctors GROUP BY 1)
SELECT t.territory_name, t.region, c.doctors, v.visits, s.revenue,
       ROUND(1.0*s.revenue/v.visits, 0) AS revenue_per_visit,
       ROUND(1.0*s.revenue/c.doctors, 0) AS revenue_per_doctor,
       RANK() OVER (ORDER BY s.revenue DESC) AS revenue_rank
FROM territories t JOIN s USING(territory_id) JOIN v USING(territory_id) JOIN c USING(territory_id)
ORDER BY revenue DESC;
