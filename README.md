# 🖥️ IT Service Desk Analytics Dashboard

## 📌 Project Overview
End-to-end data analysis of 5,000+ IT support tickets simulating a real enterprise service desk environment (similar to tools like Okta, Oracle, and enterprise browser/VPN support).

This project analyzes ticket patterns, SLA compliance, agent performance, and peak hours to generate actionable business insights.

---

## 🎯 Business Questions Answered
1. **Which issues are most common?** → Prioritize automation & training
2. **When do tickets peak?** → Optimize agent shift planning
3. **Are we meeting SLA targets?** → Identify SLA breach patterns by priority
4. **Which agents perform best?** → FCR rate, resolution time, breach rate
5. **Monthly trends?** → Forecast staffing needs

---

## 🛠️ Tech Stack
| Tool | Purpose |
|------|---------|
| Python | Core language |
| Pandas | Data manipulation & analysis |
| NumPy | Numerical operations |
| Matplotlib | Charts & visualizations |
| Seaborn | Statistical plots |
| Power BI | Interactive dashboard (see `/powerbi`) |

---

## 📁 Project Structure
```
it-helpdesk-analytics/
│
├── data/
│   └── raw_tickets.csv          # Generated dataset (5000 tickets)
│
├── outputs/
│   ├── charts/                  # All generated charts
│   │   ├── 01_ticket_by_category.png
│   │   ├── 02_peak_hours.png
│   │   ├── 03_resolution_time.png
│   │   ├── 04_agent_performance.png
│   │   └── 05_monthly_trend.png
│   └── summary_report.txt       # Key findings report
│
├── generate_data.py             # Simulates realistic ticket dataset
├── analysis.py                  # Full EDA with explanations
├── requirements.txt             # Dependencies
└── README.md
```

---

## 📊 Key Findings
- **Okta issues** (password resets + lockouts) = ~40% of all tickets → prime candidate for self-service automation
- **Peak hours**: 9AM–11AM and 2PM–4PM, heaviest on **Mondays and Tuesdays**
- **Critical ticket SLA breach rate**: ~22% — needs improvement
- **FCR rate**: Varies significantly by agent — training opportunity identified

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the dataset
python generate_data.py

# 3. Run the full analysis
python analysis.py

# Charts will be saved in outputs/charts/
```

---

## 💡 Business Recommendations
1. **Deploy self-service Okta reset portal** → estimated 30% ticket volume reduction
2. **Schedule max agents on Mon/Tue 9AM–11AM** → reduce wait times at peak
3. **Agent coaching program** for agents with high SLA breach rates
4. **Automate Oracle login failure detection** → proactive alerts before tickets are raised

---

## 👤 Author
**Your Name** | Aspiring Data Analyst  
📧 yourmail@gmail.com | 🔗 [LinkedIn](https://linkedin.com/in/yourprofile)
