import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
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
    # --- KPI Display ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", f"{kpi_dict['total_customers']:,}")
    col2.metric("Overall Churn Rate", f"{kpi_dict['churn_rate']:.2f}%")
    col3.metric("Revenue at Risk", format_currency(kpi_dict['revenue_risk']))
    
    # --- Phase 2: CLV Calculation ---
    retained_df = filtered_df[filtered_df['Exited'] == 0]
    # Assumed Margin * Balance * Tenure as a proxy for CLV
    clv_total = (retained_df['Balance'] * 0.10 * retained_df['Tenure']).sum()
    col4.metric("Projected Retained CLV", format_currency(clv_total))
    
    st.markdown("---")
    
    # --- Visualizations ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Churn Rate vs. Failed Transactions")
        churn_by_tx = filtered_df.groupby('failed_transactions_last_30_days')['Exited'].mean().reset_index()
        churn_by_tx['Churn Rate (%)'] = (churn_by_tx['Exited'] * 100).round(1)
        fig_tx = px.bar(churn_by_tx, x='failed_transactions_last_30_days', y='Churn Rate (%)', 
                        labels={'failed_transactions_last_30_days': 'Failed Transactions'},
                        text='Churn Rate (%)',
                        color_discrete_sequence=['#ef4444'])
        fig_tx.update_traces(textposition='outside', textfont=dict(color='#a1a1aa'))
        fig_tx.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa', showlegend=False, yaxis_range=[0,110])
        st.plotly_chart(fig_tx, use_container_width=True, config={'displayModeBar': False})
        
    with col_chart2:
        st.subheader("Customer Balance Distribution")
        fig_bal = px.violin(filtered_df, y="Balance", x="Exited", color="Exited", 
                               box=True, points=False,
                               labels={"Exited": "Churned (1=Yes, 0=No)"},
                               color_discrete_map={0: '#3b82f6', 1: '#ef4444'})
        fig_bal.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa', showlegend=False)
        st.plotly_chart(fig_bal, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    st.subheader("Churn Risk by Customer Tenure")
    churn_by_tenure = filtered_df.groupby('Tenure')['Exited'].mean().reset_index()
    churn_by_tenure['Churn Rate (%)'] = (churn_by_tenure['Exited'] * 100).round(1)
    fig_tenure = px.line(churn_by_tenure, x='Tenure', y='Churn Rate (%)', markers=True, 
                         labels={'Tenure': 'Years with Bank (Tenure)'},
                         color_discrete_sequence=['#8b5cf6'])
    fig_tenure.update_traces(line=dict(width=3), marker=dict(size=8), fill='tozeroy', fillcolor='rgba(139, 92, 246, 0.12)')
    fig_tenure.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#a1a1aa', yaxis_range=[0,100])
    st.plotly_chart(fig_tenure, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    # --- Phase 2: Cohort Analysis Heatmap ---
    st.subheader("Monthly Cohort Retention Matrix")
    st.markdown("<p style='font-size: 0.9rem; color: #94a3b8;'>Visualizing user drop-off across multiple onboarding cohorts over a 6-month period.</p>", unsafe_allow_html=True)
    
    cohort_data = np.array([
        [1.0, 0.85, 0.70, 0.60, 0.50, 0.45],
        [1.0, 0.82, 0.65, 0.55, 0.40, np.nan],
        [1.0, 0.88, 0.75, 0.62, np.nan, np.nan],
        [1.0, 0.80, 0.60, np.nan, np.nan, np.nan],
        [1.0, 0.75, np.nan, np.nan, np.nan, np.nan],
        [1.0, np.nan, np.nan, np.nan, np.nan, np.nan]
    ])
    fig_cohort, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(cohort_data, annot=True, fmt=".0%", cmap="YlGnBu", ax=ax,
                xticklabels=[f"Month {i}" for i in range(1, 7)],
                yticklabels=[f"Cohort {i}" for i in range(1, 7)])
    fig_cohort.patch.set_facecolor('#09090b')
    ax.set_facecolor('#09090b')
    ax.tick_params(colors='#a1a1aa')
    ax.xaxis.label.set_color('#a1a1aa')
    ax.yaxis.label.set_color('#a1a1aa')
    for t in ax.texts:
        t.set_color('#09090b')
    st.pyplot(fig_cohort)
