import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from huggingface_hub import HfApi

def generate_synthetic_data(num_samples=10000):
    np.random.seed(42)
    data = {
        'CreditScore': np.random.randint(300, 850, size=num_samples),
        'Geography': np.random.choice(['France', 'Spain', 'Germany'], size=num_samples),
        'Gender': np.random.choice(['Male', 'Female'], size=num_samples),
        'Age': np.random.randint(18, 92, size=num_samples),
        'Tenure': np.random.randint(0, 11, size=num_samples),
        'Balance': np.random.uniform(0, 250000, size=num_samples),
        'NumOfProducts': np.random.randint(1, 5, size=num_samples),
        'HasCrCard': np.random.randint(0, 2, size=num_samples),
        'IsActiveMember': np.random.randint(0, 2, size=num_samples),
        'EstimatedSalary': np.random.uniform(10.0, 200000.0, size=num_samples)
    }
    df = pd.DataFrame(data)
    
    # Simple probability model for churn
    churn_prob = np.zeros(num_samples)
    churn_prob += np.where(df['Geography'] == 'Germany', 0.1, 0)
    churn_prob += np.where(df['Age'] > 45, 0.2, 0)
    churn_prob += np.where(df['IsActiveMember'] == 0, 0.1, 0)
    churn_prob += np.where(df['Balance'] > 100000, 0.05, 0)
    
    df['Exited'] = np.random.binomial(1, np.clip(churn_prob, 0, 1))

    # Inject the failed_transactions metric as requested
    def generate_failed_tx(exited_status):
        if exited_status == 1:
            return np.random.poisson(lam=5.0)
        else:
            return np.random.poisson(lam=0.5)

    df['failed_transactions_last_30_days'] = df['Exited'].apply(generate_failed_tx)

    return df

def train_and_save_model():
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    
    os.makedirs('../data', exist_ok=True)
    df.to_csv('../data/synthetic_churn_data.csv', index=False)
    
    print("Preparing data for training...")
    # Encode categorical
    df = pd.get_dummies(df, columns=['Geography', 'Gender'], drop_first=True)
    
    X = df.drop('Exited', axis=1)
    y = df['Exited']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Save the model
    joblib.dump(model, 'churn_model.joblib')
    # Save the features expected
    joblib.dump(list(X.columns), 'model_features.joblib')
    print("Model saved to churn_model.joblib")

    # If HF token is available, push to hub
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        try:
            print("Uploading to Hugging Face...")
            api = HfApi(token=hf_token)
            # Create a repo name based on the current user or just standard
            user_info = api.whoami()
            username = user_info['name']
            repo_id = f"{username}/fintech-churn-model"
            
            api.create_repo(repo_id=repo_id, exist_ok=True)
            api.upload_file(
                path_or_fileobj="churn_model.joblib",
                path_in_repo="churn_model.joblib",
                repo_id=repo_id
            )
            api.upload_file(
                path_or_fileobj="model_features.joblib",
                path_in_repo="model_features.joblib",
                repo_id=repo_id
            )
            print(f"Successfully uploaded model to Hugging Face: {repo_id}")
        except Exception as e:
            print(f"Failed to upload to HF: {e}")
    else:
        print("No HF_TOKEN found, skipping upload.")

if __name__ == "__main__":
    train_and_save_model()
