import streamlit as st
import pandas as pd
from google import genai
import os
import io
import sqlite3

st.set_page_config(page_title="AI-Powered Customer Analytics Platform", layout="wide")

# --- Custom CSS Injection ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Premium Dark Background */
.stApp {
    background-color: #0a0a0c;
    color: #e4e4e7;
}

/* Sidebar refinement */
section[data-testid="stSidebar"] {
    background-color: #121214 !important;
    border-right: 1px solid #27272a;
}
section[data-testid="stSidebar"] .stRadio label {
    font-weight: 500;
    color: #a1a1aa;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: #3f3f46;
}
div[data-testid="metric-container"] > div {
    color: #f4f4f5;
}
div[data-testid="metric-container"] label {
    color: #a1a1aa !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Global Filters Container */
div[data-testid="stVerticalBlock"] div[style*="border"] {
    border-color: #27272a !important;
    border-radius: 8px !important;
    background-color: #0f0f11 !important;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
}

/* AI Alert Box */
.ai-alert-box {
    background: linear-gradient(145deg, #1e1b4b, #171717);
    border-left: 4px solid #6366f1;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    color: #e0e7ff;
    font-size: 1.05rem;
    line-height: 1.6;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
}

/* Smooth Buttons */
.stButton > button {
    border-radius: 6px !important;
    border: 1px solid #3f3f46 !important;
    background-color: #18181b !important;
    color: #e4e4e7 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #6366f1 !important;
    color: #ffffff !important;
    background-color: #312e81 !important;
}

/* Subheaders */
h1, h2, h3 {
    color: #f4f4f5 !important;
    font-weight: 500 !important;
    letter-spacing: -0.02em;
}
</style>
""", unsafe_allow_html=True)

# Import the new modular views
from views import executive_overview, ai_insights, retention_console, ab_testing_simulator, bi_dashboard

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

def generate_excel_report(df, kpi_dict):
    """Generates an Advanced Excel report with charts and conditional formatting."""
    output = io.BytesIO()
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # --- Sheet 1: Executive Summary ---
        summary_df = pd.DataFrame({
            'Metric': ['Total Customers', 'Overall Churn Rate (%)', 'Avg Failed Transactions', 'Revenue at Risk ($)'],
            'Value': [
                kpi_dict['total_customers'], 
                kpi_dict['churn_rate'], 
                kpi_dict['avg_failed_tx'], 
                kpi_dict['revenue_risk']
            ]
        })
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
        worksheet1 = writer.sheets['Executive Summary']
        
        # Format the summary sheet
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet1.write(0, col_num, value, header_format)
        worksheet1.set_column('A:A', 25)
        worksheet1.set_column('B:B', 20)
        
        # Add a native Excel Pie Chart
        chart = workbook.add_chart({'type': 'pie'})
        active_count = int(kpi_dict['total_customers'] * (1 - kpi_dict['churn_rate']/100))
        churned_count = kpi_dict['total_customers'] - active_count
        worksheet1.write('D1', 'Status', header_format)
        worksheet1.write('E1', 'Count', header_format)
        worksheet1.write('D2', 'Active')
        worksheet1.write('E2', active_count)
        worksheet1.write('D3', 'Churned')
        worksheet1.write('E3', churned_count)
        
        chart.add_series({
            'name': 'Customer Churn Distribution',
            'categories': "='Executive Summary'!$D$2:$D$3",
            'values':     "='Executive Summary'!$E$2:$E$3",
        })
        chart.set_title({'name': 'Customer Churn Distribution'})
        worksheet1.insert_chart('G2', chart)

        # --- Sheet 2: High-Risk Customers ---
        df.to_excel(writer, sheet_name='High-Risk Customers', index=False)
        worksheet2 = writer.sheets['High-Risk Customers']
        
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet2.set_column(i, i, column_len)
            
        if 'Churn Risk (%)' in df.columns:
            risk_col_idx = df.columns.get_loc('Churn Risk (%)')
            col_letter = chr(ord('A') + risk_col_idx) if risk_col_idx < 26 else chr(ord('A') + (risk_col_idx // 26) - 1) + chr(ord('A') + (risk_col_idx % 26))
            last_row = len(df) + 1
            range_str = f'{col_letter}2:{col_letter}{last_row}'
            
            format_red = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
            format_yellow = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
            
            worksheet2.conditional_format(range_str, {'type': 'cell', 'criteria': '>', 'value': 75, 'format': format_red})
            worksheet2.conditional_format(range_str, {'type': 'cell', 'criteria': 'between', 'minimum': 50, 'maximum': 75, 'format': format_yellow})
                                                      
    return output.getvalue()


st.title("AI-Powered Customer Analytics Platform")
st.markdown("Monitor customer churn metrics and the operational impact of payment gateway failures.")

# --- Architectural Overview ---
st.markdown("""
<div style="color: #a1a1aa; font-size: 0.95rem; line-height: 1.6; margin-bottom: 2rem;">
This dashboard is an end-to-end FinTech churn prediction engine. It evaluates how operational friction (like payment gateway failures) impacts customer retention. The architecture uses a live <strong>Random Forest ML model</strong> to score churn risk in real-time based on the global filters below. Additionally, the Retention Console leverages <strong>Google Gemini 2.5</strong> to calculate campaign ROI and automatically draft personalized recovery workflows for at-risk accounts.
</div>
""", unsafe_allow_html=True)

# Load Data Limits
@st.cache_data
def load_data_limits():
    try:
        conn = sqlite3.connect('crm_data.db')
        limits = pd.read_sql('SELECT MIN(Age) as min_age, MAX(Age) as max_age, MIN(CreditScore) as min_credit, MAX(CreditScore) as max_credit, MIN(failed_transactions_last_30_days) as min_fail, MAX(failed_transactions_last_30_days) as max_fail FROM customers', conn)
        conn.close()
        return limits.iloc[0]
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

limits = load_data_limits()

if limits is not None:
    # --- Sidebar Navigation ---
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Menu:", 
                                 ["Executive Overview", 
                                  "AI Insights", 
                                  "Retention Console", 
                                  "A/B Testing Simulator", 
                                  "BI Dashboard"])
    
    st.sidebar.markdown("---")

    # --- Main Page Filters (Always Visible) ---
    st.markdown("### Global Filters")
    with st.container(border=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            age_range = st.slider("Age Range", int(limits['min_age']), int(limits['max_age']), (int(limits['min_age']), int(limits['max_age'])))
        with col_f2:
            credit_range = st.slider("Credit Score", int(limits['min_credit']), int(limits['max_credit']), (int(limits['min_credit']), int(limits['max_credit'])))
        with col_f3:
            failed_tx = st.slider("Max Failed Transactions (30 Days)", int(limits['min_fail']), int(limits['max_fail']), int(limits['max_fail']))
    
    # Apply SQL Filters & CTE Rank
    try:
        conn = sqlite3.connect('crm_data.db')
        
        # Base filtered data for aggregate KPIs
        query_filtered = f"""
            SELECT * FROM customers
            WHERE Age BETWEEN {age_range[0]} AND {age_range[1]}
            AND CreditScore BETWEEN {credit_range[0]} AND {credit_range[1]}
            AND failed_transactions_last_30_days <= {failed_tx}
        """
        filtered_df = pd.read_sql(query_filtered, conn)
        
        # Phase 1: Complex SQL Query using CTE and Window Function for Top 50 Risk
        query_top_50 = f"""
            WITH RiskRankedCustomers AS (
                SELECT *,
                       RANK() OVER (ORDER BY "Churn Risk (%)" DESC, Balance DESC) as RiskRank
                FROM customers
                WHERE Age BETWEEN {age_range[0]} AND {age_range[1]}
                AND CreditScore BETWEEN {credit_range[0]} AND {credit_range[1]}
                AND failed_transactions_last_30_days <= {failed_tx}
            )
            SELECT * FROM RiskRankedCustomers
            WHERE RiskRank <= 50
        """
        top_50_risk = pd.read_sql(query_top_50, conn)
        conn.close()
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        filtered_df = pd.DataFrame()
        top_50_risk = pd.DataFrame()
    
    if filtered_df.empty:
        st.warning("No customers match the selected filter criteria. Please adjust the sliders.")
    else:
        
        # --- KPI Calculations ---
        total_customers = len(filtered_df)
        churn_rate = (filtered_df['Exited'].mean() * 100) if total_customers > 0 else 0
        avg_failed_tx = filtered_df['failed_transactions_last_30_days'].mean()
        revenue_at_risk = filtered_df[filtered_df['Exited'] == 1]['Balance'].sum()
        
        kpi_dict = {
            'total_customers': total_customers,
            'churn_rate': round(churn_rate, 2),
            'avg_failed_tx': round(avg_failed_tx, 2),
            'revenue_risk': revenue_at_risk
        }

        # Render corresponding view based on sidebar selection
        if selection == "Executive Overview":
            excel_data = generate_excel_report(filtered_df, kpi_dict)
            executive_overview.render(filtered_df, kpi_dict, excel_data)
            
        elif selection == "AI Insights":
            ai_insights.render(kpi_dict, get_ai_recommendation)
            
        elif selection == "Retention Console":
            retention_console.render(top_50_risk, generate_customer_outreach_script)
            
        elif selection == "A/B Testing Simulator":
            ab_testing_simulator.render()
            
        elif selection == "BI Dashboard":
            bi_dashboard.render(age_range, credit_range, failed_tx)
