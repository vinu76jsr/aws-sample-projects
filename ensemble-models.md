# Ensemble Models

An **ensemble model** combines multiple individual models to produce better predictions than any single model alone.

## Core Idea

```
Model A → Prediction A ─┐
Model B → Prediction B ─┼→ Combine → Final Prediction
Model C → Prediction C ─┘
```

"Wisdom of the crowd" - multiple weak learners together become a strong learner.

## Main Ensemble Techniques

### 1. Bagging (Bootstrap Aggregating)

- Train multiple models on **random subsets** of data
- Combine by **averaging** (regression) or **voting** (classification)
- Reduces **variance** (overfitting)

**Example**: Random Forest = Bagging + Decision Trees

```
Data → Random Subset 1 → Tree 1 ─┐
    → Random Subset 2 → Tree 2 ─┼→ Majority Vote → Prediction
    → Random Subset 3 → Tree 3 ─┘
```

### 2. Boosting

- Train models **sequentially**, each fixing errors of the previous
- Later models focus on **hard examples**
- Reduces **bias** (underfitting)

**Examples**: XGBoost, LightGBM, AdaBoost, Gradient Boosting

```
Data → Model 1 → Errors → Model 2 → Errors → Model 3 → Final
         ↑                  ↑                  ↑
    (all data)        (focus on M1          (focus on M1+M2
                        mistakes)             mistakes)
```

### 3. Stacking

- Train diverse models, then train a **meta-model** on their outputs
- Learns which model to trust for which type of input

```
Data → Random Forest → Pred 1 ─┐
    → XGBoost       → Pred 2 ─┼→ Meta-Model → Final
    → Neural Net    → Pred 3 ─┘
```

## Comparison

| Method | How it combines | Reduces | Example |
|--------|----------------|---------|---------|
| Bagging | Parallel + Average/Vote | Variance | Random Forest |
| Boosting | Sequential + Weighted | Bias | XGBoost |
| Stacking | Meta-model learns | Both | Custom pipelines |

## Why Ensembles Work

1. **Different errors cancel out** - models make different mistakes
2. **Captures diverse patterns** - each model sees data differently
3. **More robust** - less sensitive to noise

## Code Examples

### Random Forest (Bagging)

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,      # Number of trees
    max_depth=10,          # Limit tree depth
    random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### XGBoost (Boosting)

```python
import xgboost as xgb

model = xgb.XGBClassifier(
    n_estimators=100,      # Number of boosting rounds
    max_depth=6,           # Tree depth
    learning_rate=0.1,     # Step size shrinkage
    random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### Voting Classifier (Simple Ensemble)

```python
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Combine multiple different models
ensemble = VotingClassifier(
    estimators=[
        ('rf', RandomForestClassifier(n_estimators=100)),
        ('gb', GradientBoostingClassifier(n_estimators=100)),
        ('lr', LogisticRegression())
    ],
    voting='soft'  # Use predicted probabilities
)

ensemble.fit(X_train, y_train)
predictions = ensemble.predict(X_test)
```

### Stacking Classifier

```python
from sklearn.ensemble import StackingClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# Base models
base_models = [
    ('rf', RandomForestClassifier(n_estimators=100)),
    ('gb', GradientBoostingClassifier(n_estimators=100))
]

# Meta-model learns from base model predictions
stacking = StackingClassifier(
    estimators=base_models,
    final_estimator=LogisticRegression(),
    cv=5  # Cross-validation for generating meta-features
)

stacking.fit(X_train, y_train)
predictions = stacking.predict(X_test)
```

## When to Use Each Method

| Situation | Recommended Method |
|-----------|-------------------|
| Tabular data, general purpose | XGBoost / LightGBM |
| High variance (overfitting) | Random Forest (bagging) |
| High bias (underfitting) | Boosting methods |
| Kaggle competitions | Stacking multiple models |
| Need interpretability | Single decision tree or small RF |
| Production (simplicity matters) | Single well-tuned model |

## Popular Ensemble Libraries

| Library | Type | Strengths |
|---------|------|-----------|
| **XGBoost** | Boosting | Fast, regularization, handles missing values |
| **LightGBM** | Boosting | Very fast, memory efficient, leaf-wise growth |
| **CatBoost** | Boosting | Handles categorical features natively |
| **scikit-learn** | All types | Easy to use, good for learning |

## Ensemble in AWS SageMaker

SageMaker provides built-in ensemble support:

```python
# Using SageMaker's XGBoost
from sagemaker import image_uris
from sagemaker.estimator import Estimator

container = image_uris.retrieve('xgboost', region, version='1.5-1')

estimator = Estimator(
    image_uri=container,
    role=role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    hyperparameters={
        'num_round': 100,
        'max_depth': 6,
        'objective': 'binary:logistic'
    }
)
```

## Key Hyperparameters

### For Bagging (Random Forest)

| Parameter | Effect |
|-----------|--------|
| `n_estimators` | More trees = better but slower |
| `max_depth` | Deeper = more complex, risk overfitting |
| `max_features` | Features per split, lower = more diversity |

### For Boosting (XGBoost)

| Parameter | Effect |
|-----------|--------|
| `n_estimators` | More rounds = better but risk overfitting |
| `learning_rate` | Lower = needs more rounds, often better |
| `max_depth` | Usually keep shallow (3-6) |
| `subsample` | Row sampling, adds randomness |
| `colsample_bytree` | Column sampling, adds randomness |

## Trade-offs

| Aspect | Single Model | Ensemble |
|--------|--------------|----------|
| Accuracy | Lower | Higher |
| Training time | Faster | Slower |
| Inference time | Faster | Slower |
| Interpretability | Higher | Lower |
| Complexity | Lower | Higher |

## Best Practices

1. **Start simple** - Try a single model first, ensemble if needed
2. **Use diverse models** - Combine different algorithms for better results
3. **Cross-validate** - Especially important for stacking
4. **Watch for overfitting** - More models doesn't always mean better
5. **Consider production constraints** - Ensembles add latency and complexity
