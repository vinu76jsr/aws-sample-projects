# Linear Regression - A Complete Beginner's Guide

Learn linear regression from scratch. No prior machine learning knowledge required.

## What Problem Does This Solve?

Imagine you're a real estate agent. A client asks: **"How much is my 1,800 sqft house worth?"**

You could:
1. **Guess** - Not reliable
2. **Look up similar houses** - Time consuming
3. **Use a formula** - Fast and consistent ✓

Linear regression creates that formula automatically by learning from past data.

## The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                    MACHINE LEARNING                         │
│                                                             │
│    Historical Data  ──→  Algorithm  ──→  Predictions        │
│    (houses sold)        (learns)        (new house price)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Machine Learning** = Teaching computers to find patterns in data, then use those patterns to make predictions on new data.

**Linear Regression** = One of the simplest ML algorithms. It finds a straight-line relationship between inputs and outputs.

## What is Linear Regression?

### The Simplest Explanation

You probably learned this in school:

```
y = mx + b
```

That's it. Linear regression finds the best values for `m` (slope) and `b` (intercept) that fit your data.

### Real Example

Let's say bigger houses cost more:

```
House Size (sqft)    Price (lakhs)
     1000                 35
     1500                 52
     2000                 70
     2500                 87
```

Linear regression finds: `price = 0.035 × size + 0`

Now for a **1,800 sqft house**: `0.035 × 1800 = 63 lakhs`

### Visual Understanding

```
Price
(lakhs)
   │
90 ┤                              *
   │                          *
70 ┤                    ──────────── Best fit line
   │              *  ───
50 ┤          ────
   │      *───
30 ┤  ────
   │
   └──────────────────────────────────── Size (sqft)
      1000    1500    2000    2500
```

The algorithm draws the line that's closest to all points.

## Key Terms Explained (Plain English)

### Features (Inputs)

**What it is**: The information you use to make predictions.

**Example**: House size, number of bedrooms, age of house.

**Also called**: Independent variables, predictors, X.

```
Features: [size=1800, bedrooms=3, age=5]  →  Prediction: 65 lakhs
```

### Target (Output)

**What it is**: The thing you're trying to predict.

**Example**: House price.

**Also called**: Dependent variable, label, y.

### Training Data

**What it is**: Historical examples the algorithm learns from.

**Example**: 100 houses with known prices.

**Analogy**: Like studying past exam questions before a test.

### Test Data

**What it is**: New examples to check if the model learned correctly.

**Example**: 20 houses the model has never seen.

**Analogy**: Like the actual exam after studying.

### Model

**What it is**: The formula/pattern the algorithm discovers.

**Example**: `price = 0.035 × size + 2.5 × bedrooms - 0.8 × age + 10`

### Prediction

**What it is**: Using the model to estimate the target for new data.

**Example**: Model says a new house should cost 65 lakhs.

## How Does It Learn?

### Step 1: Start with a Guess

The algorithm starts with random values for the formula:
```
price = 0.01 × size + 5  (random guess)
```

### Step 2: Calculate Errors

Compare predictions to actual prices:
```
House 1: Predicted 15, Actual 35  →  Error = 20
House 2: Predicted 20, Actual 52  →  Error = 32
House 3: Predicted 25, Actual 70  →  Error = 45
```

### Step 3: Adjust to Reduce Errors

Tweak the formula to make predictions closer:
```
price = 0.02 × size + 5  (better)
price = 0.03 × size + 5  (even better)
price = 0.035 × size + 0  (best fit!)
```

### Step 4: Stop When Errors are Minimized

The algorithm finds the line that minimizes the total error across all training examples.

## Understanding the Code

### Loading Data

```python
import pandas as pd

# Load your data from a CSV file
df = pd.read_csv('housing_data.csv')

# See first 5 rows
print(df.head())
```

**What this does**: Reads your data file into a table (called DataFrame).

**Analogy**: Opening an Excel spreadsheet.

### Separating Features and Target

```python
# X = features (inputs)
X = df[['size_sqft', 'bedrooms', 'age_years']]

# y = target (what we predict)
y = df['price_lakhs']
```

**What this does**: Splits your table into inputs (X) and output (y).

**Why**: The algorithm needs to know what to learn from (X) and what to predict (y).

### Train/Test Split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,    # 20% for testing
    random_state=42   # For reproducibility
)
```

**What this does**: Randomly divides data into two groups:
- **Training set (80%)**: Algorithm learns from this
- **Test set (20%)**: We check accuracy on this

**Why**: If we test on the same data we trained on, we don't know if the model truly learned or just memorized.

**Analogy**:
- Training = Studying with practice problems
- Testing = Taking the real exam with new problems

### Creating and Training the Model

```python
from sklearn.linear_model import LinearRegression

# Create the model (empty formula)
model = LinearRegression()

# Train it (find the best formula)
model.fit(X_train, y_train)
```

**What `fit()` does**:
1. Looks at all training examples
2. Finds the formula that best predicts prices
3. Stores the formula inside `model`

### Viewing the Formula

```python
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)
```

**Output might be**:
```
Coefficients: [0.035, 5.2, -0.8]
Intercept: 10.5
```

**This means**:
```
price = 0.035×size + 5.2×bedrooms - 0.8×age + 10.5
```

**Interpretation**:
- Each 1 sqft increase → price increases by 0.035 lakhs
- Each extra bedroom → price increases by 5.2 lakhs
- Each year older → price decreases by 0.8 lakhs

### Making Predictions

```python
# Predict on test data
predictions = model.predict(X_test)

# Predict for a specific house
new_house = [[1800, 3, 5]]  # 1800 sqft, 3 bed, 5 years old
predicted_price = model.predict(new_house)
print(f"Predicted price: {predicted_price[0]:.2f} lakhs")
```

**What this does**: Uses the learned formula to estimate prices for new houses.

## How Good is the Model?

### R² Score (R-squared)

**What it measures**: How much of the price variation does the model explain?

```python
from sklearn.metrics import r2_score

r2 = r2_score(y_test, predictions)
print(f"R² Score: {r2:.2f}")
```

**Interpretation**:

| R² Value | Meaning |
|----------|---------|
| 1.0 | Perfect! Model explains all variation |
| 0.8 | Great - explains 80% of variation |
| 0.5 | Okay - explains 50% of variation |
| 0.2 | Poor - model is missing something |
| 0.0 | Useless - no better than guessing the average |

**Analogy**: If R² = 0.8, it's like getting 80% on an exam.

### RMSE (Root Mean Squared Error)

**What it measures**: On average, how far off are predictions?

```python
from sklearn.metrics import mean_squared_error
import numpy as np

mse = mean_squared_error(y_test, predictions)
rmse = np.sqrt(mse)
print(f"RMSE: {rmse:.2f} lakhs")
```

**Interpretation**: If RMSE = 5, predictions are typically off by about 5 lakhs.

**Why RMSE over plain error?**
- Penalizes big mistakes more than small ones
- Same units as target (lakhs), so it's interpretable

## Why Split Into Train and Test?

### The Problem: Overfitting

Imagine a student who memorizes all practice problems word-for-word instead of understanding the concepts. They'll ace the practice test but fail on new problems.

**Overfitting** = Model memorizes training data instead of learning patterns.

```
Overfit model:
- Training accuracy: 99%   ← Memorized
- Test accuracy: 45%       ← Can't generalize

Good model:
- Training accuracy: 85%
- Test accuracy: 82%       ← Similar = learned real patterns
```

### The Solution: Test on Unseen Data

By keeping some data aside for testing, we can detect if the model truly learned or just memorized.

## Feature Scaling: Why It Matters

### The Problem

Look at these feature ranges:

```
size_sqft:  1000 - 2500  (large numbers)
bedrooms:   2 - 5        (small numbers)
```

The algorithm might think size is more important just because the numbers are bigger.

### The Solution: Scaling

Make all features have similar ranges:

**StandardScaler** (most common):
```
Original: [1000, 1500, 2000, 2500]
Scaled:   [-1.3, -0.4, 0.4, 1.3]   (mean=0, spread=1)
```

**Code**:
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Learn and apply
X_test_scaled = scaler.transform(X_test)        # Apply only
```

**Important**: Fit the scaler on training data only! Otherwise you're "cheating" by using test data information.

## Complete Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. LOAD DATA                                               │
│     df = pd.read_csv('data.csv')                           │
├─────────────────────────────────────────────────────────────┤
│  2. PREPARE DATA                                            │
│     X = df[features]                                        │
│     y = df[target]                                          │
├─────────────────────────────────────────────────────────────┤
│  3. SPLIT DATA                                              │
│     X_train, X_test, y_train, y_test = train_test_split()  │
├─────────────────────────────────────────────────────────────┤
│  4. SCALE FEATURES (optional but recommended)               │
│     scaler.fit_transform(X_train)                          │
│     scaler.transform(X_test)                               │
├─────────────────────────────────────────────────────────────┤
│  5. TRAIN MODEL                                             │
│     model.fit(X_train, y_train)                            │
├─────────────────────────────────────────────────────────────┤
│  6. EVALUATE                                                │
│     predictions = model.predict(X_test)                     │
│     r2_score(y_test, predictions)                          │
├─────────────────────────────────────────────────────────────┤
│  7. USE FOR NEW DATA                                        │
│     model.predict(new_data)                                │
└─────────────────────────────────────────────────────────────┘
```

## Project Files

Run these in order:

| File | What You'll Learn |
|------|-------------------|
| `01_simple_regression.py` | Basics with one feature |
| `02_multiple_regression.py` | Multiple features |
| `03_preprocessing.py` | Feature scaling |
| `04_assumptions.py` | When linear regression works |
| `05_regularization.py` | Preventing overfitting |

### How to Run

```bash
# Install required packages
pip install pandas numpy scikit-learn matplotlib scipy

# Run examples
cd linear-regression-intro
python 01_simple_regression.py
```

Each script prints detailed explanations and creates visualizations.

## Dataset: housing_data.csv

25 house records with these columns:

| Column | What It Is | Example |
|--------|-----------|---------|
| `size_sqft` | House size in square feet | 1800 |
| `bedrooms` | Number of bedrooms | 3 |
| `age_years` | How old the house is | 5 |
| `distance_city_km` | Distance from city center | 10 |
| `price_lakhs` | Price in lakhs (target) | 65 |

**Expected patterns**:
- Bigger houses → Higher prices
- More bedrooms → Higher prices
- Older houses → Lower prices
- Farther from city → Lower prices

## Common Beginner Mistakes

### 1. Not Splitting Data
```python
# WRONG: Testing on training data
model.fit(X, y)
predictions = model.predict(X)  # Same data!

# RIGHT: Separate test set
X_train, X_test, y_train, y_test = train_test_split(X, y)
model.fit(X_train, y_train)
predictions = model.predict(X_test)  # New data
```

### 2. Fitting Scaler on All Data
```python
# WRONG: Scaler sees test data
scaler.fit(X)  # Includes test data!

# RIGHT: Fit only on training data
scaler.fit(X_train)
```

### 3. Forgetting to Scale Test Data
```python
# WRONG: Scaled training, unscaled test
X_train_scaled = scaler.fit_transform(X_train)
predictions = model.predict(X_test)  # Unscaled!

# RIGHT: Scale both
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
predictions = model.predict(X_test_scaled)
```

### 4. Using Wrong Data Shape
```python
# WRONG: Single value prediction
model.predict(1800)  # Error!

# RIGHT: 2D array
model.predict([[1800]])  # Works
```

## Glossary

| Term | Simple Definition |
|------|-------------------|
| **Algorithm** | Step-by-step instructions for solving a problem |
| **Coefficient** | The multiplier for each feature in the formula |
| **Feature** | Input variable used for prediction |
| **Fit** | Train the model on data |
| **Intercept** | The base value when all features are zero |
| **Model** | The learned formula/pattern |
| **Overfitting** | Model memorizes instead of learning |
| **Prediction** | The model's guess for new data |
| **R² Score** | How much variation the model explains (0-1) |
| **RMSE** | Average prediction error |
| **Target** | What you're trying to predict |
| **Training** | Teaching the model with historical data |

## What's Next?

After mastering linear regression:

1. **Logistic Regression** - Predict categories (yes/no, spam/not spam)
2. **Decision Trees** - More flexible, handles non-linear patterns
3. **Random Forest** - Multiple trees for better accuracy
4. **Neural Networks** - Complex patterns, images, text

But start here! Linear regression teaches fundamentals used everywhere in ML.

## Appendix: Library Tutorials

New to Python data science libraries? See **[APPENDIX_LIBRARIES.md](./APPENDIX_LIBRARIES.md)** for detailed tutorials on:

| Library | What It Does | Key Functions |
|---------|--------------|---------------|
| **pandas** | Data manipulation | `read_csv`, `DataFrame`, `groupby` |
| **numpy** | Numerical computing | `array`, `mean`, `sqrt`, `reshape` |
| **scikit-learn** | Machine learning | `train_test_split`, `fit`, `predict` |
| **matplotlib** | Visualization | `plot`, `scatter`, `hist`, `savefig` |
| **scipy** | Statistical tests | `shapiro`, `ttest_ind`, `pearsonr` |

Each library section includes:
- Installation instructions
- Core concepts explained
- Common operations with examples
- Quick reference card
