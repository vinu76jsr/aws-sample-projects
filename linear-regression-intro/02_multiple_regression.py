"""
Multiple Linear Regression - Multiple Features
===============================================
Predicting house price based on ALL features.

WHAT YOU'LL LEARN:
- How to use multiple features for prediction
- How to interpret multiple coefficients
- How each feature contributes to the prediction
- Comparing actual vs predicted values

FORMULA: price = b0 + b1*size + b2*bedrooms + b3*age + b4*distance

DIFFERENCE FROM SIMPLE REGRESSION:
- Simple: One input variable (size only)
- Multiple: Many input variables (size, bedrooms, age, distance)
- More features often = better predictions (but not always!)
"""

# ============================================================
# IMPORT LIBRARIES
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv('housing_data.csv')

# ============================================================
# PREPARE FEATURES AND TARGET
# ============================================================
# This time, X has 4 columns (4 features) instead of just 1
# Each feature provides different information about the house
X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

# ============================================================
# SPLIT DATA
# ============================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================================
# TRAIN MODEL
# ============================================================
# The same LinearRegression works for any number of features!
# It automatically adjusts to handle multiple inputs
model = LinearRegression()
model.fit(X_train, y_train)

# ============================================================
# EXAMINE THE LEARNED FORMULA
# ============================================================
print("="*60)
print("MULTIPLE LINEAR REGRESSION RESULTS")
print("="*60)

# With multiple features, we get multiple coefficients
# model.coef_ is now an array with one value per feature
print("\nFeature Coefficients:")
print("-" * 40)

# zip() pairs each feature name with its coefficient
for feature, coef in zip(X.columns, model.coef_):
    print(f"  {feature:20s}: {coef:>10.4f}")

# Intercept is still a single number
print(f"  {'Intercept':20s}: {model.intercept_:>10.4f}")

# ============================================================
# INTERPRET THE COEFFICIENTS
# ============================================================
print("\n" + "="*60)
print("COEFFICIENT INTERPRETATION")
print("="*60)
print("""
Each coefficient shows the effect on price when that feature
increases by 1 unit, holding all other features constant:
""")

# Positive coefficient = price increases as feature increases
# Negative coefficient = price decreases as feature increases
for feature, coef in zip(X.columns, model.coef_):
    direction = "increases" if coef > 0 else "decreases"
    print(f"  • {feature}: price {direction} by {abs(coef):.2f} lakhs per unit")

# EXAMPLE:
# - size_sqft: +0.04 means each extra sqft adds 0.04 lakhs
# - age_years: -0.80 means each year older subtracts 0.80 lakhs

# ============================================================
# MAKE PREDICTIONS AND EVALUATE
# ============================================================
y_pred = model.predict(X_test)

print("\n" + "="*60)
print("MODEL EVALUATION")
print("="*60)

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Root Mean Squared Error: {rmse:.2f} lakhs")
print(f"R² Score: {r2:.4f}")
print(f"\nModel explains {r2*100:.1f}% of price variance")

# ============================================================
# COMPARE ACTUAL VS PREDICTED
# ============================================================
print("\n" + "="*60)
print("ACTUAL VS PREDICTED (Test Set)")
print("="*60)

# Create a comparison table
# This helps visualize where predictions are good or bad
comparison = pd.DataFrame({
    'Actual': y_test.values,
    'Predicted': y_pred.round(2),
    'Error': (y_test.values - y_pred).round(2)
})
print(comparison.to_string(index=False))

# ============================================================
# PREDICT FOR A NEW HOUSE
# ============================================================
print("\n" + "="*60)
print("PREDICTION EXAMPLE")
print("="*60)

# Define a new house with all 4 features
new_house = {
    'size_sqft': 2000,
    'bedrooms': 3,
    'age_years': 5,
    'distance_city_km': 10
}

# Convert dictionary to DataFrame (model expects DataFrame-like input)
new_house_df = pd.DataFrame([new_house])
predicted_price = model.predict(new_house_df)[0]

print(f"New house features:")
for key, value in new_house.items():
    print(f"  • {key}: {value}")
print(f"\nPredicted price: {predicted_price:.2f} lakhs")

# ============================================================
# VISUALIZE: ACTUAL VS PREDICTED PLOT
# ============================================================
# This is a common way to visualize regression performance
# Perfect predictions would fall exactly on the diagonal line

plt.figure(figsize=(10, 6))

# Plot actual vs predicted as points
plt.scatter(y_test, y_pred, color='blue', alpha=0.7)

# Draw the "perfect prediction" line
# If predicted = actual, points would be on this line
plt.plot(
    [y.min(), y.max()],  # X coordinates: from min to max
    [y.min(), y.max()],  # Y coordinates: same (diagonal)
    'r--',                # Red dashed line
    linewidth=2,
    label='Perfect prediction'
)

plt.xlabel('Actual Price (lakhs)')
plt.ylabel('Predicted Price (lakhs)')
plt.title('Multiple Regression: Actual vs Predicted Prices')
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig('02_multiple_regression_plot.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nPlot saved as '02_multiple_regression_plot.png'")
