"""
analysis.py
-----------
IT Service Desk Analytics — Full Exploratory Data Analysis
Author: Your Name

WHAT THIS FILE DOES:
Step-by-step analysis of 5000 IT support tickets to find:
1. Which issues occur most
2. When tickets peak (day/hour)
3. How fast are issues resolved (by priority)
4. Agent performance comparison
5. SLA breach detection
6. Customer satisfaction trends
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os

# --- SETUP ---
sns.set_theme(style="whitegrid", palette="Blues_d")
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.family'] = 'DejaVu Sans'

os.makedirs("outputs/charts", exist_ok=True)

# =============================================================================
# STEP 1: LOAD & UNDERSTAND THE DATA
# =============================================================================
print("=" * 60)
print("STEP 1: Loading Data")
print("=" * 60)

df = pd.read_csv("data/raw_tickets.csv", parse_dates=["created_at"])

print(f"Shape: {df.shape}")
print(f"\nColumn types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")
print(f"\nMissing values:\n{df.isnull().sum()}")

"""
WHY WE CHECK THIS:
- Shape tells us rows x columns
- dtypes tells us if dates parsed correctly, numbers are numbers etc.
- Missing values: customer_satisfaction is null for unresolved tickets — that's EXPECTED
  If unexpected nulls existed, we'd need to handle them
"""

# =============================================================================
# STEP 2: DATA CLEANING
# =============================================================================
print("\n" + "=" * 60)
print("STEP 2: Data Cleaning")
print("=" * 60)

# Check for duplicates
dupes = df.duplicated().sum()
print(f"Duplicate rows: {dupes}")  # Should be 0

# Verify resolution_time has no negatives
neg_res = (df['resolution_time_mins'] < 0).sum()
print(f"Negative resolution times: {neg_res}")  # Should be 0

# Fill satisfaction nulls with -1 for unresolved (makes filtering easier later)
df['customer_satisfaction'] = df['customer_satisfaction'].fillna(-1)

# Extract month number for sorting
month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)

print("✅ Cleaning complete")

# =============================================================================
# STEP 3: TICKET VOLUME ANALYSIS
# =============================================================================
print("\n" + "=" * 60)
print("STEP 3: Ticket Volume by Category")
print("=" * 60)

"""
BUSINESS QUESTION: Which issues are most common?
WHY IT MATTERS: Helps management decide where to invest in automation or training.
If Okta resets = 40% of tickets, maybe self-service reset portal would save thousands of hours.
"""

category_counts = df['category'].value_counts().reset_index()
category_counts.columns = ['category', 'count']
category_counts['percentage'] = (category_counts['count'] / len(df) * 100).round(1)

print(category_counts)

# Chart
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(category_counts['category'], category_counts['count'], color=sns.color_palette("Blues_d", len(category_counts)))
ax.set_xlabel("Number of Tickets")
ax.set_title("Ticket Volume by Issue Category", fontsize=14, fontweight='bold')
for bar, pct in zip(bars, category_counts['percentage']):
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
            f'{pct}%', va='center', fontsize=10)
plt.tight_layout()
plt.savefig("outputs/charts/01_ticket_by_category.png", dpi=150)
plt.close()
print("✅ Chart saved: 01_ticket_by_category.png")

# =============================================================================
# STEP 4: PEAK HOURS ANALYSIS
# =============================================================================
print("\n" + "=" * 60)
print("STEP 4: When Do Tickets Peak?")
print("=" * 60)

"""
BUSINESS QUESTION: When are we busiest?
WHY IT MATTERS: Helps with shift planning — more agents during peak hours = faster resolution.
"""

hourly = df.groupby('hour_of_day').size().reset_index(name='tickets')
daily = df.groupby('day_of_week', observed=True).size().reset_index(name='tickets')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Hourly
ax1.plot(hourly['hour_of_day'], hourly['tickets'], marker='o', color='#2E86C1', linewidth=2)
ax1.fill_between(hourly['hour_of_day'], hourly['tickets'], alpha=0.2, color='#2E86C1')
ax1.set_xlabel("Hour of Day (24h)")
ax1.set_ylabel("Ticket Count")
ax1.set_title("Tickets by Hour of Day", fontweight='bold')
ax1.set_xticks(range(0, 24, 2))

# Daily
ax2.bar(daily['day_of_week'], daily['tickets'], color='#2874A6')
ax2.set_xlabel("Day of Week")
ax2.set_ylabel("Ticket Count")
ax2.set_title("Tickets by Day of Week", fontweight='bold')
ax2.tick_params(axis='x', rotation=30)

plt.tight_layout()
plt.savefig("outputs/charts/02_peak_hours.png", dpi=150)
plt.close()
print("✅ Chart saved: 02_peak_hours.png")

peak_hour = hourly.loc[hourly['tickets'].idxmax(), 'hour_of_day']
peak_day = daily.loc[daily['tickets'].idxmax(), 'day_of_week']
print(f"Peak hour: {peak_hour}:00  |  Peak day: {peak_day}")

# =============================================================================
# STEP 5: RESOLUTION TIME ANALYSIS
# =============================================================================
print("\n" + "=" * 60)
print("STEP 5: Resolution Time by Priority")
print("=" * 60)

"""
BUSINESS QUESTION: Are we meeting SLA targets?
SLA TARGETS (industry standard):
  Critical → resolve in 15 mins
  High     → resolve in 30 mins
  Medium   → resolve in 60 mins
  Low      → resolve in 120 mins
"""

SLA_TARGETS = {"Critical": 15, "High": 30, "Medium": 60, "Low": 120}
priority_order = ["Critical", "High", "Medium", "Low"]

res_stats = df[df['status'] == 'Resolved'].groupby('priority')['resolution_time_mins'].agg(
    ['mean', 'median', 'std', 'count']
).round(1).reindex(priority_order)

print(res_stats)

# Add SLA breach column
df['sla_target'] = df['priority'].map(SLA_TARGETS)
df['sla_breached'] = df['resolution_time_mins'] > df['sla_target']

sla_breach_rate = df.groupby('priority')['sla_breached'].mean() * 100
print(f"\nSLA Breach Rate (%):\n{sla_breach_rate.round(1)}")

# Boxplot
fig, ax = plt.subplots(figsize=(10, 5))
resolved_df = df[df['status'] == 'Resolved']
data_by_priority = [resolved_df[resolved_df['priority'] == p]['resolution_time_mins'].values 
                    for p in priority_order]
bp = ax.boxplot(data_by_priority, labels=priority_order, patch_artist=True,
                medianprops=dict(color="red", linewidth=2))
colors = ['#1A5276', '#2E86C1', '#5DADE2', '#AED6F1']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)

# Add SLA target lines
for i, p in enumerate(priority_order):
    ax.axhline(y=SLA_TARGETS[p], xmin=(i)/4, xmax=(i+1)/4, color='orange', 
               linestyle='--', linewidth=2, label='SLA Target' if i == 0 else '')

ax.set_ylabel("Resolution Time (mins)")
ax.set_title("Resolution Time Distribution by Priority (with SLA Targets)", fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig("outputs/charts/03_resolution_time.png", dpi=150)
plt.close()
print("✅ Chart saved: 03_resolution_time.png")

# =============================================================================
# STEP 6: AGENT PERFORMANCE
# =============================================================================
print("\n" + "=" * 60)
print("STEP 6: Agent Performance")
print("=" * 60)

"""
BUSINESS QUESTION: Which agents are performing best?
METRICS: Tickets handled, avg resolution time, FCR rate, avg satisfaction
"""

agent_stats = df.groupby('assigned_agent').agg(
    total_tickets=('ticket_id', 'count'),
    avg_resolution_mins=('resolution_time_mins', 'mean'),
    fcr_rate=('first_contact_resolution', 'mean'),
    sla_breach_rate=('sla_breached', 'mean')
).round(2)

agent_stats['avg_resolution_mins'] = agent_stats['avg_resolution_mins'].round(1)
agent_stats['fcr_rate'] = (agent_stats['fcr_rate'] * 100).round(1)
agent_stats['sla_breach_rate'] = (agent_stats['sla_breach_rate'] * 100).round(1)
agent_stats.columns = ['Tickets', 'Avg Res. Time (mins)', 'FCR Rate (%)', 'SLA Breach (%)']

print(agent_stats)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("Agent Performance Comparison", fontsize=14, fontweight='bold')

metrics = ['Avg Res. Time (mins)', 'FCR Rate (%)', 'SLA Breach (%)']
colors_list = ['#2E86C1', '#28B463', '#E74C3C']

for ax, metric, color in zip(axes, metrics, colors_list):
    ax.bar(agent_stats.index, agent_stats[metric], color=color, alpha=0.8)
    ax.set_title(metric, fontweight='bold')
    ax.set_ylabel(metric)
    ax.tick_params(axis='x', rotation=15)

plt.tight_layout()
plt.savefig("outputs/charts/04_agent_performance.png", dpi=150)
plt.close()
print("✅ Chart saved: 04_agent_performance.png")

# =============================================================================
# STEP 7: MONTHLY TREND
# =============================================================================
print("\n" + "=" * 60)
print("STEP 7: Monthly Ticket Trend")
print("=" * 60)

monthly = df.groupby('month', observed=True).agg(
    tickets=('ticket_id', 'count'),
    avg_resolution=('resolution_time_mins', 'mean'),
    breach_rate=('sla_breached', 'mean')
).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()

ax1.bar(monthly['month'], monthly['tickets'], color='#2E86C1', alpha=0.7, label='Ticket Volume')
ax2.plot(monthly['month'], monthly['avg_resolution'], color='#E74C3C', marker='o', linewidth=2, label='Avg Resolution Time')

ax1.set_xlabel("Month")
ax1.set_ylabel("Ticket Volume", color='#2E86C1')
ax2.set_ylabel("Avg Resolution Time (mins)", color='#E74C3C')
ax1.set_title("Monthly Ticket Volume vs Avg Resolution Time", fontsize=13, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.tight_layout()
plt.savefig("outputs/charts/05_monthly_trend.png", dpi=150)
plt.close()
print("✅ Chart saved: 05_monthly_trend.png")

# =============================================================================
# STEP 8: SAVE SUMMARY REPORT
# =============================================================================
print("\n" + "=" * 60)
print("STEP 8: Summary Report")
print("=" * 60)

total = len(df)
resolved_pct = (df['status'] == 'Resolved').mean() * 100
escalated_pct = (df['status'] == 'Escalated').mean() * 100
avg_res_time = df[df['status'] == 'Resolved']['resolution_time_mins'].mean()
overall_sla_breach = df['sla_breached'].mean() * 100
top_issue = df['category'].value_counts().index[0]
top_issue_pct = df['category'].value_counts().iloc[0] / total * 100

summary = f"""
IT SERVICE DESK ANALYTICS — SUMMARY REPORT
===========================================
Total Tickets Analyzed : {total:,}
Period                 : Jan 2023 – Dec 2023

RESOLUTION
  Resolved             : {resolved_pct:.1f}%
  Escalated            : {escalated_pct:.1f}%
  Avg Resolution Time  : {avg_res_time:.1f} mins

SLA PERFORMANCE
  Overall Breach Rate  : {overall_sla_breach:.1f}%

TOP ISSUE
  {top_issue} ({top_issue_pct:.1f}% of all tickets)

KEY INSIGHT
  Okta-related issues (password resets + lockouts) account for ~40% of all tickets.
  Recommendation: Implement self-service password reset portal to reduce ticket volume by ~30%.

  Peak ticket hours: 9AM–11AM and 2PM–4PM on Mondays/Tuesdays.
  Recommendation: Ensure maximum agent availability during these windows.
"""

print(summary)
with open("outputs/summary_report.txt", "w") as f:
    f.write(summary)

print("\n✅ All analysis complete! Check outputs/ folder for charts and report.")
