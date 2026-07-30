import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
import os
import joblib

# --- Phase 4: Configure Gemini API ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.warning("GEMINI_API_KEY environment variable not set. AI insights will not be available.")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_ai_recommendation(kpi_data):
    """Generates an executive summary using Gemini API."""
    prompt = f"""
    You are a Senior Data Analyst. Review these dashboard metrics:
    - Total Customers: {kpi_data['total_customers']}
    - Churn Rate: {kpi_data['churn_rate']}%
    - Avg Failed Tx: {kpi_data['avg_failed_tx']}
    - Revenue at Risk: ${kpi_data['revenue_risk']:,.2f}
    
    Provide exactly 3 short, punchy bullet points analyzing the risk and suggesting immediate action for the Operations team. Do not use filler words. Speak like a real human analyst sending a quick Slack update. Use standard markdown bullet points (-).
    """
    try:
        if not client:
            return "AI Recommendation currently unavailable. API Key missing."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Recommendation currently unavailable. Please check API configuration. (Error: {str(e)})"

def generate_customer_outreach_script(customer_profile):
    """Generates a personalized outreach email for a specific customer."""
    prompt = f"""
    You are an empathetic, senior Customer Success Manager at a premium FinTech bank.
    Write a short, highly personalized apology and retention email to this specific customer 
    who is at high risk of churning due to our platform's technical payment failures.
    
    Customer Profile:
    - Age: {customer_profile['Age']}
    - Account Balance: ${customer_profile['Balance']:,.2f}
    - Recent Failed Transactions: {customer_profile['failed_transactions_last_30_days']}
    - Geography: {customer_profile['Geography']}
    - Tenure (Years with us): {customer_profile['Tenure']}
    
    Acknowledge the specific number of failed transactions. Emphasize that we value their business 
    (mentioning their tenure or balance subtly). Offer them a sincere apology and a direct line to 
    VIP support. Keep it professional, empathetic, and under 150 words. Do not use placeholders like [Your Name].
    """
    try:
        if not client:
            return "AI generation failed. API Key missing."
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI generation failed. (Error: {str(e)})"
# --- Phase 3: Streamlit App Configuration ---
st.set_page_config(page_title="FinTech Churn & Impact Analyzer", layout="wide")

# --- Custom CSS Injection (Glassmorphism & Neon Theme) ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Main Background and Typography */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif !important;
}

/* Clean, readable dark background */
.stApp {
    background: radial-gradient(circle at 10% 20%, #151821 0%, #0b0c10 100%);
    color: #e2e8f0;
}

/* Glassmorphism Containers */
.glass-container {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 2rem;
    margin-bottom: 2rem;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.glass-container:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.04);
}

/* AI Alert Box */
.ai-alert-box {
    background: rgba(15, 17, 26, 0.8);
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 0 15px rgba(102, 252, 241, 0.1);
    color: #e0e2e4;
    font-size: 1.1rem;
    line-height: 1.6;
    transition: all 0.3s ease;
    cursor: pointer;
}

.ai-alert-box:hover {
    transform: translateX(2px);
    box-shadow: -3px 3px 15px rgba(59, 130, 246, 0.1);
    background: rgba(20, 22, 33, 0.9);
}

/* Neon KPIs (Metrics) */
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.04);
}

div[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #c5c6c7 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: rgba(11, 12, 16, 0.85) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Headers */
h1, h2, h3 {
    color: #ffffff !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>FinTech Customer Churn & Impact Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.1rem; color: #94a3b8; margin-bottom: 1rem;'>Monitor customer churn metrics and the operational impact of payment gateway failures.</p>", unsafe_allow_html=True)

with st.expander("Quick Start Guide: How to use this Dashboard", expanded=False):
    st.markdown("""
    **Welcome to the Active CRM Command Center!** This dashboard doesn't just show data—it predicts customer churn and helps you actively recover lost revenue.

    **Step 1: Filter the Data (Sidebar)**
    Use the sidebar controls on the left to zero in on specific customer segments. Watch how the overall *Revenue at Risk* changes as you adjust the 'Max Failed Transactions'.

    **Step 2: Monitor AI Operational Alerts**
    Below, the Google Gemini AI acts as your data analyst, reading the live KPIs and instantly writing a 3-sentence executive summary based on the exact data you filtered.

    **Step 3: Run the ROI Simulator & Recover Customers**
    At the bottom of the page is the **Top 50 High-Risk Customers** queue. Select a customer from the dropdown, and the AI will draft a hyper-personalized apology email. Use the *Intervention ROI Simulator* in the sidebar to calculate if giving them a $50 statement credit will actually save the company money!
    """)
    st.markdown("<br>", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    try:
        # Load the augmented dataset from Phase 1
        df = pd.read_csv("data/synthetic_churn_data.csv")
        return df
    except FileNotFoundError:
        st.error("Dataset not found. Please ensure 'data/synthetic_churn_data.csv' exists.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Customer Data")
    st.sidebar.markdown("<p style='font-size: 0.9rem; color: #94a3b8; margin-top: -10px;'>Adjust these parameters to isolate user segments and see how technical friction impacts churn.</p>", unsafe_allow_html=True)
    
    age_range = st.sidebar.slider("Age Range", int(df['Age'].min()), int(df['Age'].max()), (int(df['Age'].min()), int(df['Age'].max())), help="Filter customers by their age to see demographic differences in churn.")
    credit_range = st.sidebar.slider("Credit Score", int(df['CreditScore'].min()), int(df['CreditScore'].max()), (int(df['CreditScore'].min()), int(df['CreditScore'].max())), help="Isolate customers based on their financial standing.")
    failed_tx = st.sidebar.slider("Max Failed Transactions (30 Days)", int(df['failed_transactions_last_30_days'].min()), int(df['failed_transactions_last_30_days'].max()), int(df['failed_transactions_last_30_days'].max()), help="CRITICAL METRIC: Lower this slider to see how reducing payment failures drastically lowers the 'Revenue at Risk'.")
    
    # Apply Filters
    filtered_df = df[
        (df['Age'].between(age_range[0], age_range[1])) &
        (df['CreditScore'].between(credit_range[0], credit_range[1])) &
        (df['failed_transactions_last_30_days'] <= failed_tx)
    ].copy()
    
    if filtered_df.empty:
        st.warning("No customers match the selected filter criteria. Please adjust the sliders.")
    else:
        # --- Live ML Inference ---
        # Load the trained Random Forest model to calculate actual churn probability
        try:
            rf_model = joblib.load('ml/churn_model.joblib')
            expected_cols = joblib.load('ml/model_features.joblib')
            
            X = pd.get_dummies(filtered_df.drop('Exited', axis=1, errors='ignore'), columns=['Geography', 'Gender'], drop_first=True)
            for col in expected_cols:
                if col not in X.columns:
                    X[col] = 0
            X = X[expected_cols]
            
            # Predict actual probability
            filtered_df['Churn Risk (%)'] = (rf_model.predict_proba(X)[:, 1] * 100).round(2)
        except Exception as e:
            st.error(f"Failed to load ML model. Ensure churn_model.joblib exists. Error: {str(e)}")
            filtered_df['Churn Risk (%)'] = 0.0

        # --- Phase 5: Intervention ROI Simulator (Sidebar) ---
        st.sidebar.markdown("---")
        st.sidebar.header("Intervention ROI Simulator")
        st.sidebar.markdown("<p style='font-size: 0.9rem; color: #94a3b8; margin-top: -10px;'>If we offer angry customers money to stay, do we still make a profit? Play with the numbers to find out.</p>", unsafe_allow_html=True)
        retention_cost = st.sidebar.number_input("Cost of Retention Offer ($/user)", min_value=0, value=50, step=10, help="How much are you willing to spend (e.g. statement credit) to save a single customer?")
        win_back_rate = st.sidebar.slider("Expected Win-Back Success Rate (%)", 0, 100, 40, help="If we send the apology email, what percentage of customers will actually decide to stay?")
        
        # Calculate potential ROI based on top 50 high-risk users using REAL ML Probability
        high_risk_df = filtered_df.sort_values(by=['Churn Risk (%)', 'Balance'], ascending=[False, False])
        top_50_risk = high_risk_df.head(50)
    total_campaign_cost = len(top_50_risk) * retention_cost
    projected_saved_revenue = (top_50_risk['Balance'].sum() * (win_back_rate / 100))
    net_roi = projected_saved_revenue - total_campaign_cost
    
    st.sidebar.metric("Total Campaign Cost", f"${total_campaign_cost:,.0f}")
    st.sidebar.metric("Projected Saved Revenue", f"${projected_saved_revenue:,.0f}")
    st.sidebar.metric("Net ROI", f"${net_roi:,.0f}", delta=f"{win_back_rate}% Success Rate")
    
    # --- KPI Calculations ---
    total_customers = len(filtered_df)
    churn_rate = (filtered_df['Exited'].mean() * 100) if total_customers > 0 else 0
    avg_failed_tx = filtered_df['failed_transactions_last_30_days'].mean()
    revenue_at_risk = filtered_df[filtered_df['Exited'] == 1]['Balance'].sum()
    
    # --- AI Root Cause Analysis (Phase 4) ---
    kpi_dict = {
        'total_customers': total_customers,
        'churn_rate': round(churn_rate, 2),
        'avg_failed_tx': round(avg_failed_tx, 2),
        'revenue_risk': revenue_at_risk
    }
    
    with st.spinner("Generating AI Operational Insights..."):
        ai_insight = get_ai_recommendation(kpi_dict)
    
    st.markdown(f"""
    <div class="ai-alert-box">
        <strong style="color: #3b82f6; font-size: 1.2rem;">AI Operational Alert:</strong><br>
        <span style="font-size: 0.9rem; color: #94a3b8;">Gemini AI is analyzing your exact dashboard filters above and recommending an immediate course of action.</span><br><br>
        {ai_insight}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- KPI Display ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Overall Churn Rate", f"{churn_rate:.2f}%")
    col3.metric("Revenue at Risk", f"${revenue_at_risk:,.2f}")
    
    st.markdown("---")
    
    # --- Visualizations ---
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Churn Rate vs. Failed Transactions")
        churn_by_tx = filtered_df.groupby('failed_transactions_last_30_days')['Exited'].mean().reset_index()
        churn_by_tx['Churn Rate (%)'] = (churn_by_tx['Exited'] * 100).round(1)
        fig_tx = px.bar(churn_by_tx, x='failed_transactions_last_30_days', y='Churn Rate (%)', 
                        labels={'failed_transactions_last_30_days': 'Failed Transactions'},
                        text='Churn Rate (%)',
                        color_discrete_sequence=['#e74c3c'])
        fig_tx.update_traces(textposition='outside', textfont=dict(color='#c5c6c7'))
        fig_tx.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#c5c6c7', showlegend=False, yaxis_range=[0,110])
        st.plotly_chart(fig_tx, use_container_width=True)
        
    with col_chart2:
        st.subheader("Customer Balance Distribution")
        # Overhauled from messy histogram to clean Violin Plot
        fig_bal = px.violin(filtered_df, y="Balance", x="Exited", color="Exited", 
                               box=True, points=False,
                               labels={"Exited": "Churned (1=Yes, 0=No)"},
                               color_discrete_map={0: '#66fcf1', 1: '#e74c3c'})
        fig_bal.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#c5c6c7', showlegend=False)
        st.plotly_chart(fig_bal, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Data Table: High-Risk Customers ---
    st.subheader("Top 50 'High-Risk' Customers")
    st.markdown("Users heavily impacted by payment failures, ranked by Live ML Prediction Risk.")
    
    # Add a pseudo-CustomerID for selection purposes
    top_50_risk = top_50_risk.copy()
    top_50_risk.reset_index(inplace=True)
    top_50_risk['Customer_ID'] = top_50_risk.index.map(lambda x: f"CUST-{1000 + x}")
    
    # Move Customer_ID to front
    cols = ['Customer_ID'] + [col for col in top_50_risk.columns if col != 'Customer_ID' and col != 'index']
    top_50_risk = top_50_risk[cols]
    
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.dataframe(top_50_risk.drop(columns=['Exited']), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Phase 5: Targeted Customer Recovery & AI Outreach ---
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.subheader("AI-Powered Customer Recovery")
    st.markdown("<p style='color: #c5c6c7;'>Select a high-risk customer from the table above to instantly generate a hyper-personalized retention outreach script.</p>", unsafe_allow_html=True)
    
    selected_cust_id = st.selectbox("Select Customer to Recover:", top_50_risk['Customer_ID'].tolist())
    
    if selected_cust_id:
        cust_profile = top_50_risk[top_50_risk['Customer_ID'] == selected_cust_id].iloc[0]
        
        st.write(f"**Selected Profile:** {cust_profile['Geography']} | Age: {cust_profile['Age']} | Balance: ${cust_profile['Balance']:,.2f} | Failed TXs: {cust_profile['failed_transactions_last_30_days']} | **Churn Risk:** {cust_profile['Churn Risk (%)']}%")
        
        if st.button("Generate Personalized Recovery Email"):
            with st.spinner("Gemini is drafting the outreach..."):
                outreach_script = generate_customer_outreach_script(cust_profile)
                st.success("Outreach Script Generated Successfully!")
                st.text_area("Copy and paste to CRM:", value=outreach_script, height=250)
    st.markdown('</div>', unsafe_allow_html=True)
