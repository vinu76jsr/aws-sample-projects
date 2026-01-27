"""
Feature Scaling and Preprocessing
=================================
Why scaling matters and how to do it properly.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import r2_score

# Load data
df = pd.read_csv('housing_data.csv')

X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

# Show the problem: features have different scales
print("="*60)
print("THE SCALING PROBLEM")
print("="*60)
print("\nFeature ranges (before scaling):")
print("-" * 40)
for col in X.columns:
    print(f"  {col:20s}: {X[col].min():>6.0f} to {X[col].max():>6.0f}")

print("""
Problem: size_sqft ranges 1100-2500, but bedrooms ranges 2-5.
The model might give more weight to features with larger values.
Solution: Scale all features to similar ranges.
""")

# Split data FIRST (important: fit scaler only on training data)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================================
# Method 1: StandardScaler (Z-score normalization)
# ============================================================
print("="*60)
print("METHOD 1: StandardScaler (Z-score)")
print("="*60)
print("Formula: z = (x - mean) / std_dev")
print("Result: mean=0, std=1 for each feature\n")

scaler_standard = StandardScaler()
X_train_scaled = scaler_standard.fit_transform(X_train)  # Fit AND transform
X_test_scaled = scaler_standard.transform(X_test)        # Only transform!

print("After StandardScaler (training set):")
print("-" * 40)
X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X.columns)
for col in X_train_scaled_df.columns:
    print(f"  {col:20s}: mean={X_train_scaled_df[col].mean():>6.2f}, std={X_train_scaled_df[col].std():>5.2f}")

# Train model with scaled data
model_scaled = LinearRegression()
model_scaled.fit(X_train_scaled, y_train)
y_pred_scaled = model_scaled.predict(X_test_scaled)
r2_scaled = r2_score(y_test, y_pred_scaled)

print(f"\nR² with StandardScaler: {r2_scaled:.4f}")

# ============================================================
# Method 2: MinMaxScaler (0-1 normalization)
# ============================================================
print("\n" + "="*60)
print("METHOD 2: MinMaxScaler (0-1 range)")
print("="*60)
print("Formula: x_scaled = (x - min) / (max - min)")
print("Result: all values between 0 and 1\n")

scaler_minmax = MinMaxScaler()
X_train_minmax = scaler_minmax.fit_transform(X_train)
X_test_minmax = scaler_minmax.transform(X_test)

print("After MinMaxScaler (training set):")
print("-" * 40)
X_train_minmax_df = pd.DataFrame(X_train_minmax, columns=X.columns)
for col in X_train_minmax_df.columns:
    print(f"  {col:20s}: min={X_train_minmax_df[col].min():>5.2f}, max={X_train_minmax_df[col].max():>5.2f}")

model_minmax = LinearRegression()
model_minmax.fit(X_train_minmax, y_train)
y_pred_minmax = model_minmax.predict(X_test_minmax)
r2_minmax = r2_score(y_test, y_pred_minmax)

print(f"\nR² with MinMaxScaler: {r2_minmax:.4f}")

# ============================================================
# Compare with no scaling
# ============================================================
print("\n" + "="*60)
print("COMPARISON: Scaling Impact")
print("="*60)

model_noscale = LinearRegression()
model_noscale.fit(X_train, y_train)
y_pred_noscale = model_noscale.predict(X_test)
r2_noscale = r2_score(y_test, y_pred_noscale)

print(f"\nR² Scores:")
print(f"  No scaling:      {r2_noscale:.4f}")
print(f"  StandardScaler:  {r2_scaled:.4f}")
print(f"  MinMaxScaler:    {r2_minmax:.4f}")

print("""
Note: For Linear Regression, scaling doesn't change R² much
because LR is scale-invariant. However, scaling is CRITICAL for:
  • Gradient Descent optimization (faster convergence)
  • Regularized models (Ridge, Lasso)
  • Neural networks
  • Comparing coefficient importance
""")

# ============================================================
# Coefficient comparison after scaling
# ============================================================
print("="*60)
print("FEATURE IMPORTANCE (Scaled Coefficients)")
print("="*60)
print("\nWith StandardScaler, coefficients show relative importance:")
print("-" * 40)

importance = pd.DataFrame({
    'Feature': X.columns,
    'Coefficient': model_scaled.coef_,
    'Abs_Coefficient': np.abs(model_scaled.coef_)
}).sort_values('Abs_Coefficient', ascending=False)

for _, row in importance.iterrows():
    bar = '█' * int(row['Abs_Coefficient'] * 2)
    print(f"  {row['Feature']:20s}: {row['Coefficient']:>7.2f}  {bar}")

print("\nLarger absolute coefficient = more important feature")
