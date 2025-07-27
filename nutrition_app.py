# Nutrition Paradox Project with SQLite, EDA, and Streamlit

# --- Step 1: Import Libraries ---
import pandas as pd
import requests
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO
import base64

# --- Step 2: Define API Endpoints ---
api_urls = {
    "adult_obesity": "https://ghoapi.azureedge.net/api/NCD_BMI_30C",
    "child_obesity": "https://ghoapi.azureedge.net/api/NCD_BMI_PLUS2C",
    "adult_underweight": "https://ghoapi.azureedge.net/api/NCD_BMI_18C",
    "child_thinness": "https://ghoapi.azureedge.net/api/NCD_BMI_MINUS2C"
}

# --- Step 3: Download and Process Data ---
@st.cache_data

def fetch_data(api_url):
    response = requests.get(api_url)
    data = response.json()
    return pd.DataFrame(data["value"])

# Fetch all 4 datasets
df_adult_obesity = fetch_data(api_urls["adult_obesity"])
df_child_obesity = fetch_data(api_urls["child_obesity"])
df_adult_underweight = fetch_data(api_urls["adult_underweight"])
df_child_thinness = fetch_data(api_urls["child_thinness"])

# --- Step 4: Preprocessing Function ---
def preprocess(df, age_group):
    df = df[["ParentLocation", "Dim1", "TimeDim", "Low", "High", "NumericValue", "SpatialDim"]].copy()
    df["Age_Group"] = age_group
    df.rename(columns={
        "ParentLocation": "Region",
        "Dim1": "Gender",
        "TimeDim": "Year",
        "Low": "LowerBound",
        "High": "UpperBound",
        "NumericValue": "Mean_Estimate",
        "SpatialDim": "Country"
    }, inplace=True)
    df["CI_Width"] = df["UpperBound"] - df["LowerBound"]
    return df

# Apply preprocessing
df_obesity = pd.concat([
    preprocess(df_adult_obesity, "Adult"),
    preprocess(df_child_obesity, "Child/Adolescent")
])

df_malnutrition = pd.concat([
    preprocess(df_adult_underweight, "Adult"),
    preprocess(df_child_thinness, "Child/Adolescent")
])

# --- Step 5: Save to SQLite ---
conn = sqlite3.connect("nutrition_paradox.db")

# Save tables
df_obesity.to_sql("obesity", conn, if_exists="replace", index=False)
df_malnutrition.to_sql("malnutrition", conn, if_exists="replace", index=False)

# --- Step 6: Streamlit UI ---
st.title("📊 Nutrition Paradox: Obesity and Malnutrition Dashboard")

# Sidebar filters
selected_table = st.sidebar.selectbox("Choose Dataset", ["obesity", "malnutrition"])
query_options = {
    "obesity": [
        "Top 5 regions with highest avg obesity (2022)",
        "Top 5 countries with highest obesity",
        "Obesity trend in India",
        "Average obesity by gender",
        "Country count by obesity level and age group",
        "Top/Bottom 5 countries by CI_Width",
        "Average obesity by age group",
        "Top 10 countries with consistent low obesity",
        "Female obesity exceeds male",
        "Global avg obesity % per year"
    ],
    "malnutrition": [
        "Avg malnutrition by age group",
        "Top 5 countries with highest malnutrition",
        "Trend in African region",
        "Avg malnutrition by gender",
        "CI width by level and age",
        "India/Nigeria/Brazil trend",
        "Regions with lowest malnutrition",
        "Countries with increasing malnutrition",
        "Min/Max levels year-wise",
        "High CI_Width flags"
    ]
}

selected_query = st.sidebar.selectbox("Choose Query", query_options[selected_table])

# SQL Queries
query_dict = {
    "Top 5 regions with highest avg obesity (2022)":
        "SELECT Region, AVG(Mean_Estimate) as Avg_Obesity FROM obesity WHERE Year = 2022 GROUP BY Region ORDER BY Avg_Obesity DESC LIMIT 5",

    "Top 5 countries with highest obesity":
        "SELECT Country, AVG(Mean_Estimate) as Avg_Obesity FROM obesity GROUP BY Country ORDER BY Avg_Obesity DESC LIMIT 5",

    "Obesity trend in India":
        "SELECT Year, AVG(Mean_Estimate) as Avg_Obesity FROM obesity WHERE Country = 'IND' GROUP BY Year",

    "Average obesity by gender":
        "SELECT Gender, AVG(Mean_Estimate) as Avg_Obesity FROM obesity GROUP BY Gender",

    "Country count by obesity level and age group":
        "SELECT Age_Group, COUNT(DISTINCT Country) as Country_Count FROM obesity WHERE Mean_Estimate >= 30 GROUP BY Age_Group",

    "Top/Bottom 5 countries by CI_Width":
        "SELECT Country, AVG(CI_Width) as Avg_CI FROM obesity GROUP BY Country ORDER BY Avg_CI DESC LIMIT 5",

    "Average obesity by age group":
        "SELECT Age_Group, AVG(Mean_Estimate) as Avg_Obesity FROM obesity GROUP BY Age_Group",

    "Top 10 countries with consistent low obesity":
        "SELECT Country, AVG(Mean_Estimate) as LowAvg, AVG(CI_Width) as LowCI FROM obesity GROUP BY Country HAVING LowAvg < 25 AND LowCI < 2 ORDER BY LowAvg ASC LIMIT 10",

    "Female obesity exceeds male":
        "SELECT o1.Country, o1.Year FROM obesity o1 JOIN obesity o2 ON o1.Country = o2.Country AND o1.Year = o2.Year WHERE o1.Gender = 'Female' AND o2.Gender = 'Male' AND o1.Mean_Estimate - o2.Mean_Estimate > 5",

    "Global avg obesity % per year":
        "SELECT Year, AVG(Mean_Estimate) as Global_Obesity FROM obesity GROUP BY Year ORDER BY Year",

    "Avg malnutrition by age group":
        "SELECT Age_Group, AVG(Mean_Estimate) as Avg_Malnutrition FROM malnutrition GROUP BY Age_Group",

    "Top 5 countries with highest malnutrition":
        "SELECT Country, AVG(Mean_Estimate) as Avg_Malnutrition FROM malnutrition GROUP BY Country ORDER BY Avg_Malnutrition DESC LIMIT 5",

    "Trend in African region":
        "SELECT Year, AVG(Mean_Estimate) as Africa_Malnutrition FROM malnutrition WHERE Region = 'Africa' GROUP BY Year",

    "Avg malnutrition by gender":
        "SELECT Gender, AVG(Mean_Estimate) as Avg_Malnutrition FROM malnutrition GROUP BY Gender",

    "CI width by level and age":
        "SELECT Age_Group, AVG(CI_Width) as AvgCI FROM malnutrition GROUP BY Age_Group",

    "India/Nigeria/Brazil trend":
        "SELECT Country, Year, AVG(Mean_Estimate) as AvgMal FROM malnutrition WHERE Country IN ('IND','NGA','BRA') GROUP BY Country, Year",

    "Regions with lowest malnutrition":
        "SELECT Region, AVG(Mean_Estimate) as Avg_Mal FROM malnutrition GROUP BY Region ORDER BY Avg_Mal ASC LIMIT 5",

    "Countries with increasing malnutrition":
        "SELECT Country, MAX(Mean_Estimate)-MIN(Mean_Estimate) as Diff FROM malnutrition GROUP BY Country HAVING Diff > 0 ORDER BY Diff DESC LIMIT 5",

    "Min/Max levels year-wise":
        "SELECT Year, MIN(Mean_Estimate) as Min_Mal, MAX(Mean_Estimate) as Max_Mal FROM malnutrition GROUP BY Year",

    "High CI_Width flags":
        "SELECT * FROM malnutrition WHERE CI_Width > 5 LIMIT 10"
}

# Run and display query
if selected_query in query_dict:
    query = query_dict[selected_query]
    df_result = pd.read_sql_query(query, conn)
    st.subheader(selected_query)
    st.dataframe(df_result)

    # Basic visualization if numeric
    if "Year" in df_result.columns and df_result.shape[1] == 2:
        st.line_chart(df_result.set_index("Year"))
    elif "Avg_Obesity" in df_result.columns or "Avg_Malnutrition" in df_result.columns:
        st.bar_chart(df_result.set_index(df_result.columns[0]))

# --- EDA Section ---
st.markdown("---")
st.header("📈 Exploratory Data Analysis")
eda_data = df_obesity if selected_table == "obesity" else df_malnutrition

# 1. Distribution of Mean_Estimate
st.subheader("1. Distribution of Mean Estimate")
fig1, ax1 = plt.subplots()
sns.histplot(eda_data["Mean_Estimate"], bins=30, kde=True, ax=ax1)
st.pyplot(fig1)

# 2. Boxplot of CI_Width by Region
st.subheader("2. CI_Width by Region")
fig2, ax2 = plt.subplots()
eda_clean = eda_data.dropna(subset=["Region", "CI_Width"]).copy()
sns.boxplot(data=eda_clean, x="Region", y="CI_Width", ax=ax2)
ax2.tick_params(axis='x', rotation=90)
st.pyplot(fig2)

# 3. Line plot: Trend over years
st.subheader("3. Global Mean Estimate Over Time")
trend_df = eda_data.groupby("Year")["Mean_Estimate"].mean().reset_index()
fig3, ax3 = plt.subplots()
sns.lineplot(data=trend_df, x="Year", y="Mean_Estimate", marker='o', ax=ax3)
st.pyplot(fig3)

# 4. Bar chart: Top 10 countries by Mean_Estimate
st.subheader("4. Top 10 Countries by Average Mean Estimate")
top_countries = eda_data.groupby("Country")["Mean_Estimate"].mean().sort_values(ascending=False).head(10).reset_index()
fig4, ax4 = plt.subplots()
sns.barplot(data=top_countries, x="Mean_Estimate", y="Country", ax=ax4)
st.pyplot(fig4)

# 5. Pie chart: Count by Age Group
st.subheader("5. Distribution by Age Group")
age_counts = eda_data["Age_Group"].value_counts()
st.pyplot(age_counts.plot.pie(autopct='%1.1f%%', figsize=(5, 5)).get_figure())

# 6. Scatter plot: Mean_Estimate vs CI_Width
st.subheader("6. Mean Estimate vs CI Width")
fig6, ax6 = plt.subplots()
sns.scatterplot(data=eda_data, x="Mean_Estimate", y="CI_Width", hue="Gender", ax=ax6)
st.pyplot(fig6)

# 7. Heatmap: Mean Estimate by Region and Year
st.subheader("7. Heatmap of Region-Year Mean Estimate")
heat_df = eda_data.groupby(["Region", "Year"])["Mean_Estimate"].mean().unstack()
fig7, ax7 = plt.subplots(figsize=(10, 5))
sns.heatmap(heat_df, cmap="YlGnBu", annot=True, fmt=".1f", ax=ax7)
st.pyplot(fig7)

# 8. Dual-line: Obesity vs Malnutrition trend comparison (Global)
if selected_table == "obesity":
    st.subheader("8. Compare with Malnutrition (Global Trend)")
    df_compare1 = df_obesity.groupby("Year")["Mean_Estimate"].mean().reset_index().rename(columns={"Mean_Estimate": "Obesity"})
    df_compare2 = df_malnutrition.groupby("Year")["Mean_Estimate"].mean().reset_index().rename(columns={"Mean_Estimate": "Malnutrition"})
    df_merged = pd.merge(df_compare1, df_compare2, on="Year")
    fig8, ax8 = plt.subplots()
    sns.lineplot(data=df_merged, x="Year", y="Obesity", label="Obesity", marker='o', ax=ax8)
    sns.lineplot(data=df_merged, x="Year", y="Malnutrition", label="Malnutrition", marker='o', ax=ax8)
    ax8.set_ylabel("Mean Estimate")
    st.pyplot(fig8)

# --- Close DB ---
conn.close()