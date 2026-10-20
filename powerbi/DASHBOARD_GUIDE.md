# Power BI build guide (about 60-90 min)

Import from `data/powerbi/`: dim_doctor, dim_product, dim_territory, dim_rep, dim_date, fact_sales, fact_visits, segment_summary.
Reference picture: `reports/charts/07_dashboard_preview.png`.

## 1. Data model (star schema, all 1-to-many, single direction)
| From (one) | To (many) | Key |
|---|---|---|
| dim_doctor | fact_sales, fact_visits | doctor_id |
| dim_product | fact_sales, fact_visits | product_id |
| dim_territory | dim_doctor, dim_rep | territory_id |
| dim_rep | fact_visits | rep_id |
| dim_date | fact_sales, fact_visits | month (text yyyy-mm) |

Hide key columns and mark `dim_date[month_start]` as date. Sort `month_name` by `month_num`.

## 2. DAX measures
```DAX
Revenue = SUM(fact_sales[revenue])
Units = SUM(fact_sales[units])
Visits = COUNTROWS(fact_visits)
Active Doctors = DISTINCTCOUNT(fact_sales[doctor_id])
Revenue per Visit = DIVIDE([Revenue], [Visits])
Revenue per Doctor = DIVIDE([Revenue], [Active Doctors])
Visits per Doctor = DIVIDE([Visits], DISTINCTCOUNT(dim_doctor[doctor_id]))

Revenue PM = CALCULATE([Revenue], DATEADD(dim_date[month_start], -1, MONTH))
MoM Growth % = DIVIDE([Revenue] - [Revenue PM], [Revenue PM])

Revenue Share % = DIVIDE([Revenue], CALCULATE([Revenue], ALL(dim_product)))
Visit Share % = DIVIDE([Visits], CALCULATE([Visits], ALL(dim_doctor)))
Revenue Share % (Segment) = DIVIDE([Revenue], CALCULATE([Revenue], ALL(dim_doctor[segment])))
Effort-Outcome Gap = [Visit Share %] - [Revenue Share % (Segment)]   -- positive = over-invested

Virtual Visit % = DIVIDE(CALCULATE([Visits], fact_visits[visit_type] = "Virtual"), [Visits])
```

## 3. Page 1 - Executive Overview
- 4 KPI cards: Revenue, Active Doctors, Visits, Revenue per Visit
- Line chart: Revenue by month (dim_date[month_name])
- Bar: Revenue by territory_name; Donut or bar: Revenue by product_name
- Slicers: region, therapy_area, specialty

## 4. Page 2 - Doctor Segmentation
- Scatter: X = est_monthly_potential, Y = visits_12m, Legend = segment, Details = doctor_id (colors: Core navy, Under-served red, Over-served orange, Maintain grey)
- Clustered column: Visit Share % vs Revenue Share % (Segment) by segment
- Matrix: assigned_tier (rows) x potential_group (columns), count of doctors
- Table: top 20 under-served doctors (filter segment = "Under-served (Increase)", sort by est_monthly_potential)

## 5. Page 3 - Territory & Rep Performance
- Table: territory_name, Revenue, Visits, Revenue per Visit, Revenue per Doctor (conditional-format Revenue per Visit)
- Bar: Revenue per Rep (dim_rep[rep_id]); slicer on territory
- Drill-through page: Doctor detail (specialty, tier, potential, monthly visits and revenue)

## 6. Polish
Consistent palette, titles that state the insight ("27.8% of visits go to 16.1% of revenue"), tooltips, mobile layout off. Save as `PharmaPulse.pbix`, export a PDF and add screenshots to the GitHub README.
