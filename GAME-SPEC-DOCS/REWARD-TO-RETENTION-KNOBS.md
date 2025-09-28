# 🎛️ Reward-to-Retention Control Knobs

*Complete guide to the reward systems that directly impact churn and retention in FYNDR*

## 🔗 **How Churn is Currently Linked to Rewards**

### **Direct Churn Reduction Mechanisms**
Your system has **4 primary reward-based churn reduction mechanisms**:

1. **Streak Bonuses** → **70% churn reduction** (14+ day streaks)
2. **Purchase Investment** → **30% churn reduction** (any spending)
3. **Level Progression** → **40% churn reduction** (level 10+)
4. **Activity Engagement** → **Up to 4x churn increase** (inactivity penalties)

---

## 🎯 **Retention Control Knobs**

### **1. Streak System (MOST POWERFUL)**
**Current Impact**: 70% churn reduction for 14+ day streaks

**Knobs to Turn:**
```python
# Scan Streak Bonuses
scan_streak_bonus_days: int = 7          # Days needed for bonus
scan_streak_bonus_multiplier: float = 2.0  # Point multiplier

# Placement Streak Bonuses  
placement_streak_bonus_days: int = 14     # Days needed for bonus
placement_streak_bonus_multiplier: float = 2  # Point multiplier

# Activity Streak Bonuses
activity_streak_bonus_days: int = 21      # Days needed for bonus
activity_streak_bonus_multiplier: float = 2.0  # Point multiplier
```

**Retention Impact:**
- **Reduce days needed**: 7→5 days = More players get streak bonuses
- **Increase multipliers**: 2.0→3.0 = Higher rewards = stronger retention
- **Add intermediate tiers**: 3-day, 7-day, 14-day, 21-day bonuses

### **2. Comeback Bonus System**
**Current Impact**: 2x point multiplier for returning players

**Knobs to Turn:**
```python
comeback_bonus_days: int = 3              # Days away to trigger
comeback_bonus_multiplier: float = 2.0    # Point multiplier
```

**Retention Impact:**
- **Reduce trigger days**: 3→2 days = Earlier comeback rewards
- **Increase multiplier**: 2.0→3.0 = More attractive comeback
- **Add comeback points**: Direct point bonuses for returning

### **3. New Player Onboarding**
**Current Impact**: 3x point multiplier for first 7 days

**Knobs to Turn:**
```python
new_player_bonus_days: int = 7            # Days of bonus
new_player_bonus_multiplier: float = 3.0  # Point multiplier
new_player_free_packs: int = 0            # Free sticker packs
```

**Retention Impact:**
- **Extend bonus period**: 7→14 days = Longer onboarding
- **Increase multiplier**: 3.0→4.0 = More generous new player experience
- **Add free packs**: 0→2 free packs = Immediate value

### **4. Level Progression System**
**Current Impact**: 40% churn reduction for level 10+ players

**Knobs to Turn:**
```python
# Level-based churn reduction
level_5_churn_reduction: float = 0.8     # 20% reduction
level_10_churn_reduction: float = 0.6    # 40% reduction

# XP requirements
points_per_level: int = 100              # Points needed per level
max_level: int = 20                       # Maximum level
```

**Retention Impact:**
- **Reduce XP requirements**: 100→75 points = Faster leveling
- **Add more level tiers**: 20→30 levels = Longer progression
- **Increase level bonuses**: Better rewards at each level

---

## 🚀 **Virality Control Knobs**

### **1. Referral Reward System**
**Current Impact**: 2x point multiplier for 14 days after successful referral

**Knobs to Turn:**
```python
referral_reward_multiplier: float = 2.0   # Point multiplier
referral_reward_days: int = 14            # Days of bonus
```

**Virality Impact:**
- **Increase multiplier**: 2.0→3.0 = More attractive to refer
- **Extend bonus period**: 14→21 days = Longer reward period
- **Add referral points**: Direct point bonuses for successful referrals

### **2. Social Mechanics**
**Current Impact**: Social sneeze bonuses for viral spread

**Knobs to Turn:**
```python
social_sneeze_threshold: int = 3          # Scans needed for sneeze
social_sneeze_bonus: float = 3.0         # Bonus multiplier
social_sneeze_cap: int = 1               # Max sneezes per day
```

**Virality Impact:**
- **Reduce threshold**: 3→2 scans = Easier to trigger viral
- **Increase bonus**: 3.0→4.0 = More rewarding viral spread
- **Remove cap**: 1→unlimited = More viral potential

### **3. Event System**
**Current Impact**: 1.5x point multiplier during events

**Knobs to Turn:**
```python
event_frequency_days: int = 21           # Days between events
event_duration_days: int = 7              # Event duration
event_bonus_multiplier: float = 1.5       # Point multiplier
```

**Virality Impact:**
- **Increase frequency**: 21→14 days = More events
- **Extend duration**: 7→10 days = Longer events
- **Increase multiplier**: 1.5→2.0 = More exciting events

---

## 📊 **Retention Optimization Strategies**

### **High Impact, Low Effort**
1. **Reduce streak requirements**: 7→5 days for scan streaks
2. **Increase comeback multiplier**: 2.0→3.0
3. **Add free packs for new players**: 0→2 packs
4. **Extend new player bonus**: 7→14 days

### **Medium Impact, Medium Effort**
1. **Add intermediate streak tiers**: 3-day, 7-day, 14-day bonuses
2. **Increase level progression speed**: Reduce XP requirements
3. **Add referral point bonuses**: Direct points for successful referrals
4. **Implement daily login bonuses**: Consistent daily rewards

### **High Impact, High Effort**
1. **Add prestige system**: Reset progression with permanent benefits
2. **Implement guild/clan system**: Social retention mechanics
3. **Add seasonal progression**: Long-term goals and rewards
4. **Create achievement system**: Milestone-based rewards

---

## 🎮 **Player Type-Specific Knobs**

### **Whale Retention**
- **Increase purchase bonuses**: Higher multipliers for spending
- **Add VIP tiers**: Exclusive rewards for high spenders
- **Implement loyalty programs**: Cumulative spending rewards

### **Grinder Retention**
- **Optimize scan rewards**: Higher base points for scanning
- **Add scanning achievements**: Milestone rewards for scan counts
- **Implement leaderboards**: Competitive elements

### **Casual Retention**
- **Reduce engagement requirements**: Lower thresholds for bonuses
- **Add passive rewards**: Points for owned stickers
- **Implement social features**: Friend systems and sharing

---

## 🔧 **Implementation Priority**

### **Immediate (Week 1)**
1. **Reduce scan streak days**: 7→5 days
2. **Increase comeback multiplier**: 2.0→3.0
3. **Add new player free packs**: 0→2 packs

### **Short-term (Month 1)**
1. **Extend new player bonus**: 7→14 days
2. **Add intermediate streak tiers**: 3-day, 7-day bonuses
3. **Increase referral multiplier**: 2.0→3.0

### **Medium-term (Quarter 1)**
1. **Implement daily login bonuses**
2. **Add achievement system**
3. **Create player type-specific rewards**

### **Long-term (Year 1)**
1. **Add prestige system**
2. **Implement guild/clan mechanics**
3. **Create seasonal progression**

---

## 📈 **Expected Impact**

### **Retention Improvements**
- **Streak optimization**: +15-25% retention
- **Comeback bonuses**: +10-20% retention
- **New player onboarding**: +20-30% Day 1 retention
- **Level progression**: +10-15% long-term retention

### **Virality Improvements**
- **Referral optimization**: +50-100% referral rate
- **Social mechanics**: +25-50% viral coefficient
- **Event system**: +30-60% engagement during events

---

## 🎯 **Quick Wins (Implement First)**

1. **Scan streak days**: 7→5 days
2. **Comeback multiplier**: 2.0→3.0
3. **New player free packs**: 0→2 packs
4. **Referral multiplier**: 2.0→3.0

**Expected Result**: +20-30% overall retention improvement

*Last Updated: September 27, 2024*
*Next Review: After implementing quick wins*
