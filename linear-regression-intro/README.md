# Linear Regression - Learn by Example

A hands-on guide to understand linear regression from basics to regularization.

## What is Linear Regression?

Linear regression finds the **best-fit line** through your data to predict a continuous value.

```
Simple:    y = mx + b
Multiple:  y = b₀ + b₁x₁ + b₂x₂ + ... + bₙxₙ
```

Where:
- `y` = predicted value (target)
- `x` = input features
- `b` = coefficients (learned from data)

## How It Works

The algorithm finds coefficients that **minimize the sum of squared errors**:

```
Error = Σ (actual - predicted)²
```

This is called **Ordinary Least Squares (OLS)**.

## Project Structure

```
linear-regression-intro/
├── README.md
├── housing_data.csv              # Sample dataset
├── 01_simple_regression.py       # Single feature
├── 02_multiple_regression.py     # Multiple features
├── 03_preprocessing.py           # Feature scaling
├── 04_assumptions.py             # Check assumptions
└── 05_regularization.py          # Ridge, Lasso
```

## Learning Path

### 1. Simple Linear Regression (`01_simple_regression.py`)

Predict house price using only size.

```
price = m * size + b
```

**Key concepts:**
- Slope and intercept interpretation
- Train/test split
- R² score (how much variance explained)
- RMSE (prediction error in original units)

**Run:**
```bash
python 01_simple_regression.py
```

---

### 2. Multiple Linear Regression (`02_multiple_regression.py`)

Predict price using all features: size, bedrooms, age, distance.

```
price = b₀ + b₁*size + b₂*bedrooms + b₃*age + b₄*distance
```

**Key concepts:**
- Multiple coefficients
- Each coefficient = effect when other features held constant
- Actual vs predicted comparison

**Run:**
```bash
python 02_multiple_regression.py
```

---

### 3. Feature Scaling (`03_preprocessing.py`)

Why and how to scale features.

**Problem:**
```
size: 1100-2500 sqft
bedrooms: 2-5
```

Features have different scales → can affect model training.

**Solutions:**
- **StandardScaler**: mean=0, std=1
- **MinMaxScaler**: range 0-1

**Key concepts:**
- Fit scaler on training data only
- Transform both train and test
- Compare coefficient importance after scaling

**Run:**
```bash
python 03_preprocessing.py
```

---

### 4. Checking Assumptions (`04_assumptions.py`)

Linear regression assumes:

| Assumption | What it means | How to check |
|------------|---------------|--------------|
| **Linearity** | X and y have linear relationship | Residuals vs fitted plot |
| **Normality** | Residuals are normally distributed | Histogram, Shapiro-Wilk test |
| **Homoscedasticity** | Constant variance in residuals | Residuals spread evenly |
| **No multicollinearity** | Features not highly correlated | Correlation matrix |

**Run:**
```bash
python 04_assumptions.py
```

---

### 5. Regularization (`05_regularization.py`)

Prevent overfitting with penalties on coefficients.

| Method | Penalty | Effect |
|--------|---------|--------|
| **Ridge (L2)** | α × Σ(coef²) | Shrinks coefficients |
| **Lasso (L1)** | α × Σ\|coef\| | Can zero out coefficients |
| **ElasticNet** | Both L1 + L2 | Best of both |

**When to use:**
- Ridge: Many features, all useful
- Lasso: Want feature selection
- ElasticNet: Correlated features

**Run:**
```bash
python 05_regularization.py
```

## Dataset: housing_data.csv

25 house records with intentional patterns:

| Column | Description | Range |
|--------|-------------|-------|
| size_sqft | House size | 1100-2500 |
| bedrooms | Number of bedrooms | 2-5 |
| age_years | Age of house | 1-20 |
| distance_city_km | Distance from city | 2-25 |
| price_lakhs | Price (target) | 32-115 |

**Expected relationships:**
- ↑ size → ↑ price
- ↑ bedrooms → ↑ price
- ↑ age → ↓ price
- ↑ distance → ↓ price

## Key Metrics

### R² (R-squared)

```
R² = 1 - (unexplained variance / total variance)
```

| Value | Interpretation |
|-------|----------------|
| 1.0 | Perfect fit |
| 0.8+ | Strong |
| 0.5-0.8 | Moderate |
| <0.5 | Weak |

### RMSE (Root Mean Squared Error)

```
RMSE = √(Σ(actual - predicted)² / n)
```

RMSE is in the same units as target (lakhs), so it's interpretable.

## Common Pitfalls

1. **Not scaling features** → Coefficients not comparable
2. **Ignoring multicollinearity** → Unstable coefficients
3. **Using R² only** → Can be misleading with many features
4. **Overfitting** → Great train score, poor test score
5. **Leaking test data** → Fitting scaler on full dataset

## Quick Reference

### Scikit-learn Code Pattern

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# Predict
predictions = model.predict(X_test_scaled)

# Coefficients
print(model.coef_)        # Feature weights
print(model.intercept_)   # Bias term
```

## Requirements

```bash
pip install pandas numpy scikit-learn matplotlib scipy
```

## Next Steps

After mastering linear regression:
1. **Polynomial Regression** - Capture non-linear relationships
2. **Logistic Regression** - Classification problems
3. **Gradient Descent** - Understand optimization
4. **Regularization tuning** - GridSearchCV for best alpha
5. **Tree-based models** - Random Forest, XGBoost
