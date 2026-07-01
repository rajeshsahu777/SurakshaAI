# MODULE 5: STREAMLIT DASHBOARD
# Karnataka Crime Intelligence & Analytical Platform
# Run from Anaconda Prompt: streamlit run streamlit_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os, json, warnings
warnings.filterwarnings('ignore')

# ============================================================
# AUTO-DETECT OUTPUT FOLDER
# Looks in script's own folder and common locations
# ============================================================
def find_output_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        script_dir,
        os.path.join(script_dir, 'output'),
        os.path.join(script_dir, 'outputs'),
        os.path.join(script_dir, 'cleaned'),
        r"C:\Users\Rajesh\Datathone",
        r"C:\Users\Rajesh\Datathone\datasets\rajanand\crime-in-india\versions\4\cleaned",
        ".",
    ]
    for path in candidates:
        if os.path.exists(os.path.join(path, 'karnataka_clean.csv')):
            return path
    return script_dir   # fallback — will show friendly error

OUTPUT_PATH = find_output_path()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="KSP Crime Intelligence Platform",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .main-header {
        background: linear-gradient(135deg, #1a1f2e, #2d1b69);
        padding: 20px; border-radius: 12px; margin-bottom: 20px;
        border: 1px solid #30363d;
    }
    .metric-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 10px; padding: 16px; text-align: center;
    }
    .metric-value { font-size: 2em; font-weight: bold; color: #58a6ff; }
    .metric-label { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
    .alert-critical {
        background: #3d1515; border-left: 4px solid #f85149;
        padding: 12px; border-radius: 6px; margin: 8px 0;
    }
    .alert-high {
        background: #2d1f00; border-left: 4px solid #e3b341;
        padding: 12px; border-radius: 6px; margin: 8px 0;
    }
    .section-title {
        font-size: 1.2em; font-weight: bold; color: #58a6ff;
        border-bottom: 1px solid #30363d; padding-bottom: 8px; margin-bottom: 16px;
    }
    div[data-testid="stSidebar"] { background-color: #161b22; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_all_data(base_path):
    data = {}

    main_path = os.path.join(base_path, 'karnataka_clean.csv')
    if not os.path.exists(main_path):
        return None, main_path   # Return path so we can show it in error

    data['main'] = pd.read_csv(main_path)

    for key, fname in [
        ('hotspot',  'hotspot_clusters.csv'),
        ('risk',     'risk_predictions.csv'),
        ('forecast', 'crime_forecast.csv'),
        ('anomaly',  'anomaly_flagged.csv'),
    ]:
        fpath = os.path.join(base_path, fname)
        if os.path.exists(fpath):
            data[key] = pd.read_csv(fpath)

    return data, main_path

data, found_path = load_all_data(OUTPUT_PATH)

# ============================================================
# FRIENDLY ERROR if CSV not found
# ============================================================
if data is None:
    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color:#f85149;">❌ Dataset Not Found</h1>
    </div>
    """, unsafe_allow_html=True)

    st.error(f"Could not find `karnataka_clean.csv`")
    st.markdown("**Searched in:**")
    st.code(found_path)

    st.markdown("""
**How to fix — choose one option:**

**Option A** — Put `streamlit_dashboard.py` in the SAME folder as your CSV files, then run:
```
streamlit run streamlit_dashboard.py
```

**Option B** — Edit line 30 of this file to point to your CSV folder:
```python
OUTPUT_PATH = r"C:\\Users\\soham\\your\\actual\\path\\here"
```

**Option C** — Run from the correct folder in Anaconda Prompt:
```
cd C:\\Users\\soham\\path\\where\\csvs\\are
streamlit run C:\\Users\\soham\\path\\to\\streamlit_dashboard.py
```

**Your CSV files needed:**
- `karnataka_clean.csv`  ← from preprocess_crime.py
- `risk_predictions.csv` ← from risk_classifier.py
- `crime_forecast.csv`   ← from time_series_forecast.py
- `anomaly_flagged.csv`  ← from anomaly_detection.py
    """)
    st.stop()

# ============================================================
# SETUP
# ============================================================
df = data['main']

SKIP_COLS = ['YEAR', 'STATE_ENCODED', 'DISTRICT_ENCODED', 'LAT', 'LON',
             'TOTAL_CRIMES', 'RISK_LABEL']
crime_cols = [c for c in df.select_dtypes(include='number').columns if c not in SKIP_COLS]

state_col    = 'STATE_UT'   if 'STATE_UT'   in df.columns else df.columns[0]
district_col = 'DISTRICT'   if 'DISTRICT'   in df.columns else df.columns[1]
year_col     = 'YEAR'       if 'YEAR'       in df.columns else df.columns[2]

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 🚨 KSP Intelligence Platform")
st.sidebar.markdown(f"<small style='color:#3fb950'>✅ Data loaded from:<br>{OUTPUT_PATH}</small>", unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "📊 Overview Dashboard",
    "🗺️ Hotspot Map",
    "⚠️ Risk Predictor",
    "📈 Crime Forecast",
    "🔴 Anomaly Alerts",
    "🔗 Network Analysis",
    "📋 Raw Data Explorer"
])

st.sidebar.markdown("---")

all_years = sorted(df[year_col].unique())
selected_years = st.sidebar.select_slider(
    "Year Range", options=all_years,
    value=(all_years[0], all_years[-1])
)

# Remove TOTAL / ZZ TOTAL / RAILWAYS junk rows from district list
junk_kw = ["TOTAL", "ZZ", "RAILWAY", "STATE"]
all_districts = [
    d for d in sorted(df[district_col].dropna().unique())
    if not any(kw in str(d).upper() for kw in junk_kw)
]
selected_district = st.sidebar.selectbox("Focus District", ["All Districts"] + list(all_districts))

# df_all = year-filtered, junk-removed — used for Overview charts (always all districts)
df_all = df[(df[year_col] >= selected_years[0]) & (df[year_col] <= selected_years[1])]
df_all = df_all[~df_all[district_col].str.upper().str.contains("|".join(junk_kw), na=False)]

# df_filtered = year + optional district filter — used for detail pages
df_filtered = df_all.copy()
if selected_district != "All Districts":
    df_filtered = df_all[df_all[district_col] == selected_district]

# ============================================================
# HELPER — dark chart style
# ============================================================
def dark_fig(w=7, h=3.5):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('#161b22')
    ax.set_facecolor('#161b22')
    for spine in ax.spines.values():
        spine.set_color('#30363d')
    ax.tick_params(colors='#8b949e')
    ax.grid(True, alpha=0.2, color='#30363d')
    return fig, ax

# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================
if page == "📊 Overview Dashboard":

    st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; color:#58a6ff;">🚨 Karnataka Crime Intelligence Platform</h1>
        <p style="margin:4px 0 0 0; color:#8b949e;">State Crime Records Bureau — Strategic Intelligence Hub</p>
    </div>
    """, unsafe_allow_html=True)

    # Overview always shows ALL districts (df_all), not single district
    total_crimes  = int(df_all['TOTAL_CRIMES'].sum()) if 'TOTAL_CRIMES' in df_all.columns else 0
    high_risk_cnt = int((df_all['RISK_LABEL'] == 2).sum()) if 'RISK_LABEL' in df_all.columns else 0
    district_cnt  = df_all[district_col].nunique()
    years_span    = selected_years[1] - selected_years[0] + 1

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, color in [
        (c1, f"{total_crimes:,}",  "Total Crimes Recorded",      "#58a6ff"),
        (c2, str(high_risk_cnt),   "High Risk District-Years",   "#f85149"),
        (c3, str(district_cnt),    "Districts Analyzed",         "#3fb950"),
        (c4, str(years_span),      "Years of Data",              "#e3b341"),
    ]:
        col.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    # Crime trend
    with col_l:
        st.markdown('<div class="section-title">📅 Crime Trend Over Years</div>', unsafe_allow_html=True)
        if 'TOTAL_CRIMES' in df_all.columns:
            yearly = df_all.groupby(year_col)['TOTAL_CRIMES'].sum()
            fig, ax = dark_fig(7, 3.5)
            ax.plot(yearly.index, yearly.values, color='#58a6ff', linewidth=2.5, marker='o', markersize=5)
            ax.fill_between(yearly.index, yearly.values, alpha=0.15, color='#58a6ff')
            ax.set_xlabel('Year', color='#8b949e')
            ax.set_ylabel('Total Crimes', color='#8b949e')
            st.pyplot(fig, use_container_width=True)
            plt.close()

    # Top districts
    with col_r:
        st.markdown('<div class="section-title">🏆 Top 10 Districts by Crime</div>', unsafe_allow_html=True)
        if 'TOTAL_CRIMES' in df_all.columns:
            top_d = df_all.groupby(district_col)['TOTAL_CRIMES'].sum().nlargest(10)
            fig, ax = dark_fig(7, 3.5)
            clrs = ['#f85149' if i < 3 else '#e3b341' if i < 6 else '#58a6ff' for i in range(len(top_d))]
            ax.barh(top_d.index[::-1], top_d.values[::-1], color=clrs[::-1])
            ax.set_xlabel('Total Crimes', color='#8b949e')
            ax.tick_params(labelsize=8)
            st.pyplot(fig, use_container_width=True)
            plt.close()

    col_l2, col_r2 = st.columns(2)

    # Risk pie
    with col_l2:
        st.markdown('<div class="section-title">🔴 Risk Distribution</div>', unsafe_allow_html=True)
        # Risk pie — always use main data RISK_LABEL (integer 0/1/2)
        # risk_predictions may have float prob columns — avoid them
        if 'RISK_LABEL' in df_all.columns:
            rl = df_all['RISK_LABEL'].dropna()
            # Handle both cases: numeric (0/1/2) or string ('LOW'/'MEDIUM'/'HIGH')
            sample = str(rl.iloc[0]) if len(rl) > 0 else '0'
            if sample in ['LOW','MEDIUM','HIGH']:
                # already strings — use directly
                rc = rl.value_counts()
            else:
                # numeric — map to strings
                rc = rl.astype(int).map({0:'LOW', 1:'MEDIUM', 2:'HIGH'}).value_counts()
            rc = rc[rc.index.isin(['LOW','MEDIUM','HIGH'])]  # drop any NaN labels

            color_map = {'HIGH':'#f85149','MEDIUM':'#e3b341','LOW':'#3fb950'}

            if len(rc) >= 2:
                fig, ax = plt.subplots(figsize=(5, 3.5))
                fig.patch.set_facecolor('#161b22')
                ax.set_facecolor('#161b22')
                clrs_pie = [color_map.get(k,'#58a6ff') for k in rc.index]
                wedges, texts, autotexts = ax.pie(
                    rc.values, labels=rc.index, colors=clrs_pie,
                    autopct='%1.1f%%', textprops={'color':'#e6edf3','fontsize':11},
                    startangle=140, wedgeprops={'linewidth':1,'edgecolor':'#0d1117'}
                )
                for at in autotexts:
                    at.set_color('#0d1117'); at.set_fontweight('bold')
                ax.set_title('Risk Distribution — All Karnataka', color='#e6edf3', fontsize=11)
                st.pyplot(fig, use_container_width=True)
                plt.close()
            else:
                fig, ax = dark_fig(5, 3.5)
                ax.bar(rc.index, rc.values,
                       color=[color_map.get(k,'#58a6ff') for k in rc.index])
                ax.set_ylabel('Count', color='#8b949e')
                ax.set_title('Risk Distribution', color='#e6edf3')
                st.pyplot(fig, use_container_width=True)
                plt.close()
        else:
            st.info("RISK_LABEL column not found.")

    # Crime type bar
    with col_r2:
        st.markdown('<div class="section-title">📊 Top Crime Types</div>', unsafe_allow_html=True)
        if crime_cols:
            top_crimes = df_all[crime_cols].sum().nlargest(8)
            fig, ax = dark_fig(7, 3.5)
            ax.bar(range(len(top_crimes)), top_crimes.values, color='#58a6ff', alpha=0.85)
            ax.set_xticks(range(len(top_crimes)))
            ax.set_xticklabels([c.replace('_',' ')[:12] for c in top_crimes.index],
                                rotation=45, ha='right', fontsize=7, color='#8b949e')
            st.pyplot(fig, use_container_width=True)
            plt.close()

# ============================================================
# PAGE 2 — HOTSPOT MAP
# ============================================================
elif page == "🗺️ Hotspot Map":
    st.markdown("## 🗺️ Crime Hotspot Map")

    tab1, tab2 = st.tabs(["🔴 Cluster Map", "🌡️ Heatmap"])
    for tab, fname in [(tab1, 'karnataka_hotspot_map.html'), (tab2, 'karnataka_heatmap.html')]:
        with tab:
            fpath = os.path.join(OUTPUT_PATH, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)
            else:
                st.warning(f"{fname} not found. Run hotspot_model.py first.")

    if 'hotspot' in data:
        df_h = data['hotspot']
        if 'CLUSTER' in df_h.columns:
            st.markdown("### Cluster Summary")
            summary = df_h.groupby('CLUSTER').agg(
                Districts=(district_col, 'count'),
                Avg_Crimes=('TOTAL_CRIMES', 'mean')
            ).round(0).reset_index()
            summary['Type'] = summary['CLUSTER'].apply(lambda x: '🔴 Hotspot' if x != -1 else '⚪ Isolated')
            st.dataframe(summary, use_container_width=True)

    if os.path.exists(os.path.join(OUTPUT_PATH, 'hotspot_clusters.png')):
        st.image(os.path.join(OUTPUT_PATH, 'hotspot_clusters.png'), use_container_width=True)

# ============================================================
# PAGE 3 — RISK PREDICTOR
# ============================================================
elif page == "⚠️ Risk Predictor":
    st.markdown("## ⚠️ District Risk Predictor")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🎯 Predict Risk")
        pred_district = st.selectbox("Select District", all_districts)
        pred_year     = st.selectbox("Select Year", sorted(df[year_col].unique(), reverse=True))

        if st.button("🔍 Predict Risk", use_container_width=True):
            row = df[(df[district_col] == pred_district) & (df[year_col] == pred_year)]
            if row.empty:
                st.warning(f"No data for {pred_district} in {pred_year}")
            elif 'RISK_LABEL' in row.columns:
                rv_raw = row['RISK_LABEL'].values[0]
                # Handle both string ('LOW') and numeric (0/1/2) RISK_LABEL
                str_map = {'LOW': ('🟢 LOW RISK', '#3fb950'),
                           'MEDIUM': ('🟡 MEDIUM RISK', '#e3b341'),
                           'HIGH': ('🔴 HIGH RISK', '#f85149')}
                int_map = {0: ('🟢 LOW RISK', '#3fb950'),
                           1: ('🟡 MEDIUM RISK', '#e3b341'),
                           2: ('🔴 HIGH RISK', '#f85149')}
                if str(rv_raw).upper() in str_map:
                    label, color = str_map[str(rv_raw).upper()]
                else:
                    label, color = int_map.get(int(rv_raw), ('UNKNOWN', '#8b949e'))
                tc = int(row['TOTAL_CRIMES'].values[0]) if 'TOTAL_CRIMES' in row.columns else 'N/A'
                st.markdown(f"""
                <div style="background:#161b22; border:2px solid {color}; border-radius:10px;
                            padding:20px; text-align:center; margin-top:12px;">
                    <div style="font-size:2em; font-weight:bold; color:{color};">{label}</div>
                    <div style="color:#8b949e; margin-top:8px;">{pred_district} — {pred_year}</div>
                    <div style="color:#e6edf3; margin-top:8px;">Total Crimes: <strong>{tc:,}</strong></div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📊 All High Risk District-Years")
        src = data.get('risk', df)
        label_col = 'PREDICTED_RISK_LABEL' if 'PREDICTED_RISK_LABEL' in src.columns else 'RISK_LABEL'
        if label_col in src.columns:
            high = src[src[label_col] == 2][[district_col, year_col, 'TOTAL_CRIMES']].sort_values('TOTAL_CRIMES', ascending=False).head(20)
            st.dataframe(high, use_container_width=True)

    if os.path.exists(os.path.join(OUTPUT_PATH, 'xgb_results.png')):
        st.markdown("### Model Performance")
        st.caption("Note: 'Zz Total' in the chart is a dataset aggregate row — not a real district. Ignore it.")
        st.image(os.path.join(OUTPUT_PATH, 'xgb_results.png'), use_container_width=True)

# ============================================================
# PAGE 4 — FORECAST
# ============================================================
elif page == "📈 Crime Forecast":
    st.markdown("## 📈 Crime Forecast — Time Series")

    if 'forecast' in data:
        df_fc = data['forecast']

        # ── auto-detect column names ──
        # find district col
        fc_dist_col = district_col if district_col in df_fc.columns else df_fc.columns[0]
        # find year col
        fc_year_col = next((c for c in df_fc.columns if 'year' in c.lower()), df_fc.columns[1])
        # find crimes col (predicted or actual count)
        fc_crime_col = next((c for c in df_fc.columns
                             if any(k in c.lower() for k in ['predict','crime','count','yhat','value','total'])),
                            df_fc.select_dtypes(include='number').columns[0])
        # find is_forecast flag
        fc_flag_col = next((c for c in df_fc.columns if 'forecast' in c.lower() or 'flag' in c.lower()), None)

        fc_districts = sorted(df_fc[fc_dist_col].dropna().unique())
        fc_district = st.selectbox("Select District", fc_districts)
        df_d = df_fc[df_fc[fc_dist_col] == fc_district].sort_values(fc_year_col)

        if fc_flag_col:
            historical = df_d[df_d[fc_flag_col] == False]
            forecast   = df_d[df_d[fc_flag_col] == True]
        else:
            # no flag col — treat all as historical
            historical = df_d
            forecast   = pd.DataFrame()

        fig, ax = dark_fig(10, 4)
        if not historical.empty:
            ax.plot(historical[fc_year_col], historical[fc_crime_col],
                    color='#58a6ff', linewidth=2.5, marker='o', markersize=5, label='Historical')
        if not forecast.empty:
            ax.plot(forecast[fc_year_col], forecast[fc_crime_col],
                    color='#f85149', linewidth=2.5, linestyle='--', marker='s', markersize=5, label='Forecast')
            lb = next((c for c in forecast.columns if 'lower' in c.lower() or 'lb' in c.lower()), None)
            ub = next((c for c in forecast.columns if 'upper' in c.lower() or 'ub' in c.lower()), None)
            if lb and ub:
                ax.fill_between(forecast[fc_year_col], forecast[lb], forecast[ub],
                                alpha=0.2, color='#f85149', label='Confidence Band')
        ax.set_title(f'Crime Forecast — {fc_district}', color='#e6edf3', fontsize=13)
        ax.set_xlabel('Year', color='#8b949e')
        ax.set_ylabel('Crimes', color='#8b949e')
        ax.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='#e6edf3')
        st.pyplot(fig, use_container_width=True)
        plt.close()

        # Emerging threats
        trend_col = next((c for c in df_fc.columns if 'trend' in c.lower()), None)
        if trend_col and fc_flag_col:
            st.markdown("### 🚨 Emerging Threat Districts")
            threats = df_fc[
                (df_fc[fc_flag_col] == True) &
                (df_fc[trend_col].str.contains('INCREAS', na=False, case=False))
            ][[fc_dist_col, fc_year_col, fc_crime_col, trend_col]].drop_duplicates(fc_dist_col)
            if not threats.empty:
                st.dataframe(threats, use_container_width=True)
            else:
                st.info("No increasing trend districts in forecast period.")
    else:
        st.warning("crime_forecast.csv not found.")
        if os.path.exists(os.path.join(OUTPUT_PATH, 'forecast_top5_districts.png')):
            st.image(os.path.join(OUTPUT_PATH, 'forecast_top5_districts.png'), use_container_width=True)

# ============================================================
# PAGE 5 — ANOMALY ALERTS
# ============================================================
elif page == "🔴 Anomaly Alerts":
    st.markdown("## 🔴 Anomaly Detection — Unusual Crime Patterns")

    if 'anomaly' in data:
        df_an = data['anomaly']
        total_anom = int((df_an['IS_ANOMALY'] == 1).sum()) if 'IS_ANOMALY' in df_an.columns else 0
        critical   = int((df_an.get('ANOMALY_SEVERITY', pd.Series()) == 'CRITICAL').sum())
        pct        = round(total_anom / len(df_an) * 100, 1) if len(df_an) > 0 else 0

        c1, c2, c3 = st.columns(3)
        for col, val, label, color in [
            (c1, str(total_anom), "Anomalous Records",  "#f85149"),
            (c2, str(critical),   "Critical Severity",  "#f85149"),
            (c3, f"{pct}%",       "Anomaly Rate",       "#e3b341"),
        ]:
            col.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{color};">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🚨 Alert List")

        if 'IS_ANOMALY' in df_an.columns:
            cols_show = [district_col, year_col, 'TOTAL_CRIMES']
            if 'ANOMALY_SEVERITY' in df_an.columns: cols_show.append('ANOMALY_SEVERITY')
            if 'ANOMALY_SCORE'    in df_an.columns: cols_show.append('ANOMALY_SCORE')
            anomalies = df_an[df_an['IS_ANOMALY'] == 1][cols_show].sort_values('TOTAL_CRIMES', ascending=False)

            for _, row in anomalies.head(10).iterrows():
                sev  = row.get('ANOMALY_SEVERITY', 'HIGH')
                css  = 'alert-critical' if sev == 'CRITICAL' else 'alert-high'
                icon = '🔴' if sev == 'CRITICAL' else '🟡'
                tc   = int(row['TOTAL_CRIMES']) if pd.notna(row['TOTAL_CRIMES']) else 0
                st.markdown(f"""
                <div class="{css}">
                    {icon} <strong>{row[district_col]}</strong> ({int(row[year_col])})
                    — Total Crimes: <strong>{tc:,}</strong> &nbsp;|&nbsp; Severity: <strong>{sev}</strong>
                </div>""", unsafe_allow_html=True)

        if os.path.exists(os.path.join(OUTPUT_PATH, 'anomaly_results.png')):
            st.markdown("### Analysis Charts")
            st.image(os.path.join(OUTPUT_PATH, 'anomaly_results.png'), use_container_width=True)
    else:
        st.warning("anomaly_flagged.csv not found. Run anomaly_detection.py first.")

# ============================================================
# PAGE 6 — NETWORK ANALYSIS
# ============================================================
elif page == "🔗 Network Analysis":
    st.markdown("## 🔗 Criminal Network & Link Analysis")

    st.markdown("### 🔥 Crime Type Correlation Matrix")
    if crime_cols and len(crime_cols) >= 2:
        top12 = df_filtered[crime_cols].sum().nlargest(12).index.tolist()
        corr  = df_filtered[top12].corr()
        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_facecolor('#161b22')
        ax.set_facecolor('#161b22')
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn', ax=ax,
                    linewidths=0.5, linecolor='#30363d', annot_kws={'size': 8},
                    xticklabels=[c.replace('_',' ')[:12] for c in top12],
                    yticklabels=[c.replace('_',' ')[:12] for c in top12])
        ax.tick_params(colors='#8b949e', labelsize=8)
        ax.set_title('Crime Type Co-occurrence Correlation', color='#e6edf3', fontsize=12)
        st.pyplot(fig, use_container_width=True)
        plt.close()

    st.markdown("### 📌 District Crime Profile (Modus Operandi)")
    sel_d = st.selectbox("Select District", all_districts, key="net_d")
    df_d  = df[df[district_col] == sel_d]
    if not df_d.empty and crime_cols:
        profile = df_d[crime_cols].sum().nlargest(10)
        fig, ax = dark_fig(8, 3.5)
        clrs = ['#f85149' if i < 3 else '#e3b341' if i < 6 else '#58a6ff' for i in range(len(profile))]
        ax.bar([c.replace('_',' ')[:14] for c in profile.index], profile.values, color=clrs)
        ax.set_title(f'Crime Profile — {sel_d}', color='#e6edf3')
        ax.tick_params(colors='#8b949e', labelsize=8, rotation=45)
        st.pyplot(fig, use_container_width=True)
        plt.close()

# ============================================================
# PAGE 7 — RAW DATA EXPLORER
# ============================================================
elif page == "📋 Raw Data Explorer":
    st.markdown("## 📋 Raw Data Explorer")
    col1, col2 = st.columns(2)
    with col1:
        crime_filter = st.selectbox("Filter by Crime Type", ["All"] + crime_cols[:20])
    with col2:
        sort_options = ['TOTAL_CRIMES', year_col, district_col] if 'TOTAL_CRIMES' in df_filtered.columns else [year_col, district_col]
        sort_col = st.selectbox("Sort By", sort_options)

    df_disp = df_filtered.copy()
    if crime_filter != "All" and crime_filter in df_disp.columns:
        df_disp = df_disp[df_disp[crime_filter] > 0]
    df_disp = df_disp.sort_values(sort_col, ascending=False)

    st.dataframe(df_disp.head(200), use_container_width=True)
    st.caption(f"Showing {min(200, len(df_disp))} of {len(df_disp)} rows")

    csv_bytes = df_disp.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Filtered Data as CSV", data=csv_bytes,
                       file_name="karnataka_filtered.csv", mime="text/csv")

# ============================================================
# SIDEBAR FOOTER
# ============================================================
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="color:#8b949e; font-size:0.75em; text-align:center;">
KSP Crime Intelligence Platform<br>Karnataka State Police — SCRB<br>
Built with Python · Streamlit · ML
</div>""", unsafe_allow_html=True)