# PharmaPulse - Findings & Recommendations
*Data: synthetic, 1,200 doctors, 24 reps, 8 territories, 6 products, Jan-Dec 2025. Revenue in Rs.*

## Headline
Sales effort is only loosely matched to doctor potential. The sales force made **19,435 visits** to generate **Rs 63.4M**, but 27.8% of visits go to doctors who produce 16.1% of revenue, while 52 high-potential doctors get just 2.2% of visits.

## Key findings
1. **Revenue is concentrated.** Top 20% of doctors deliver 48.2% of revenue (SQL Q5), so targeting matters.
2. **Tiering is inaccurate.** 60 true high-potential doctors sit in Tier C (lowest priority), and 26 Tier A doctors are not high potential (Python); SQL Q7 shows the same pattern.
3. **Four doctor segments** (potential vs visits):
   | Segment | Doctors | Avg potential | Avg visits/yr | % visits | % revenue |
   |---|---|---|---|---|---|
   | Protect & Grow (Core) | 360 | 47.7 | 26.6 | 49.3 | 57.6 |
   | Under-served (Increase) | 52 | 42.0 | 8.2 | 2.2 | 6.2 |
   | Over-served (Reduce) | 300 | 16.7 | 18.0 | 27.8 | 16.1 |
   | Maintain (Low-touch) | 488 | 14.5 | 8.2 | 20.7 | 20.1 |
4. **Territories differ in efficiency.** Delhi (Rs 10.2M) and Bengaluru (Rs 10.2M) lead on revenue; Bengaluru also has the best revenue per visit (Rs 3,721) and per doctor (Rs 62k). Jaipur is last on revenue and revenue per visit (Rs 2,939).
5. **Products.** CardioSafe (24.1%), GlucoBalance (21.6%) and NeuroCalm (19.6%) make up about 65% of revenue; GastroEase is smallest (9.9%).
6. **Diminishing returns.** After controlling for potential, a 10% increase in annual visits is associated with about 1.4% more revenue (elasticity 0.14). Extra visits beyond the core level add little.
7. **Churn risk.** 10 high-potential doctors saw revenue fall more than 10% from H1 to H2 (SQL Q9 lists the largest declines).

## Recommendations
1. **Re-tier doctors using potential, not rep judgement.** Refresh tiers quarterly with the potential score plus recent sales.
2. **Rebalance visits.** Cut about 30% of visits to the 300 over-served doctors (about 1,620 visits) and redirect them to the 52 under-served doctors, weighted by potential.
3. **Move low-potential doctors to low-touch channels** (virtual calls, email, samples) rather than in-person visits.
4. **Put the 10 declining high-potential doctors on a recovery list** for manager review and a senior rep visit within 30 days.
5. **Territory plans:** use Bengaluru's coverage model as a benchmark; diagnose Jaipur (small doctor base, low efficiency) before adding headcount.
6. **Protect the three lead brands**; examine GastroEase positioning with gastro specialists.

## Estimated impact (illustrative)
Using the visit elasticity (0.14), the reallocation lifts revenue by about **Rs 0.55M (+0.9%)** with no extra visits. The gain is modest because returns flatten; the larger value is in cutting waste, which could free capacity for new launches. Treat this as a directional estimate from observational (not experimental) data; a pilot with a control group is the right validation.

## Limitations
- Synthetic data: patterns were designed in, so real data would be noisier.
- Potential is a CRM estimate, not measured market size.
- Elasticity is correlational; reps may visit doctors who already prescribe more.
- No cost data, so ROI is not computed.
