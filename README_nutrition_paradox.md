
# 🥗 Nutrition Paradox: A Global View on Obesity and Malnutrition

This project explores the global paradox of coexisting **obesity** and **malnutrition** using WHO public datasets. It includes data collection, processing, storage in SQLite, and an interactive dashboard built with **Streamlit** for visualization and analysis.

---

## 🚀 Features

- 📊 Interactive dashboard comparing global obesity and malnutrition trends
- 🌍 Country- and region-wise analysis (India, Africa, etc.)
- 🔍 Filtered SQL queries for focused insights
- 📈 Exploratory Data Analysis with charts (histograms, heatmaps, trends, etc.)
- 🗃️ SQLite database backend for efficient querying

---

## 🏗️ Project Structure

```bash
nutrition_paradox/
│
├── nutrition_app.py        # Main application script with Streamlit UI
├── nutrition_paradox.db    # SQLite database (auto-generated)
├── requirements.txt        # Required Python packages (optional)
└── README.md               # Project documentation (this file)
```

---

## 🔧 Technologies Used

- **Python 3.10+**
- **Pandas** for data manipulation
- **Requests** for API access
- **SQLite3** for local storage
- **Seaborn** & **Matplotlib** for plots
- **Streamlit** for UI and interactivity

---

## 🌐 Data Sources

Data is fetched from the [World Health Organization (WHO) API](https://ghoapi.azureedge.net/api):

- Adult Obesity: `NCD_BMI_30C`
- Child Obesity: `NCD_BMI_PLUS2C`
- Adult Underweight: `NCD_BMI_18C`
- Child Thinness: `NCD_BMI_MINUS2C`

---

## 📥 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/nutrition-paradox.git
   cd nutrition-paradox
   ```

2. **Install required libraries**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   streamlit run nutrition_app.py
   ```

---

## 🧠 Insights You Can Explore

Select from a list of curated queries like:

- Top 5 regions/countries with highest obesity or malnutrition
- Gender or age-wise distribution
- Country-level trends (India, Nigeria, Brazil)
- Confidence interval analysis (CI Width)
- Global year-over-year obesity vs. malnutrition trends

---

## 📊 Visualizations Included

- 📈 Line Charts for trends
- 📦 Boxplots and Histograms
- 🌍 Heatmaps across regions and years
- 🥧 Pie charts for distribution
- 📉 Dual-line comparison of malnutrition vs obesity globally

---

## 📌 Note

- All data is cached using `@st.cache_data` to improve performance
- The SQLite DB `nutrition_paradox.db` will be created automatically
- Country codes follow WHO standard ISO Alpha-3

---

## 🙌 Acknowledgements

- World Health Organization (WHO) Open Data Platform
- Streamlit for interactive app development
- Seaborn & Matplotlib for robust visualization
