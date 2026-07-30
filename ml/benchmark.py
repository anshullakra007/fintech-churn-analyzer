import time
import os
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from generate_and_train import generate_synthetic_data

def run_benchmarks():
    print("--- Starting Exhaustive Benchmarks ---")
    
    # 1. Data Generation Scalability
    print("\n1. Data Generation Scalability (100,000 records)")
    start_time = time.time()
    df_large = generate_synthetic_data(num_samples=100000)
    data_gen_time = time.time() - start_time
    print(f"Data Generation Time: {data_gen_time:.4f} seconds")
    
    # 2. Model Loading
    print("\n2. Model Loading")
    model_path = "churn_model.joblib"
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found.")
        return
    
    start_time = time.time()
    model = joblib.load(model_path)
    model_load_time = time.time() - start_time
    print(f"Model Load Time: {model_load_time:.4f} seconds")
    
    # 3. Data Preprocessing for Inference
    # Using 20% of the generated data for testing (~20,000 records)
    test_df = df_large.sample(frac=0.2, random_state=42)
    y_true = test_df['Exited']
    X_test_raw = test_df.drop('Exited', axis=1)
    
    # Apply exact same preprocessing (dummies) as training
    X_test_processed = pd.get_dummies(X_test_raw, columns=['Geography', 'Gender'], drop_first=True)
    
    # Ensure columns match training
    expected_cols = joblib.load('model_features.joblib')
    # Add missing cols with 0
    for col in expected_cols:
        if col not in X_test_processed.columns:
            X_test_processed[col] = 0
    # Keep only expected cols in correct order
    X_test_processed = X_test_processed[expected_cols]
    
    # 4. Inference Latency
    print("\n3. Inference Latency (20,000 records)")
    start_time = time.time()
    y_pred = model.predict(X_test_processed)
    y_pred_proba = model.predict_proba(X_test_processed)[:, 1]
    inference_time = time.time() - start_time
    print(f"Total Inference Time: {inference_time:.4f} seconds")
    print(f"Average Latency per Record: {(inference_time / len(X_test_processed)) * 1000:.4f} ms")
    
    # 5. Exhaustive ML Metrics
    print("\n4. Exhaustive Model Evaluation Metrics")
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_true, y_pred_proba)
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    
    print("\n--- Benchmarking Complete ---")
    
    # Write results to a JSON file for easy reading later if needed
    results = {
        "data_generation_seconds_100k": round(data_gen_time, 4),
        "model_load_seconds": round(model_load_time, 4),
        "inference_total_seconds_20k": round(inference_time, 4),
        "inference_ms_per_record": round((inference_time / len(X_test_processed)) * 1000, 4),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4)
        }
    }
    
    import json
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=4)
        
if __name__ == "__main__":
    run_benchmarks()
