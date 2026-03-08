"""
generate_data.py
----------------
WHY THIS FILE EXISTS:
We don't have real company data (that's confidential), so we SIMULATE it.
This is 100% normal in data analytics portfolios.
Recruiters know this — what matters is your ANALYSIS, not the data source.

WHAT WE'RE SIMULATING:
A service desk dataset like what Capgemini handles — Okta, Oracle, browser issues etc.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ✅ Set seed so data is reproducible (same output every time you run it)
np.random.seed(42)
random.seed(42)

# --- CONFIGURATION ---
NUM_TICKETS = 5000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)

# Issue categories — based on real service desk work
CATEGORIES = [
    "Okta Password Reset",
    "Okta Account Lockout",
    "Oracle Access Issue",
    "Oracle Login Failure",
    "Browser Compatibility Issue",
    "VPN Connectivity",
    "Data Sync Failure",
    "Email Configuration",
    "Software Installation",
    "Hardware Issue"
]

# Realistic probability weights (Okta issues are most common in real life)
CATEGORY_WEIGHTS = [0.22, 0.18, 0.12, 0.10, 0.10, 0.08, 0.07, 0.06, 0.04, 0.03]

PRIORITIES = ["Low", "Medium", "High", "Critical"]
PRIORITY_WEIGHTS = [0.30, 0.40, 0.20, 0.10]

AGENTS = ["Agent_A", "Agent_B", "Agent_C", "Agent_D", "Agent_E"]

STATUS = ["Resolved", "Escalated", "Pending"]
STATUS_WEIGHTS = [0.75, 0.15, 0.10]

CHANNELS = ["Phone", "Chat", "Email"]
CHANNEL_WEIGHTS = [0.45, 0.35, 0.20]

REGIONS = ["North", "South", "East", "West"]


def random_datetime(start, end):
    """Generate a random datetime between start and end"""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def resolution_time(priority, status):
    """
    WHY: Different priorities have different SLA targets.
    Critical = must resolve fast. Low = can take time.
    Escalated tickets take longer by nature.
    """
    base_times = {"Low": 120, "Medium": 60, "High": 30, "Critical": 15}
    base = base_times[priority]
    
    if status == "Escalated":
        return round(np.random.normal(base * 2.5, base * 0.5), 1)
    elif status == "Resolved":
        return round(np.random.normal(base, base * 0.3), 1)
    else:  # Pending
        return round(np.random.normal(base * 3, base * 0.8), 1)


def first_contact_resolution(priority, status):
    """FCR = Was the issue resolved in first contact? Key KPI in service desks."""
    if status == "Resolved" and priority in ["Low", "Medium"]:
        return random.choices([True, False], weights=[0.75, 0.25])[0]
    return False


# --- GENERATE DATA ---
print("Generating 5000 service desk tickets...")

data = []
for i in range(1, NUM_TICKETS + 1):
    created_at = random_datetime(START_DATE, END_DATE)
    category = random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0]
    priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
    status = random.choices(STATUS, weights=STATUS_WEIGHTS)[0]
    res_time = resolution_time(priority, status)
    
    data.append({
        "ticket_id": f"TKT-{i:05d}",
        "created_at": created_at,
        "day_of_week": created_at.strftime("%A"),
        "hour_of_day": created_at.hour,
        "month": created_at.strftime("%B"),
        "category": category,
        "priority": priority,
        "status": status,
        "channel": random.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0],
        "assigned_agent": random.choice(AGENTS),
        "region": random.choice(REGIONS),
        "resolution_time_mins": max(5, res_time),  # minimum 5 mins
        "first_contact_resolution": first_contact_resolution(priority, status),
        "customer_satisfaction": random.choices(
            [1, 2, 3, 4, 5],
            weights=[0.05, 0.10, 0.20, 0.35, 0.30]
        )[0] if status == "Resolved" else None
    })

df = pd.DataFrame(data)
df = df.sort_values("created_at").reset_index(drop=True)

# Save to CSV
df.to_csv("data/raw_tickets.csv", index=False)
print(f"✅ Generated {len(df)} tickets and saved to data/raw_tickets.csv")
print(df.head())
print(f"\nShape: {df.shape}")
print(f"Date range: {df['created_at'].min()} to {df['created_at'].max()}")
