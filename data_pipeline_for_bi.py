import pandas as pd
import joblib
import os

def run_pipeline():
    print("--- Starting BI Data Pipeline ---")
    
    data_path = 'data/synthetic_churn_data.csv'
    model_path = 'ml/churn_model.joblib'
    features_path = 'ml/model_features.joblib'
    
    if not os.path.exists(data_path):
        print(f"Error: Could not find data file at {data_path}")
        return
        
    print("1. Loading raw data...")
    df = pd.read_csv(data_path)
    
    print("2. Loading ML Models...")
    try:
        rf_model = joblib.load(model_path)
        expected_cols = joblib.load(features_path)
    except Exception as e:
        print(f"Error loading models: {e}")
        return
        
    print("3. Processing Features and Running Inference...")
    # Apply identical preprocessing
    X = pd.get_dummies(df.drop('Exited', axis=1, errors='ignore'), columns=['Geography', 'Gender'], drop_first=True)
    for col in expected_cols:
        if col not in X.columns:
            X[col] = 0
    X = X[expected_cols]
    
    # Predict Probability
    df['Churn Risk Probability'] = rf_model.predict_proba(X)[:, 1].round(4)
    df['Churn Risk (%)'] = (df['Churn Risk Probability'] * 100).round(2)
    
    # 4. Denormalize & Format for BI
    print("4. Formatting for BI Ingestion...")
    # Ensure types are string for categoricals
    df['Geography'] = df['Geography'].astype(str)
    df['Gender'] = df['Gender'].astype(str)
    
    # Create a descriptive risk tier column
    def get_risk_tier(prob):
        if prob > 0.75:
            return 'High Risk'
        elif prob > 0.50:
            return 'Medium Risk'
        return 'Low Risk'
        
    df['Risk Tier'] = df['Churn Risk Probability'].apply(get_risk_tier)
    
    # Save the cleaned dataset
    output_path = 'data/bi_export.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Pipeline Complete! BI-Ready file saved to: {output_path}")
    
    print("\n" + "="*50)
    print("Top Calculated Fields & DAX Formulas")
    print("="*50)
    
    print("\n--- TABLEAU (Calculated Fields) ---")
    print("1. Revenue at Risk")
    print("   SUM( IF [Exited] = 1 THEN [Balance] END )")
    print("\n2. Predicted Revenue at Risk")
    print("   SUM( [Balance] * [Churn Risk Probability] )")
    print("\n3. Average Failed Transactions (High Risk Users)")
    print("   AVG( IF [Risk Tier] = 'High Risk' THEN [failed_transactions_last_30_days] END )")
    
    print("\n--- POWER BI (DAX Formulas) ---")
    print("1. Revenue at Risk = ")
    print("   CALCULATE(SUM('bi_export'[Balance]), 'bi_export'[Exited] = 1)")
    print("\n2. Predicted Revenue at Risk = ")
    print("   SUMX('bi_export', 'bi_export'[Balance] * 'bi_export'[Churn Risk Probability])")
    print("\n3. High Risk Customer Count = ")
    print("   CALCULATE(COUNTROWS('bi_export'), 'bi_export'[Risk Tier] = \"High Risk\")")
    print("\n" + "="*50)

if __name__ == "__main__":
    run_pipeline()
