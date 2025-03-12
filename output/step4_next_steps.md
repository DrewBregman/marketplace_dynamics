## 1. Research Priorities

1. **Quantifying Non-Wage Drivers of Shift Appeal**  
   • **Gap**: While compensation plays a role, many workers prioritize facility conditions, scheduling convenience, and reputation. We lack a structured, quantitative measure of these non-wage attributes.  
   • **Rationale**: Understanding how facility reputation and shift desirability factors stack up against wages will help in prioritizing improvement efforts and reducing reliance on pay inflation.  
   • **Benefit**: Pinpointing which specific non-wage factors matter most (e.g., manager communication, parking availability, cancellation rates) can guide tailored facility-level interventions.

2. **Optimal Timing and Magnitude of Pay Adjustments**  
   • **Gap**: We know that one larger, well-timed increase can outperform multiple small increments—but we do not know the precise “trigger thresholds” for different shift types and worker segments.  
   • **Rationale**: Identifying threshold points for wage elasticity can inform more accurate initial offers, thereby reducing repeated adjustments and improving fill velocity.  
   • **Benefit**: This directly addresses Patterns B and C, potentially driving down overall costs and reinforcing worker trust through transparent, decisive offers.

3. **Facility Reputation Dynamics and Recovery**  
   • **Gap**: We know facilities with poor reputations pay more and fill slower, but it’s unclear how long it takes to repair reputational damage (e.g., after improved management or reduced cancellations).  
   • **Rationale**: Measuring how quickly worker sentiment shifts when conditions improve can help tailor interventions and messaging to speed up facility “recovery.”  
   • **Benefit**: Could offer a roadmap for struggling facilities to regain trust, thus stabilizing their staffing costs.

4. **Segment Transition Drivers and Retention**  
   • **Gap**: High-volume (Segment A) workers occasionally “burn out” and shift to lower engagement levels. We need deeper insight into why and how to reinvigorate them.  
   • **Rationale**: Segment A represents a high proportion of claims and marketplace liquidity. Minimizing churn or temporary drop-offs maintains stable coverage.  
   • **Benefit**: Sustained engagement of top contributors reduces last-minute bidding wars and ensures consistent availability for more routine shifts.

5. **Spillover Mechanics During Peak Demand**  
   • **Gap**: While we see Segment B or dormant workers step up during flu season or emergencies, we lack a clear model of how pay, shift length, or other perks drive these activations.  
   • **Rationale**: Improving seasonal forecasting and understanding triggers that reactivate dormant supply can significantly reduce crisis-driven shortages.  
   • **Benefit**: Enables planned “surge staffing” strategies that are cost-effective and timely, rather than reactive, high-pay scrambling.

---

## 2. Data Collection Plan

1. **Expanded Facility Attribute Scores**  
   • **Data Points**: Worker rating of facility environment, manager responsiveness, shift organization, and cancellation history (beyond raw counts).  
   • **Collection Methods**: Post-shift surveys or quick rating prompts; tracking reasons behind cancellations (facility-driven vs. worker-driven).  
   • **Complement to Existing Analysis**: Creates a more detailed “reputation profile,” allowing us to correlate fill rates with each sub-attribute.

2. **Shift Posting and Update Log**  
   • **Data Points**: Timestamps and details of every shift posting, including any subsequent changes to pay rate or shift parameters.  
   • **Collection Methods**: Automated event logging within the platform whenever a facility modifies shift details.  
   • **Complement to Existing Analysis**: Supports investigating how timing and magnitude of adjustments affect fill velocity and final compensation (Patterns B and C).

3. **Worker Interaction Traces**  
   • **Data Points**: Login frequency, shift browsing time, reason for rejecting or not claiming a shift (if voluntarily shared), skill or specialty tags.  
   • **Collection Methods**: Application usage logging coupled with optional exit surveys or “why did you pass” quick forms.  
   • **Complement to Existing Analysis**: Refines segment definitions (A vs. B) and helps detect early signals of worker disengagement or shifting preferences.

4. **Seasonal Engagement and Re-Engagement Triggers**  
   • **Data Points**: Worker reactivation rates correlated with specific incentives (e.g., surge pay, personal outreach messages, crisis or holiday situations).  
   • **Collection Methods**: Targeted push notifications or email campaigns with trackable links to see who reactivates.  
   • **Complement to Existing Analysis**: Builds a predictive model for dormant-to-active transitions, helping forecast workforce capacity during peak or crisis periods.

5. **Worker-Reported “Facility Improvement” Data**  
   • **Data Points**: For facilities undergoing improvements (e.g., new management, better scheduling practices), worker feedback on noticed changes.  
   • **Collection Methods**: Follow-up surveys after a first shift at the “improved” facility.  
   • **Complement to Existing Analysis**: Evaluates how quickly reputation can rebound when changes are made, validating or refuting the “spiral” theory around cancellations and negative experiences.

---

## 3. Validation Approaches

1. **Multivariate Regression and Elasticity Modeling**  
   • **Purpose**: Isolate the effect of wage vs. non-wage variables (facility rating, shift timing) on fill velocity.  
   • **Technique**: Use a mixed-effects model controlling for facility ID as a random effect, capturing repeated measures over time.  
   • **Causality vs. Correlation**: Sequential modeling can be employed—examining fill velocity changes immediately following a wage bump or facility improvement—to strengthen causal inferences.

2. **Difference-in-Differences (DiD) Analysis**  
   • **Purpose**: Evaluate facility reputation recovery after interventions (e.g., new scheduling policy).  
   • **Technique**: Compare “treated” facilities (implementing an improvement) against a control group of similar facilities that did not. Track fill rates and cost trends over matching time horizons.  
   • **Causality vs. Correlation**: By establishing comparable baselines and parallel trends, DiD helps attribute changes in staffing metrics to the specific intervention.

3. **Segmentation Stability Check**  
   • **Purpose**: Confirm the existence and behavior of worker segments (A vs. B), especially transitions.  
   • **Technique**: Cluster analysis on shift-claiming frequency, wage sensitivity, and times claimed. Track individuals over time to detect movement from high-volume to selective status.  
   • **Causality vs. Correlation**: Observing changes in claim patterns following external stressors (e.g., personal schedule changes, platform policy updates) can suggest causal reasons for segment switching.

4. **Early Click-to-Claim Indicators**  
   • **Purpose**: Validate whether the first 2-3 hours of posting predict final fill outcomes and total cost.  
   • **Technique**: Construct a predictive model with “initial click-to-claim ratio” as a leading variable, controlling for shift type, location, and time of day. Compare model performance vs. baseline.  
   • **Causality vs. Correlation**: If strong early metrics consistently forecast final results, it increases confidence that real-time interventions (e.g., immediate pay revision) could be effective.

---

## 4. Limited Experiments

1. **Single vs. Multiple Pay Bumps**  
   • **Hypothesis**: One-time, larger pay increases (20%+) at the initial posting outperform incremental 5% increases repeated over time.  
   • **Design**: Randomly select a set of upcoming shifts at representative facilities. Half post an upfront, more substantial wage increase; the other half rely on multiple small increments.  
   • **Measurements**: Time to first claim, total cost, final wages paid, worker feedback.  
   • **Interpretation**: Shorter fill times and lower total cost in the “one-time bump” group would confirm Pattern B and C. If no difference emerges, it suggests a simpler re-pricing approach might suffice.

2. **Facility Improvement Disclosure**  
   • **Hypothesis**: Publicizing specific changes (e.g., new scheduling manager) can accelerate reputation recovery and fill rates.  
   • **Design**: For facilities with a history of poor ratings that have implemented improvements, label shifts in the app (“Under New Management”) vs. no label in a control group.  
   • **Measurements**: Shift claim speed, wage levels needed, worker satisfaction post-shift.  
   • **Interpretation**: If labeled shifts see fewer pay revisions and faster fill, it suggests direct communication of improvements helps rebuild trust.

3. **Targeted Re-Engagement Offers to Dormant Workers**  
   • **Hypothesis**: Personalized outreach (mentioning facility closeness, relevant specialties) plus moderate pay boost reactivates dormant workers more effectively than a generic broadcast.  
   • **Design**: Two groups of dormant workers—one receives tailored messages and targeted shift suggestions, the other receives general promotional emails.  
   • **Measurements**: Re-engagement rate, subsequent shift claims, time from message to claim.  
   • **Interpretation**: A higher claim rate from the personalized group indicates the power of targeted incentives and communication in expanding supply.

---

## 5. Counter-Hypothesis Testing

1. **Alternative Explanation for Non-Wage Sensitivity**  
   • **Possibility**: High fill rates at certain facilities might be due to geographic convenience or worker familiarity, not purely “reputation” or favorable conditions.  
   • **Method**: Control for commute distance, public transport access, and worker’s prior experience with the facility in the regression analysis.  
   • **Critical Assumption**: The difference in fill speed is truly about intangible reputation factors; robust location and shift familiarity controls are needed to confirm or refute.

2. **Questioning Pay Thresholds**  
   • **Possibility**: The abrupt elasticity “cliff” could be driven by seasonal scheduling changes or competitor facility closings, not the wage crossing a key threshold.  
   • **Method**: Compare fill rates before and after the same wage threshold in different seasons or market conditions. Look at competitor facility postings during the same window.  
   • **Critical Assumption**: Wage thresholds are universal triggers. Testing across varied market conditions helps confirm if the effect is consistent or situational.

3. **Worker Segment Fluidity**  
   • **Possibility**: The line between Segment A (high-volume) and Segment B (selective) is more porous than assumed; external factors (e.g., personal schedule changes, licensing status) may dominate.  
   • **Method**: Include life or schedule event data (if available) to see if it correlates with a sudden drop in shift claims, versus platform or facility-level factors.  
   • **Critical Assumption**: Segmentation is primarily driven by marketplace changes. If personal events overshadow marketplace drivers, the entire strategy to retain Segment A might need rethinking.

By systematically examining these counter-hypotheses, we ensure that the proposed strategies—such as early decisive wage setting and reputation-focused initiatives—are genuinely addressing root causes rather than coincidental correlations. This comprehensive research plan lays the groundwork for a more data-driven, efficient, and equitable healthcare staffing marketplace.