"""
SageMaker XGBoost Training Script

This script demonstrates a complete training job that can run on SageMaker.
It follows the SageMaker training script conventions.

Key Paths (IMPORTANT FOR EXAM):
- /opt/ml/input/data/<channel>/ : Training data
- /opt/ml/model/ : Save model artifacts here
- /opt/ml/input/config/hyperparameters.json : Hyperparameters
- /opt/ml/output/ : Output artifacts
"""

import argparse
import os
import json
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib

# SageMaker paths - MEMORIZE THESE FOR EXAM
MODEL_DIR = os.environ.get('SM_MODEL_DIR', '/opt/ml/model')
TRAIN_DIR = os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train')
VALIDATION_DIR = os.environ.get('SM_CHANNEL_VALIDATION', '/opt/ml/input/data/validation')
OUTPUT_DIR = os.environ.get('SM_OUTPUT_DATA_DIR', '/opt/ml/output')


def parse_args():
    """
    Parse hyperparameters passed by SageMaker.
    These come from the 'hyperparameters' dict in the Estimator.
    """
    parser = argparse.ArgumentParser()

    # XGBoost hyperparameters
    parser.add_argument('--max_depth', type=int, default=5)
    parser.add_argument('--eta', type=float, default=0.2)
    parser.add_argument('--num_round', type=int, default=100)
    parser.add_argument('--objective', type=str, default='binary:logistic')
    parser.add_argument('--subsample', type=float, default=0.8)
    parser.add_argument('--colsample_bytree', type=float, default=0.8)
    parser.add_argument('--min_child_weight', type=int, default=1)
    parser.add_argument('--gamma', type=float, default=0)

    # SageMaker specific
    parser.add_argument('--model_dir', type=str, default=MODEL_DIR)
    parser.add_argument('--train', type=str, default=TRAIN_DIR)
    parser.add_argument('--validation', type=str, default=VALIDATION_DIR)

    return parser.parse_args()


def load_data(data_dir):
    """
    Load training data from SageMaker input channel.

    SageMaker downloads S3 data to /opt/ml/input/data/<channel>/
    """
    # Find CSV file in the data directory
    input_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    if not input_files:
        raise ValueError(f"No CSV files found in {data_dir}")

    # Load and concatenate all CSV files
    dfs = []
    for file in input_files:
        file_path = os.path.join(data_dir, file)
        df = pd.read_csv(file_path, header=None)
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)

    # First column is label, rest are features (SageMaker convention)
    y = data.iloc[:, 0]
    X = data.iloc[:, 1:]

    return X, y


def train(args):
    """
    Main training function.
    """
    print("Loading training data...")
    X_train, y_train = load_data(args.train)
    print(f"Training data shape: {X_train.shape}")

    # Load validation data if available
    X_val, y_val = None, None
    if os.path.exists(args.validation):
        print("Loading validation data...")
        X_val, y_val = load_data(args.validation)
        print(f"Validation data shape: {X_val.shape}")

    # Create DMatrix (XGBoost's data structure)
    dtrain = xgb.DMatrix(X_train, label=y_train)

    # XGBoost parameters
    params = {
        'max_depth': args.max_depth,
        'eta': args.eta,
        'objective': args.objective,
        'subsample': args.subsample,
        'colsample_bytree': args.colsample_bytree,
        'min_child_weight': args.min_child_weight,
        'gamma': args.gamma,
        'eval_metric': 'auc'
    }

    print(f"Training with parameters: {params}")

    # Setup evaluation list
    evals = [(dtrain, 'train')]
    if X_val is not None:
        dval = xgb.DMatrix(X_val, label=y_val)
        evals.append((dval, 'validation'))

    # Train the model
    model = xgb.train(
        params=params,
        dtrain=dtrain,
        num_boost_round=args.num_round,
        evals=evals,
        early_stopping_rounds=10 if X_val is not None else None,
        verbose_eval=10
    )

    # Evaluate on training data
    train_preds = model.predict(dtrain)
    train_preds_binary = [1 if p > 0.5 else 0 for p in train_preds]
    train_accuracy = accuracy_score(y_train, train_preds_binary)
    train_auc = roc_auc_score(y_train, train_preds)

    print(f"\nTraining Accuracy: {train_accuracy:.4f}")
    print(f"Training AUC: {train_auc:.4f}")

    # Evaluate on validation data
    if X_val is not None:
        val_preds = model.predict(dval)
        val_preds_binary = [1 if p > 0.5 else 0 for p in val_preds]
        val_accuracy = accuracy_score(y_val, val_preds_binary)
        val_auc = roc_auc_score(y_val, val_preds)

        print(f"Validation Accuracy: {val_accuracy:.4f}")
        print(f"Validation AUC: {val_auc:.4f}")

    # Save model - MUST save to /opt/ml/model/ for SageMaker
    model_path = os.path.join(args.model_dir, 'xgboost-model')
    model.save_model(model_path)
    print(f"\nModel saved to {model_path}")

    # Save model metadata
    metadata = {
        'hyperparameters': params,
        'num_boost_round': args.num_round,
        'feature_count': X_train.shape[1],
        'training_samples': X_train.shape[0]
    }

    metadata_path = os.path.join(args.model_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print("Training complete!")


# Entry point functions for SageMaker inference
def model_fn(model_dir):
    """
    Load model for inference.
    SageMaker calls this when creating an endpoint.
    """
    model_path = os.path.join(model_dir, 'xgboost-model')
    model = xgb.Booster()
    model.load_model(model_path)
    return model


def input_fn(request_body, request_content_type):
    """
    Deserialize input data for inference.
    """
    if request_content_type == 'text/csv':
        # Parse CSV input
        import io
        df = pd.read_csv(io.StringIO(request_body), header=None)
        return xgb.DMatrix(df.values)
    elif request_content_type == 'application/json':
        # Parse JSON input
        data = json.loads(request_body)
        return xgb.DMatrix(pd.DataFrame(data).values)
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data, model):
    """
    Make predictions.
    """
    return model.predict(input_data)


def output_fn(prediction, accept):
    """
    Serialize predictions for response.
    """
    if accept == 'application/json':
        return json.dumps(prediction.tolist())
    elif accept == 'text/csv':
        return ','.join(map(str, prediction))
    else:
        return json.dumps(prediction.tolist())


if __name__ == '__main__':
    args = parse_args()
    train(args)
