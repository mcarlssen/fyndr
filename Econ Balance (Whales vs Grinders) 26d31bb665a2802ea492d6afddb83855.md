# Econ Balance (Whales vs. Grinders)

# Key Questions

1. How do we make the stickers desirable and monetizable?
2. Could the sticker shape itself change as the user ascends leaderboard tiers? Perhaps reflecting the tier by the number of sides - tier 3 is a triangle, tier 4 is a square, tier five is a pentagon, etc
3. Holo, foil, transparent, or metallic stickers are the most obvious copy-protection methods. This is expensive to produce. What strategies can be found to mitigate this cost? Embossing? NFC? How does this scale in manufacturing?
4. How do we prevent sticker spoofing?

# TL;DR

- Make “fancier” stickers primarily cosmetic plus small network-effect multipliers, never raw point bombs.
- Let every advantage from purchases be earnable via play with more effort or time.
- Price packs to hit a healthy per-pack contribution, and push bundles or wallet top-ups to amortize shipping and fees.
- Use layered, cheap-to-scale authenticity: per-sticker unique IDs + app attestation + periodic server checks; reserve expensive finishes for higher tiers and promos.

---

### 1) A simple, fair economy model

Design goal: buying helps you express status and seed new scans, but playing hard can match the same progression.

- Currencies and obtainables
    - Soft currency: Points from scans and quests.
    - Hard currency: Optional wallet top-ups for buying packs, cosmetics, or limited drops.
    - Obtainables: Sticker, in-app cosmetic reactions when sticker is scanned, seasonal sticker sets, limited-tier upgrades.
- Progression and multipliers
    - Base multiplier per sticker: 1.0
    - Tiered sticker multipliers: 1.05, 1.10, 1.15, 1.20 (cap at ~2x). These apply to both owner and scanner to encourage others to seek them out.
    - Possible: players advance by points level AND activity gates: e.g., Tier 2 requires points Level 5 plus “10 unique scans in 5 venue categories.” This way, a purchase-only player cannot skip the gate;  they only save time once the gate is met.
- Earned vs bought sticker acquisition
    - Earn path: 60–70% of sticker packs are earnable via points and quests. Time-to-pack target: 3–5 days for an engaged player.
    - Buy path: 30–40% come from micro-purchases or wallet redemptions. Purchased packs include limited art or finish variants but the same multiplier caps.
- Anti pay-to-win guardrails
    - Diminishing returns per sticker per day and per account per week.
        - NOT SURE this works. Don't want stickers to devalue because that defeats the purpose of buying them. Farmers should be able to invest $1000 and be rewarded accordingly - after all, they are providing the economy for grinders. The natural outcome is that a whale dumping $1000 into the local game economy ALSO produces a surge in grinder points. ACTION ITEM: *do the math to make sure this doesn’t create a runaway affect.*
    - Weekly “earn cap parity”: the maximum points advantage from purchases alone is bounded to ~10–15% of a fully free player who hits weekly quests and diversity bonuses.
        - What if instead there was a silent ‘density’ factor which reduced sticker multipliers of placements too near that farmers other stickers? This encourages the player to expand their physical range and limits how much they will buy, by virtue of sticker points depreciation over time as they level up. This avoids directly nerfing a whale’s earning capability, and instead simply forces them to put in more work.
    - Activity backstops: high-value quests and “courier missions” let grinders beat whales through effort.
        - This margin of advantage should be small - 5-10% at most. Rely on players being lazy to drive revenue. Make the game fun for grinders.

---

### 2) Monetization pillars that respect fairness

- Physical pack sales
    - Anchor price: $3 pack incl. shipping for bundles. Encourage 2-pack or 4-pack checkout to amortize postage and fixed fees.
    - Limited seasonal sets and collabs at small price premia (+$0.50–$1.00) tied to events. Cosmetic value > power.
- Wallet top-ups
    - $5–$10 increments that can be used for new stickers or app cosmetics. Bundles occasionally include a “booster weekend” token that increases scanner earnings, not owner earnings. This drives engagement to that whale’s stickers.
- Cosmetics and identity
    - Profile frames, map skins, sticker halos, club banners, scan reactions. Purely visual or tiny social utility. Priced for impulse buys.
- Rewarded ads (opt-in only)
    - Streak protection, revive a missed quest, minor scanner bonus for the next 1–3 scans. No permanent power gain.
- Local sponsorships
    - Sponsored zones and treasure routes that temporarily boost scanner rewards in specific areas; the boost applies equally to all players in-zone.

---

### 3) Example numbers to tune

Use these to simulate and find your balance; adjust to your audience.

- Earning pace targets
    - Engaged player: 40–70 points/day achievable via scanning others, diversity bonuses, and dailies.
    - Pack price in points: 250–350 points per 6-pack for non-limited art. Means 4–7 days per earned pack.
    - Cosmetic-only rewards at 50–120 points to keep daily wins flowing.
- Multipliers
    - Tier 1: 1.00
    - Tier 2: 1.05
    - Tier 3: 1.10
    - Tier 4: 1.15
    - Tier 5: 1.20
    Never exceed ~2x outside of time-limited events.
- Diminishing returns
    - Per-sticker daily scans: full value for first 3 unique scans, then 50%, then 25% flat.
    - Per-account soft cap: after N high-value scans per day, subsequent scans earn reduced points until reset.
    - *ACTION ITEM: does this work? Not convinced that daily diminishing returns are a good idea.*
- Effort compensation rule of thumb
    - A buyer placing more stickers gains surface area.
    - A grinder can match by:
        - Scanning in diverse venues and distances
        - Finishing weekly courier missions
        - Chaining “social sneeze” bonuses
        Target: an engaged grinder can earn 105-110% of a light spender’s weekly net points.

---

### 

---

### 7) Next steps to de-risk quickly

- Simulate with your current unit-econ sheet:
    - Test points-per-pack at 250, 300, 350 and multipliers capped at 1.20.
    - Model buyer rate at 40%, 50%, 60% and average packs per buyer per season at 2.0, 2.7, 3.5.
- Run a campus micro-pilot:
    - Two SKUs: Standard vinyl vs. “holo edge” limited run.
    - A/B daily quest pacing and earned-pack price.
    - Measure scan diversity, time-to-first-scan, and counterfeit flags.

If you want, I can draft a short “Economy and Anti-Abuse Tuning” section on your Development questions page with the numbers above, plus a pilot test matrix.

- Yes: “passive points from others scanning your placements” can be the main purchase incentive, as long as the passive yield is capped and counterbalanced by active scanning and quests.
- Two complementary economies work well: a Scanning economy (active play) and a Farming economy (placement yield). Tie them together so either path can win locally, and the best players blend both.
- Cosmetics can be deprioritized. You can still sell “utility” sticker packs and location boosts without profile bling.
- Rewarded ads can be meaningful but will likely be secondary to sticker revenue. Sponsorships can out-earn both on a per‑area basis if packaged well.
- “Super stickers” for venues can work, but make them time‑/zone‑limited and scanner‑oriented so they don’t break fairness.

---

### 1) Make passive yield the core purchase incentive, safely

Think of a sticker as a “yield node” that pays points when others scan it.

- Placement yield design
    - Baseline yield per unique scan within a time window.
    - Diminishing returns per sticker per day to prevent spamming surface area.
    - Decay over time without fresh scans to avoid set‑and‑forget farms.
    - Zone competition: overlapping stickers share the pot or reduce each other’s marginal value.
- Fairness guardrails
    - Passive yield soft cap per account per day or week.
    - Active counterbalance: quests, distance and venue diversity bonuses, and “courier” missions that let an active player out-earn a passive farmer on any given day.
    - Strategic play: great placement and seeding networks beat raw sticker count.
- Is passive enough to drive purchases?
    - For many players, yes—if you make three things true:
        1. Time-to-first-yield is short after placement.
        2. Yield feels visible and compounding for “good” placements.
        3. There’s a steady need for more placements to sustain or grow yield due to decay and zone competition.

---

### 2) Two intertwined economies that don’t conflict

- Scanning economy (active)
    - Earn through diversity, distance, streaks, quests, and “social sneeze” chains.
    - Primary tool for new players and dense-city residents.
- Farming economy (passive)
    - Earn from other people scanning your placements.
    - Primary tool for strategic placers and buyers.
- The link
    - Quests that require doing both: place in three distinct venue categories and scan five unique stickers in new areas.
    - Leaderboards can weigh hybrid score: e.g., 60% scanning points + 40% placement yield, rotating weights by week to keep metas fresh.

---

### 3) Quests as the backbone

- Daily: “Scan 5 unique stickers over 2 km total travel” or “Place 1 sticker with photo proof in a new category.”
- Weekly: “Courier” missions to seed new neighborhoods with boosted first‑scan yield.
- Rotating “local events” quests to route foot traffic past sponsor locations.
- Make earned packs a predictable outcome of completing weekly quests so non‑buyers always feel progression.

---

### 4) Skip cosmetics for now, sell utility

- Early monetization pillars without social bling
    - Utility sticker packs: standard vs “premium finish” variants with small passive yield perks like longer decay timer or slightly higher first‑scan bonus.
    - Limited location boosts: “hot zone seeding” tokens that temporarily raise the first N scans’ value after a placement. These should also be earnable via quests to avoid pay‑to‑win.

---

### 5) Ads vs stickers vs sponsorships

- Rewarded ads (opt‑in)
    - Typical early ARPUs: roughly $0.02–$0.05 per completion, a few completions per DAU if well-placed.
    - Directional per‑user per month: $0.05–$0.30 for light ad loads.
    - Useful as a supplement and safety net for streak protection and revives, not a primary revenue source at small scale.
- Sticker sales
    - Your unit‑econ anchor with bundled shipping can produce a healthy contribution per pack.
    - Drives core loop health by creating more placements, which increases scanning fun for everyone.
- Local sponsorships
    - Highest ceiling per geography. Example packages:
        - Starter: $150–$300 for a month of “sponsored hotspot” status with a boosted scan bonus in a small radius.
        - Premium: $500–$1,500 includes a pack of venue “super stickers,” featured map pin, and a weekly quest that routes players past the venue.
        - Civic/edu: free or discounted libraries and parks “community stickers” to seed density and goodwill.
    - Operationally, sell time‑boxed boosts that amplify scanner rewards in‑zone rather than permanent power for the venue owner.

---

### 6) “Super stickers” without breaking fairness

- Make them scanner‑centric and time‑boxed
    - 5–10x base points for the first K unique scans each day in a small radius, resets daily.
    - Everyone benefits by scanning them; no permanent multiplier stored on player accounts.
    - Rotate or throttle if a single venue dominates.
- Anti‑farm safeguards
    - Require on‑site device attestation, short dwell hints, and anti‑cluster logic.
    - Cap per‑account daily earnings from any one super sticker.
    - Sponsor pays for attention, not for leaderboard dominance.

---

### 7) Example tuning targets to test

- Passive yield per placement
    - First 3 unique scans/day at 2 points each to owner, then 1, then 0.5.
    - Decay: −20% daily max yield if no unique scans happen that day, refreshed on a new unique scan.
- Active scanning rewards
    - Diversity bonuses worth 30–50% of an engaged player’s daily points.
    - Weekly quests worth one earned pack plus a “courier token.”
- Earned vs bought pace
    - Earned pack price: 250–350 points.
    - Purchase price: keep the $3 anchor, nudge to 2‑pack checkout to amortize shipping.
- Leaderboard fairness
    - Daily soft cap on passive yield per account that is achievable by a very active free player via scanning and quests.

---

### 8) Fast experiments

- A/B “passive first scan” bump
    - Variant A: +2 owner for first 3 daily uniques.
    - Variant B: +3 for the first daily unique only, then +1s.
    - Measure purchase lift and placement density vs. scan fun.
- Two‑economy leaderboard
    - Week 1: 60% scanning, 40% placement.
    - Week 2: 50/50 with a courier mission spotlight.
- Sponsor pilot
    - Offer 3 SKUs to 5 local venues plus 2 civic locations.
    - Track footfall, scans per dollar, and player sentiment.

If you want, I can draft a “Dual‑Economy and Monetization” section under Development questions with these tuning targets and a 2‑week pilot plan.

### Framing

You’re already leaning into freemium, progression multipliers, and integrity caps in the brief. Below are concrete, low-cost ways to raise perceived value, keep COGS in check for per-player‑unique stickers, and harden against pay‑to‑win while staying aligned with your first‑gen points system and unit‑econ constraints.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)[[2]](Econ%20Balance%20(Whales%20vs%20Grinders)%2026d31bb665a2802ea492d6afddb83855.md)

---

### 1) Increase value in the physical stickers

Make the physical object feel collectible, social, and progression-tied without pricey substrates.

- Progression-visible design layers
    - Tier shapes as you suggested, plus subtle progress rings or “facet notches” added as players level. Same base stock, different artwork files per tier. Visible rarity without foil.[[2]](Econ%20Balance%20(Whales%20vs%20Grinders)%2026d31bb665a2802ea492d6afddb83855.md)
    - Limited seasonal variants and campus drops that rotate. Scarcity feels special even on standard vinyl.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Social status cues at scan-time
    - When a sticker is scanned, show a unique “owner card” with animated frame tied to the physical design set. Physical item unlocks a digital flex moment for both owner and scanner.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Set completion and map collections
    - Print subtle collection IDs on the sticker edge (e.g., “City Set 2 • 5/12”). Completing sets yields small global multipliers and a profile badge. The physical completion chase adds value.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Provenance and “first placement” tags
    - The first successful placement photo and nickname become the sticker’s provenance record. Future scanners see that lineage in-app, giving even common stickers a story.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Community utility
    - Host/business collab marks: small corner icon indicates “partner pin” with boosted discovery. Even without foil, co-branded stickers carry perceived value in high-traffic venues.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Tamper-evident micro features on standard stock
    - Microtext border, duplex art with a tear-path motif, and a “VOID” back-print pattern. Cheap to print, feels legit, discourages casual reprints without premium materials.[[2]](Econ%20Balance%20(Whales%20vs%20Grinders)%2026d31bb665a2802ea492d6afddb83855.md)

---

### 2) Reduce cost to manufacture unique-per-player stickers

Optimize around digital uniqueness with economical physical production.

- Decouple uniqueness from full-variable print
    - Use a static background + small variable area that encodes the unique ID/QR. Most of the sticker is gang‑run; only a 1–2 cm square changes. Lowers digital print time and waste.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Sequential short codes + shared QR template
    - Print one dynamic QR template domain and inject uniqueness via short alphanumeric in QR payload and microtext. Smaller codes print cleaner, faster, and cheaper than dense per‑sticker URLs.[[2]](Econ%20Balance%20(Whales%20vs%20Grinders)%2026d31bb665a2802ea492d6afddb83855.md)
- Batch personalization via roll labels
    - Print unique rolls per user in batches of 12–24 to amortize RIP overhead. Collate into 6‑packs. This preserves “unique to you” while hitting label press efficiencies.
- Two-tier inventory
    - Tier A: generic “seed” stickers, cheap mass run.
    - Tier B: personal stickers with variable codes, used as rewards or purchases. Most play can start on Tier A to seed the network; personal runs are smaller and justified by engagement.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Minimal SKUs, maximal art variance
    - Keep size, finish, and die line constant. Rotate artwork sets digitally. One die + one laminate keeps COGS stable while offering variety.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Print-partner automation
    - Integrate CSV upload of codes and artwork with batch ID registration. Target digital label presses with inline verification scans to cut spoilage and manual QA time.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Anti-spoof without premium stock
    - Photo-proof at placement, GPS/time clustering checks, per-device caps, and downweights on suspect scans. Trust the software to provide integrity so you don’t pay for holographic film.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)[[2]](Econ%20Balance%20(Whales%20vs%20Grinders)%2026d31bb665a2802ea492d6afddb83855.md)

Manufacturing ladder to test:

1. Phase 1: Generic seed + tiny variable QR area on standard matte vinyl.
2. Phase 2: Add microtext and duplex back-print “VOID” pattern.
3. Phase 3: Optional specialty finish for sponsor or high-tier drops only.

---

### 3) Avoid pay-to-win strategies

Let money buy convenience or cosmetics, not net point advantage.

- Strict “cosmetic or QoL” monetization
    - Purchases unlock designs, frames, and mild non-stacking quality-of-life boosts like streak protection, extra inventory slots, or route hints. No direct point multipliers beyond what is earnable via progression.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Performance comes from placement quality and social spread
    - Keep base points and bonuses gated by unique scans, geo diversity, venue variety, and sneeze chains. Purchases can’t bypass uniqueness, caps, or cooldowns.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Hard caps and diminishing returns
    - Per-sticker daily caps, weekly account caps, and rapidly diminishing returns ensure that buying more stickers does not linearly translate into more points.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Parallel earnable path
    - Any purchasable progression perk must be obtainable through regular play in a comparable timeframe. Wallet top-ups offer convenience for shipping or bundles, not extra scoring power.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Transparency and economy health
    - Publicly document multipliers, caps, and fairness rules in-app. Visible rulesets reduce perceived p2w and help players self-regulate optimal, non-exploitative play.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Ad policy: protection, not power
    - Rewarded ads protect streaks or revive limited boosts. No ads that grant score multipliers beyond what gameplay already enables.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)

---

### Bonus: Anti-spoofing without expensive substrates

Address the open questions with software-first integrity.

- Multi-signal scan trust score
    - Mix device attestation, coarse-to-precise location patterns, time deltas, historic travel speed, and camera capture heuristics. Downweight or null low-trust scans.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Placement proof and “lifecycle”
    - Require initial placement photo and occasional “health check” resnaps. Aged stickers without periodic unique scans decay in value until refreshed.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Social corroboration
    - Independent scanners within a time window increase a sticker’s trust; tight clusters from the same device or spoofy patterns reduce it.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)
- Cheap visual tells
    - Microtext ring with the short code and a small art element that is hard to replicate precisely on casual home printers. Enough friction to deter casual spoofers.[[2]](Econ%20Balance%20(Whales%20vs%20Grinders)%2026d31bb665a2802ea492d6afddb83855.md)

---

### What to pilot next

- Run a two-arm test on one campus:
    - A: generic seed packs only
    - B: 1 generic + 1 mini personalized strip per pack
- Measure: time-to-first unique scan, unique scans per sticker, buyer rate, contribution/pack, and perceived fairness NPS.[[1]](FYNDR%20gg%2026b31bb665a2802182b0c83bea0980c0.md)

If you want, I can draft a short addendum into the Development questions page that captures these recommendations under each question.