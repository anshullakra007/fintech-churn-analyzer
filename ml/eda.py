import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def perform_eda(csv_path: str):
    """
    Performs Exploratory Data Analysis (EDA) on the augmented Churn dataset.
    """
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find file at {csv_path}")
        return

    # Set Seaborn style for a clean, professional look
    sns.set_theme(style="whitegrid", palette="muted")
    
    # Create directory for output visualizations if it doesn't exist
    os.makedirs('eda_visualizations', exist_ok=True)

    # 1. Calculate overall churn rate
    churn_rate = df['Exited'].mean() * 100
    print(f"\n--- Key Metrics ---")
    print(f"Overall Churn Rate: {churn_rate:.2f}%")

    # 2. Group by failed_transactions_last_30_days and calculate churn percentage
    churn_by_failures = df.groupby('failed_transactions_last_30_days')['Exited'].agg(['mean', 'count']).reset_index()
    churn_by_failures['Churn_Rate_Pct'] = churn_by_failures['mean'] * 100
    print("\n--- Churn Rate by Failed Transactions ---")
    print(churn_by_failures[['failed_transactions_last_30_days', 'count', 'Churn_Rate_Pct']].head(10))

    # 3. Calculate 'Revenue at Risk'
    # Define high risk as Exited == 1 for this retrospective calculation
    revenue_at_risk = df[df['Exited'] == 1]['Balance'].sum()
    print(f"\n--- Revenue at Risk ---")
    print(f"Total Balance of Churned (High-Risk) Users: ${revenue_at_risk:,.2f}")

    # Generate Visualizations

    # Plot 1: Correlation Heatmap
    plt.figure(figsize=(10, 8))
    # Select only numerical columns for correlation
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    
    # Create a mask for the upper triangle for a cleaner look
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    sns.heatmap(corr, mask=mask, cmap="coolwarm", vmax=1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=False)
    plt.title('Correlation Heatmap of Customer Features', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig('eda_visualizations/correlation_heatmap.png', dpi=300)
    plt.close()
    print("\nGenerated: eda_visualizations/correlation_heatmap.png")

    # Plot 2: Bar Chart of Churn Rate vs. Failed Transactions
    plt.figure(figsize=(12, 6))
    
    # Filter to view the most common failure counts for a cleaner chart (e.g., up to 10 failures)
    plot_data = churn_by_failures[churn_by_failures['failed_transactions_last_30_days'] <= 10]
    
    ax = sns.barplot(x='failed_transactions_last_30_days', y='Churn_Rate_Pct', 
                     data=plot_data, color='#3498db')
    
    plt.title('Impact of Payment Gateway Failures on Customer Churn', fontsize=16, pad=15)
    plt.xlabel('Number of Failed Transactions (Last 30 Days)', fontsize=12)
    plt.ylabel('Churn Rate (%)', fontsize=12)
    
    # Add value labels on top of bars
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.1f}%", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5), 
                    textcoords='offset points')
                    
    sns.despine(left=True)
    plt.tight_layout()
    plt.savefig('eda_visualizations/churn_vs_failures.png', dpi=300)
    plt.close()
    print("Generated: eda_visualizations/churn_vs_failures.png")

    # Plot 3: Distribution Plot of Balances (Churned vs. Retained)
    plt.figure(figsize=(10, 6))
    
    sns.kdeplot(data=df[df['Exited'] == 0], x='Balance', label='Retained (Exited=0)', 
                fill=True, color='#2ecc71', alpha=0.5)
    sns.kdeplot(data=df[df['Exited'] == 1], x='Balance', label='Churned (Exited=1)', 
                fill=True, color='#e74c3c', alpha=0.5)
                
    plt.title('Distribution of Account Balances: Retained vs. Churned Customers', fontsize=16, pad=15)
    plt.xlabel('Account Balance ($)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend()
    sns.despine(left=True)
    
    # Format x-axis with commas
    ax = plt.gca()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    plt.tight_layout()
    plt.savefig('eda_visualizations/balance_distribution.png', dpi=300)
    plt.close()
    print("Generated: eda_visualizations/balance_distribution.png")
    print("\nEDA complete. All visualizations saved to 'eda_visualizations/' directory.")

if __name__ == "__main__":
    # Pointing to the synthetic dataset we generated in Phase 1
    DATA_FILE = '../data/synthetic_churn_data.csv'
    perform_eda(DATA_FILE)
