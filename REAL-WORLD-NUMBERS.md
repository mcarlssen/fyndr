Recap table — all real-world datapoints we’ve collected so far

Below is a compact reference table summarizing the empirical datapoints and recommended simulation knobs I’ve given you so far (numbers are benchmarks or recommended baselines to plug into your sim). I mark the most load-bearing claims with citations.

Topic	                                    Empirical benchmark / recommended baseline	                                Notes / source

Paying-user penetration (install → payer)	0.2% – 2% typical; top titles can be higher.	                            Use a planning range 0.2–2% depending on genre & UA. 

Paying user spending distribution	        Heavy skew / whales — tiny % of users produce large share of revenue.	    Expect extreme long tail; model a small whale cohort (0.5–3%) with high ARPPU. 

Typical purchase frequency for payers	    Example conservative baseline 1.2 purchases/month → daily ≈ 4% per day      Used earlier to convert purchases/month → p/day for payers.
                                            (conditional on payer) (Poisson approx).	                                

Price bands to test	                        Impulse $0.99–$1.99; Core pack $3.99–$6.99;                                 Industry best practice: mix cheap+mid+high.  
                                            Mid/high $9.99–$19.99; Collector $24.99+.

Grinders vs casual split	                Grinders ≈ 20–30%, Casual ≈ 70–80% (use 17–20% grinders as you had).	    Based on genre segmentation & PC/mobile studies. 

Grinders paying behavior	                Not zero — reasonable to assume 5–15% of grinders convert to                Data shows core players more likely to purchase; 
                                            payers (recommended), not 0%.	                                            pure zero loses revenue realism. 

Purchase behavior (whales)              	Whales small % (1–3%); high purchase frequency (2–4+ / month)           	Model whales separately and cap diminishing returns. 
                                            and large ARPPU.

Referral conversion rates	                Invite→install conversion varies widely; incentivized referrals can be      Use conservative 5% if invite is casual/no reward; 
                                            10–30%; organic share often single-digit %.	                                use 10–30% if properly incentivized. 

Invites/user (organic)	                    Typical organic I 0.1–0.5 invites/user/month; incentivized programs         Most users send 0 invites; top sharers drive the mean. 
                                            can push I ~1.0+/month for active cohorts.	

K_month (recommended sim bands)	            Conservative K_month ≈ 0.005; Realistic K_month ≈ 0.03;                     Translate to per-day p_day ~ 
                                            Optimistic K_month ≈ 0.10–0.30.	                                            0.00017 → 0.001 → 0.0033–0.01 respectively.  
                                            
Baseline per-day recruit probability    	p_day = 0.001 (0.1% per day per active player) —                            ~10 new users/day per 10k active players.  
                                            conservative but meaningful baseline to start.	