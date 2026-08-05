import pandas as pd
import sqlite3
import os

def build_database():
    print("--- Phase 1: Database Migration ---")
    
    csv_path = 'data/bi_export.csv'
    db_path = 'crm_data.db'
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run data_pipeline_for_bi.py first.")
        return
        
    print(f"1. Reading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Optional: sanitize column names to make SQL easier (remove spaces and special characters)
    # df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('%', 'pct')
    # Actually, let's keep them as is and quote them in SQL to match the dataframe exactly.
    
    print(f"2. Connecting to SQLite database ({db_path})...")
    conn = sqlite3.connect(db_path)
    
    print("3. Creating table 'customers' and inserting data...")
    # This will replace the table if it already exists
    df.to_sql('customers', conn, if_exists='replace', index=False)
    
    # Create an index to speed up queries based on Churn Risk
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_churn_risk ON customers ("Churn Risk (%)")')
    conn.commit()
    
    print("4. Verifying insertion...")
    cursor.execute('SELECT COUNT(*) FROM customers')
    count = cursor.fetchone()[0]
    print(f"   Successfully inserted {count} records into 'customers' table.")
    
    conn.close()
    print("\n✅ Database migration complete! You are ready to query crm_data.db")

if __name__ == "__main__":
    build_database()
