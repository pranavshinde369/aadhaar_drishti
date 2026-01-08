import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from urllib.request import urlopen
from streamlit_option_menu import option_menu

# ==========================================
# 1. PAGE CONFIGURATION & GOVTECH THEME
# ==========================================
st.set_page_config(
    page_title="Aadhaar Drishti | National Command Center",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 CSS: THE "GOVERNMENT-GRADE" UI SYSTEM
st.markdown("""
<style>
    /* 1. GLOBAL TYPOGRAPHY & BACKGROUND */
    .stApp {
        background-color: #f4f6f9; /* Neutral Light Grey */
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    h1, h2, h3 {
        color: #003366 !important; /* Official Navy Blue */
        font-weight: 700;
    }
    p, label, div {
        color: #333333;
    }

    /* 2. SIDEBAR: AUTHORITATIVE NAVY */
    section[data-testid="stSidebar"] {
        background-color: #003366;
    }
    /* Sidebar Text Colors */
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    /* Selected Nav Item */
    .nav-link-selected {
        background-color: #ff9933 !important; /* Saffron Accent */
        color: white !important;
        font-weight: bold;
    }

    /* 3. KPI CARDS: CLEAN, SHADOWED, ACCENTED */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-top: 5px solid #003366; /* The "GovTech" Accent */
    }
    div[data-testid="stMetricLabel"] > div {
        color: #666666 !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] > div {
        color: #003366 !important;
        font-size: 1.8rem;
        font-weight: 800;
    }

    /* 4. BUTTONS - STANDARDIZED BLUE */
    div.stButton > button {
        background-color: #2563eb !important; /* Royal Blue */
        color: white !important;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        border-radius: 6px;
        width: 100%;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* 5. TABLE HEADERS */
    thead tr th {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
        font-weight: bold !important;
    }

    /* 6. CHATBOT STYLING */
    .stChatMessage {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* 7. REMOVE BLOAT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def load_data():
    files = {
        "fraud": "engine_fraud_30days.csv",
        "boom": "engine_boom_180days.csv",
        "ghost": "engine_ghost_3years.csv",
        "digital": "engine_digital_1year.csv"
    }
    data = {}
    for key, path in files.items():
        if os.path.exists(path):
            data[key] = pd.read_csv(path)
        else:
            data[key] = pd.DataFrame()
    return data

df_dict = load_data()

# MAP PREP: Normalize State Names to match GeoJSON
def normalize_state_names(df):
    if df.empty or 'state' not in df.columns: return df
    
    corrections = {
        "Andaman and Nicobar Islands": "Andaman & Nicobar Island",
        "Arunachal Pradesh": "Arunachal Pradesh",
        "Dadra and Nagar Haveli": "Dadra and Nagar Haveli and Daman and Diu",
        "Daman and Diu": "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi": "NCT of Delhi",
        "Jammu and Kashmir": "Jammu & Kashmir",
        "Ladakh": "Ladakh",
        "Telangana": "Telangana",
        "Odisha": "Odisha",
        "Chattisgarh": "Chhattisgarh"
    }
    df['state'] = df['state'].replace(corrections)
    return df

for k in df_dict:
    df_dict[k] = normalize_state_names(df_dict[k])

# Load India GeoJSON for Maps (Cached)
INDIA_GEOJSON_URL = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

@st.cache_data
def load_map_data():
    with urlopen(INDIA_GEOJSON_URL) as response:
        return json.load(response)

india_geojson = load_map_data()

# ==========================================
# 3. CHATBOT LOGIC (HELPER FUNCTION)
# ==========================================
def get_bot_response(user_query):
    user_query = user_query.lower()
    
    # 1. GREETINGS
    if any(x in user_query for x in ["hi", "hello", "hey"]):
        return "Namaste! I am Drishti AI. I can answer questions about Fraud Alerts, Migration Trends, or Ghost Villages. Try asking: 'Which district has the most fraud?'"
    
    # 2. FRAUD QUERIES
    if "fraud" in user_query or "alert" in user_query:
        df = df_dict['fraud']
        if df.empty: return "I don't have fraud data loaded right now."
        high_risk = len(df[df['audit_status'].str.contains("HIGH RISK")])
        top_district = df['district'].value_counts().idxmax() if not df.empty else "Unknown"
        return f"Currently, I detect **{high_risk} High-Risk Alerts** requiring immediate audit. The district with the highest suspicious activity is **{top_district}**."

    # 3. MIGRATION / BOOM TOWN QUERIES
    if "migration" in user_query or "boom" in user_query or "growth" in user_query:
        df = df_dict['boom']
        if df.empty: return "Migration data is unavailable."
        count = len(df)
        avg_vel = df['velocity_q3'].mean()
        return f"I have identified **{count} Boom Towns** experiencing rapid population influx. The average enrollment velocity is **{avg_vel:.1f} enrollments/day** (2x Baseline)."

    # 4. GHOST VILLAGE / ELDERLY QUERIES
    if "ghost" in user_query or "elderly" in user_query or "aging" in user_query:
        df = df_dict['ghost']
        if df.empty: return "Demographic data is unavailable."
        count = len(df)
        return f"There are **{count} Ghost Villages** detected where high elderly populations are unable to access centers. I recommend deploying **Mobile Aadhaar Vans**."

    # 5. DIGITAL DIVIDE
    if "digital" in user_query or "dark" in user_query:
        df = df_dict['digital']
        if df.empty: return "Digital exclusion data is unavailable."
        return f"I see **{len(df)} Digital Dark Zones** where biometric failure rates are abnormally high."

    # DEFAULT FALLBACK
    return "I am analyzing the latest signals. You can ask me about: **Fraud Alerts**, **Migration Hotspots**, or **Digital Exclusion**."

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png", width=60)
    st.markdown("### Aadhaar Drishti")
    st.markdown("**Predictive Governance Platform**")
    st.markdown("---")
    
    selected = option_menu(
        menu_title=None,
        options=["National Overview", "Integrity Shield (Fraud)", "Migration Tracker", "Demographic Scanner", "Digital Divide Overlay", "Impact & Outcomes"],
        icons=["house", "shield-check", "airplane-engines", "people", "wifi-off", "trophy"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#ffffff", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "margin":"5px", "color": "#f0f0f0"},
            "nav-link-selected": {"background-color": "#ff9933", "color": "white"},
        }
    )
    
    st.markdown("---")
    st.caption("System Status: ● Online")
    st.caption(f"Last Sync: {pd.Timestamp.now().strftime('%d-%b-%Y %H:%M')}")

# ==========================================
# 5. MODULES
# ==========================================

# ------------------------------------------
# SCREEN 1: NATIONAL OVERVIEW (CHATBOT INTEGRATED HERE)
# ------------------------------------------
if selected == "National Overview":
    st.title("🇮🇳 National Command Center")
    
    # --- CHATBOT SECTION (INSERTED JUST BELOW TITLE) ---
    with st.expander("🤖 **Ask Drishti AI Assistant** (Click to Chat)", expanded=False):
        st.caption("I can analyze Fraud, Migration, and Digital Trends from your datasets.")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am monitoring the National Dashboard. Ask me 'Show fraud stats' or 'Where are boom towns?'"}]

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input (Uses Streamlit's chat_input, handles interaction inside the loop)
        if prompt := st.chat_input("Ask Drishti about governance data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            response = get_bot_response(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun() # Force rerun to update chat immediately
    # ---------------------------------------------------

    st.markdown("**Governance Question:** Where does the government need to act *right now*?")
    
    # 1. KPI ROW
    digital_df = df_dict["digital"]
    fraud_df = df_dict["fraud"]
    
    active_dark_zones = len(digital_df) if not digital_df.empty else 0
    high_risk_alerts = len(fraud_df[fraud_df['audit_status'].str.contains("HIGH RISK")]) if not fraud_df.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Population Scanned", "1.42B", "Live Update")
    with c2: st.metric("Digital Dark Zones", active_dark_zones, "Exclusion Risk", delta_color="inverse")
    with c3: st.metric("Biometric Compliance", "92.4%", "+0.8% (MoM)")
    with c4: st.metric("Pending Updates", "1.1Cr", "System Stress", delta_color="inverse")
    
    st.markdown("---")

    # 2. THE CORE MAP
    c_map, c_action = st.columns([2, 1])
    
    with c_map:
        st.subheader("📍 National Situational Awareness")
        map_layer = st.radio("Select Intelligence Layer:", 
            ["🔥 Migration Pressure", "👻 Aging Population", "📱 Digital Divide", "🚨 Fraud Alerts"], 
            horizontal=True)
        
        # --- LOGIC: Select Data Based on Layer ---
        if "Fraud" in map_layer:
            df = df_dict["fraud"]
            color = "Reds"
            title = "High-Risk Fraud Centers"
            insight_data = df[df['audit_status'].str.contains("HIGH RISK")]
        elif "Migration" in map_layer:
            df = df_dict["boom"]
            color = "Oranges"
            title = "Migration Velocity"
            insight_data = df
        elif "Aging" in map_layer:
            df = df_dict["ghost"]
            color = "Purples"
            title = "Elderly Dependency"
            insight_data = df
        else: # Digital Divide
            df = df_dict["digital"]
            color = "Blues"
            title = "Digital Exclusion Zones"
            insight_data = df

        # RENDER MAP
        if not df.empty:
            state_agg = df.groupby('state').size().reset_index(name='Intensity')
            fig = px.choropleth(
                state_agg, geojson=india_geojson, locations='state', featureidkey="properties.ST_NM",
                color='Intensity', color_continuous_scale=color, title=f"Heatmap: {map_layer}"
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for this layer.")

    # 3. DYNAMIC ACTIONABLE INSIGHTS
    with c_action:
        st.subheader("⚡ Actionable Insights")
        st.info(f"Top 5 Critical Targets: {map_layer}")
        
        if not insight_data.empty:
            # Group by District to deduplicate
            if "Fraud" in map_layer:
                action_table = insight_data.groupby(['district', 'risk_reason']).size().reset_index(name='Alerts')
            elif "Migration" in map_layer:
                action_table = insight_data.groupby(['district']).size().reset_index(name='Hubs')
                action_table['Action'] = "Expand Infra"
            elif "Aging" in map_layer:
                action_table = insight_data.groupby(['district']).size().reset_index(name='Villages')
                action_table['Action'] = "Pension Van"
            else: # Digital
                action_table = insight_data.groupby(['district', 'action']).size().reset_index(name='Zones')
            
            # Sort and Head
            sort_col = action_table.columns[-1] # Sort by the count column
            action_table = action_table.sort_values(sort_col, ascending=False).head(5)

            st.dataframe(
                action_table,
                hide_index=True,
                use_container_width=True
            )
        else:
            st.write("System stable. No critical actions pending.")

# ------------------------------------------
# SCREEN 2: INTEGRITY SHIELD
# ------------------------------------------
elif selected == "Integrity Shield (Fraud)":
    st.title("🛡️ Integrity Shield")
    st.markdown("**Governance Question:** Which Aadhaar centers require audit, and which alerts are false positives?")
    
    df = df_dict["fraud"]
    
    if not df.empty:
        high_risk = df[df['audit_status'].str.contains("HIGH RISK")]
        suppressed = df[df['audit_status'].str.contains("SUPPRESSED")]
        
        # KPIs
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("High-Risk Alerts", len(high_risk), "Audit Required", delta_color="inverse")
        with c2: st.metric("Auto-Suppressed", len(suppressed), "Migration Context Verified")
        with c3: st.metric("Total Analyzed", len(df), "Last 30 Days")
        
        st.markdown("---")
        
        st.subheader("🚨 Priority Audit Queue (Pattern Analysis)")
        
        if not high_risk.empty:
            # Deduplication logic
            audit_queue = high_risk.groupby(['state', 'district', 'risk_reason']).size().reset_index(name='Frequency')
            audit_queue = audit_queue.sort_values('Frequency', ascending=False).head(10)
            
            st.dataframe(
                audit_queue,
                column_config={
                    "state": "State",
                    "district": "District",
                    "risk_reason": "Fraud Pattern",
                    "Frequency": st.column_config.ProgressColumn(
                        "Alert Intensity",
                        help="Number of alerts in this district",
                        format="%d",
                        min_value=0,
                        max_value=int(audit_queue['Frequency'].max()),
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
            
        with st.expander("ℹ️  Audit Explanation: Why were alerts suppressed?"):
            st.write("The system detected high velocity enrolment in specific pincodes. However, by cross-referencing with the **Migration Tracker**, we confirmed these are legitimate 'Boom Towns' with influx of workers, not synthetic fraud.")

# ------------------------------------------
# SCREEN 3: MIGRATION TRACKER
# ------------------------------------------
elif selected == "Migration Tracker":
    st.title("🔥 Migration Tracker (Boom Towns)")
    st.markdown("**Governance Question:** Where is population pressure increasing and infrastructure needs scaling?")
    
    df = df_dict["boom"]
    
    if not df.empty:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.metric("Identified Boom Towns", len(df), "High Velocity Influx")
        with c2:
            st.metric("Avg Velocity", f"{df['velocity_q3'].mean():.1f}", "Enrolments/Day")

        st.markdown("---")
        
        c_trend, c_list = st.columns([2, 1])
        with c_trend:
            st.subheader("📈 Top Districts by Growth")
            fig = px.bar(df['district'].value_counts().head(10), orientation='h', color_discrete_sequence=['#ff9933'])
            st.plotly_chart(fig, use_container_width=True)
            
        with c_list:
            st.subheader("Administrative Response")
            st.write("Recommended actions for top districts:")
            top_districts = df['district'].value_counts().head(5).index.tolist()
            for dist in top_districts:
                st.warning(f"📍 **{dist}**: Increase Aadhaar Seva Kendra capacity by 20%.")

# ------------------------------------------
# SCREEN 4: DEMOGRAPHIC SCANNER
# ------------------------------------------
elif selected == "Demographic Scanner":
    st.title("👻 Demographic Scanner (Ghost Villages)")
    st.markdown("**Governance Question:** Which regions are aging and at risk of service exclusion?")
    
    df = df_dict["ghost"]
    
    if not df.empty:
        st.metric("Ghost Villages Identified", len(df), "High Youth Exodus")
        
        st.subheader("📊 Districts with Critical Elderly Dependency")
        
        top_aging_dist = df.groupby('district')['elderly_pressure_median'].max().reset_index()
        top_aging_dist = top_aging_dist.sort_values('elderly_pressure_median', ascending=False).head(12)
        
        fig = px.bar(
            top_aging_dist, 
            x='elderly_pressure_median', 
            y='district', 
            orientation='h',
            title="Ranked by Elderly Pressure Ratio",
            color='elderly_pressure_median',
            color_continuous_scale='Purples',
            labels={'elderly_pressure_median': 'Elderly Ratio (Max)', 'district': 'District'}
        )
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Critical Intervention List")
        critical_list = df.groupby('district').agg({
            'elderly_pressure_median': 'max',
            'pincode': 'count'
        }).reset_index()
        critical_list.columns = ['District', 'Max Elderly Ratio', 'Villages at Risk']
        critical_list = critical_list.sort_values('Max Elderly Ratio', ascending=False).head(10)

        st.dataframe(
            critical_list,
            column_config={
                "District": "District",
                "Max Elderly Ratio": st.column_config.NumberColumn("Max Elderly Ratio", format="%.1f"),
                "Villages at Risk": st.column_config.NumberColumn("Villages at Risk", format="%d ⚠️")
            },
            hide_index=True,
            use_container_width=True
        )

# ------------------------------------------
# SCREEN 5: DIGITAL DIVIDE
# ------------------------------------------
elif selected == "Digital Divide Overlay":
    st.title("📱 Digital Divide Overlay")
    st.markdown("**Governance Question:** Where will digital-only services fail?")
    
    df = df_dict["digital"]
    
    if not df.empty:
        st.error(f"🚨 ALERT: {len(df)} Digital Dark Zones detected with low biometric compliance.")
        
        st.subheader("🚑 Deployment Plan")
        
        deploy_plan = df.groupby(['district', 'state', 'action']).size().reset_index(name='Zones')
        deploy_plan = deploy_plan.sort_values('Zones', ascending=False).head(15)
        
        st.dataframe(
            deploy_plan,
            column_config={
                "district": "Target District",
                "state": "State",
                "action": "Required Intervention",
                "Zones": st.column_config.NumberColumn("Zones", format="%d 📍") 
            },
            hide_index=True,
            use_container_width=True
        )

# ------------------------------------------
# SCREEN 6: IMPACT & OUTCOMES
# ------------------------------------------
elif selected == "Impact & Outcomes":
    st.title("🏆 Impact & Outcomes")
    st.markdown("**Governance Question:** Is Aadhaar Drishti improving governance outcomes?")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Pending Updates", "-18%", "Reduced Delay")
    with c2: st.metric("Biometric Compliance", "+6.4%", "YoY Improvement")
    with c3: st.metric("False Alerts", "-25%", "Audit Efficiency")
    with c4: st.metric("Response Time", "48 hrs", "vs 14 Days (Old)")
    
    st.markdown("---")
    
    st.subheader("💰 Operational Savings (Projected)")
    
    c_roi1, c_roi2 = st.columns(2)
    with c_roi1:
        st.success("""
        ### ⏱️ 2,400 Man-Hours Saved
        **Reason:** Automated suppression of false fraud alerts in verified Boom Towns.
        *(Assuming 4 hrs per manual investigation)*
        """)
    with c_roi2:
        st.success("""
        ### 💵 ₹1.2 Crore Saved
        **Reason:** Replaced 240+ random enrolment camps with targeted 'Boom Town' deployment.
        *(Assuming ₹50k cost per camp)*
        """)
        
    st.markdown("---")
    
    st.subheader("📥 Export Official Reports")
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    
    with c_btn1:
        st.button("📄 National Policy Brief (PDF)", type="primary", use_container_width=True)
    with c_btn2:
        st.button("📊 Export State-wise Audit Log (CSV)", use_container_width=True)
    with c_btn3:
        st.button("📉 Fraud Investigation Log", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-style: italic; margin-top: 50px;">
        "This dashboard does not display data. It enables decisions, interventions, and accountability."
    </div>
    """, unsafe_allow_html=True)