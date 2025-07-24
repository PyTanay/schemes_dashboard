# 📊 Scheme Lifecycle Management Dashboard

A modern, information-heavy Streamlit dashboard for visualizing, analyzing, and reporting **scheme file lifecycle data** across departments.
This dashboard helps track scheme processing KPIs, attachment handling time, user/department performance, bottlenecks, and more.

---

## 🚀 Quick Start

### ✅ 1. Clone the Repository

```bash
git clone https://github.com/PyTanay/schemes_dashboard.git
cd schemes_dashboard
```

> Replace `your-username` with your GitHub username.

---

### ✅ 2. Set Up Python Environment

Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
```

**Activate it:**

* **Windows (CMD):**

  ```bash
  .venv\Scripts\activate
  ```
* **Windows (PowerShell):**

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
* **macOS/Linux:**

  ```bash
  source .venv/bin/activate
  ```

---

### ✅ 3. Install Required Packages

```bash
pip install -r requirements.txt
```

---

### ✅ 4. Run the Dashboard

```bash
streamlit run app.py
```

This will open the dashboard at:
**`http://localhost:8501`**

---

## 📁 Project Structure

```
streamlit-dashboard/
│
├── app.py                  # Main Streamlit dashboard logic
├── requirements.txt
├── README.md
│
├── data/                   # Contains input CSV files
│   ├── schemes.csv
│   ├── workflow.csv
│   └── attachments.csv
│
├── components/             # Visuals and charting components
│   └── charts.py
│
├── utils/                  # Backend utilities for data load, processing, calculations
│   ├── data_loader.py
│   ├── calculation.py
│   ├── preprocessing.py
│   └── __init__.py
```

---

## 📊 Dashboard Features

### ✅ Key KPI Cards

* Total schemes handled
* Average processing time per scheme
* Average attachment handling time
* Schemes pending

### 📈 Charts and Visualizations

* ⏱️ **Line Chart**: Avg. processing time per user/department over time
* 📊 **Bar Charts**:

  * Scheme distribution by category, year, plant
  * Average time taken per user or department
* 📉 **Histogram**:

  * Distribution of scheme processing time (with filters and bin selection)
* 🔁 **Sankey Diagram**:

  * Flow of schemes between departments
* 🗖️ **Calendar Heatmap**:

  * Activity by date (scheme inflow/outflow)
* 🔥 **Top Performers**:

  * Fastest and slowest handlers
* 📂 **Aging Buckets**:

  * Schemes grouped by <90 days, 90–180 days, >180 days
* 🗓️ **Annual Reports**:

  * Received, processed, carried over, and pending schemes by user/department

---

## 🧠 How Data Works

* `workflow.csv` → Tracks user handling, department, forwarding time, and time taken
* `schemes.csv` → Metadata of each scheme (plant, year, category, descriptions)
* `attachments.csv` → Tracks files uploaded by users under each scheme

> All files use `scheme_id` as a primary key for joining.

---

## 🛠️ Built With

| Tool                                                        | Purpose                           |
| ----------------------------------------------------------- | --------------------------------- |
| [Python](https://www.python.org/)                           | Core programming language         |
| [Streamlit](https://streamlit.io/)                          | Web-based dashboard interface     |
| [Pandas](https://pandas.pydata.org/)                        | Data wrangling                    |
| [Plotly](https://plotly.com/)                               | Interactive visualizations        |
| [Git](https://git-scm.com/) + [GitHub](https://github.com/) | Version control and collaboration |

---

## 🔐 Git & GitHub Tips

### ✅ Check if Git is Initialized

```bash
git remote -v
```

If blank, set remote:

```bash
git remote add origin https://github.com/your-username/streamlit-dashboard.git
git push -u origin main
```

Use [GitHub Personal Access Tokens](https://github.com/settings/tokens) instead of passwords if prompted.

---

## ✅ Setup Notes for New Users

* Ensure your `/data/` folder contains the three required CSVs:

  * `schemes.csv`
  * `workflow.csv`
  * `attachments.csv`
* These files are **ignored from Git pushes** (via `.gitignore`) for data sensitivity.

---

## 🤝 Contributions (Optional)

Want to contribute enhancements, bug fixes, or new visualizations?

```bash
# Create a new branch
git checkout -b feature-name

# Commit changes
git add .
git commit -m "Describe your change"

# Push and open a PR
git push origin feature-name
```

---

## 📧 Contact

This tool is developed by the **Tanay**.
For internal queries, raise a support ticket or contact the dashboard maintainer.

---

## 📝 License

This project is internal-use only unless otherwise licensed.
