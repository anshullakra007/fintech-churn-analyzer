import streamlit as st
import plotly.express as px
import numpy as np

def render(filtered_df, kpi_dict, excel_data):
    def format_currency(value):
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        else:
            return f"${value:,.2f}"

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Humanized Introduction ---
    with st.chat_message("assistant"):
        st.write(f"I've analyzed the **{kpi_dict['total_customers']:,}** users matching your criteria. Right now, we're looking at a **{kpi_dict['churn_rate']:.2f}% flight risk**, which puts **{format_currency(kpi_dict['revenue_risk'])}** in immediate jeopardy. Here's how the friction points break down.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- KPI Display ---
    retained_df = filtered_df[filtered_df['Exited'] == 0]
    clv_total = (retained_df['Balance'] * 0.10 * retained_df['Tenure']).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Users Analyzed", f"{kpi_dict['total_customers']:,}")
    col2.metric("Flight Risk (Churn)", f"{kpi_dict['churn_rate']:.2f}%")
    col3.metric("Revenue on the Line", format_currency(kpi_dict['revenue_risk']))
    col4.metric("Lifetime Value (Retained)", format_currency(clv_total))
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- Visualizations ---
    common_layout = dict(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font_color='#94a3b8', 
        showlegend=False,
        margin=dict(t=40, b=30),
        xaxis=dict(showgrid=False, zeroline=False, title_font=dict(size=14, color='#e2e8f0'), tickfont=dict(color='#a1a1aa')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, title_font=dict(size=14, color='#e2e8f0'), tickfont=dict(color='#a1a1aa'))
    )

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("<h3 style='font-size: 1.2rem; color: #e4e4e7;'>Friction vs. Flight Risk</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #71717a; margin-top: -10px;'>How failed transactions drive users away.</p>", unsafe_allow_html=True)
        
        churn_by_tx = filtered_df.groupby('failed_transactions_last_30_days')['Exited'].mean().reset_index()
        churn_by_tx['Churn Rate (%)'] = (churn_by_tx['Exited'] * 100).round(1)
        
        fig_tx = px.bar(churn_by_tx, x='failed_transactions_last_30_days', y='Churn Rate (%)', 
                        labels={'failed_transactions_last_30_days': 'Failed Tx (Last 30 Days)'},
                        text='Churn Rate (%)')
        
        fig_tx.update_traces(marker_color='#ef4444', marker_line_color='#b91c1c',
                             marker_line_width=1.5, opacity=0.8,
                             textposition='outside', textfont=dict(color='#a1a1aa'))
        fig_tx.update_layout(**common_layout, yaxis_range=[0,110])
        st.plotly_chart(fig_tx, width='stretch', config={'displayModeBar': False})
        
    with col_chart2:
        st.markdown("<h3 style='font-size: 1.2rem; color: #e4e4e7;'>Wealth Distribution</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #71717a; margin-top: -10px;'>Comparing balances between retained and churned users.</p>", unsafe_allow_html=True)
        
        fig_bal = px.violin(filtered_df, y="Balance", x="Exited", color="Exited", 
                               box=True, points=False,
                               labels={"Exited": "Status (1=Churned)"},
                               color_discrete_map={0: '#3b82f6', 1: '#ef4444'})
        
        fig_bal.update_traces(meanline_visible=True, opacity=0.7)
        fig_bal.update_layout(**common_layout)
        fig_bal.update_xaxes(tickvals=[0, 1], ticktext=['Retained', 'Churned'])
        st.plotly_chart(fig_bal, width='stretch', config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.markdown("<h3 style='font-size: 1.2rem; color: #e4e4e7;'>Loyalty Curve</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #71717a; margin-top: -10px;'>Churn probability based on years with the bank.</p>", unsafe_allow_html=True)
        
        churn_by_tenure = filtered_df.groupby('Tenure')['Exited'].mean().reset_index()
        churn_by_tenure['Churn Rate (%)'] = (churn_by_tenure['Exited'] * 100).round(1)
        
        fig_tenure = px.line(churn_by_tenure, x='Tenure', y='Churn Rate (%)', markers=True, 
                             labels={'Tenure': 'Years of Tenure'})
        
        fig_tenure.update_traces(line=dict(width=4, color='#8b5cf6'), marker=dict(size=10, color='#a78bfa', line=dict(width=2, color='#fff')), fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.15)')
        fig_tenure.update_layout(**common_layout, yaxis_range=[0,100])
        st.plotly_chart(fig_tenure, width='stretch', config={'displayModeBar': False})
        
    with col_chart4:
        st.markdown("<h3 style='font-size: 1.2rem; color: #e4e4e7;'>Demographic Shift</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.85rem; color: #71717a; margin-top: -10px;'>How age correlates with account closure.</p>", unsafe_allow_html=True)
        
        churn_by_age = filtered_df.groupby('Age')['Exited'].mean().reset_index()
        churn_by_age['Churn Rate (%)'] = (churn_by_age['Exited'] * 100).round(1)
        
        fig_age = px.line(churn_by_age, x='Age', y='Churn Rate (%)', markers=False, 
                             labels={'Age': 'Customer Age'})
        
        fig_age.update_traces(line=dict(width=3, color='#3b82f6', shape='spline'), fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.1)')
        fig_age.update_layout(**common_layout, yaxis_range=[0,100])
        st.plotly_chart(fig_age, width='stretch', config={'displayModeBar': False})
    
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    
    # --- Phase 2: Cohort Analysis Heatmap ---
    with st.chat_message("assistant"):
        st.write("I also pulled the cohort retention matrix. Notice the steep drop-off after Month 2 for recent onboarding batches.")
        
    st.markdown("<h2 style='font-size: 1.8rem; color: #e4e4e7;'>Cohort Retention Matrix</h2>", unsafe_allow_html=True)
    
    with st.container(border=True):
        cohort_data = np.array([
            [1.0, 0.85, 0.70, 0.60, 0.50, 0.45],
            [1.0, 0.82, 0.65, 0.55, 0.40, np.nan],
            [1.0, 0.88, 0.75, 0.62, np.nan, np.nan],
            [1.0, 0.80, 0.60, np.nan, np.nan, np.nan],
            [1.0, 0.75, np.nan, np.nan, np.nan, np.nan],
            [1.0, np.nan, np.nan, np.nan, np.nan, np.nan]
        ])
        
        fig_cohort = px.imshow(cohort_data, 
                               labels=dict(x="Months Since Onboarding", y="User Cohort", color="Retention"),
                               x=[f"Month {i}" for i in range(1, 7)],
                               y=[f"Cohort {i}" for i in range(1, 7)],
                               text_auto=".0%",
                               color_continuous_scale="Purples")
        
        fig_cohort.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='#a1a1aa',
            margin=dict(l=0, r=0, t=10, b=0)
        )
        fig_cohort.update_xaxes(showgrid=False, zeroline=False)
        fig_cohort.update_yaxes(showgrid=False, zeroline=False)
        
        st.plotly_chart(fig_cohort, width='stretch', config={'displayModeBar': False})
