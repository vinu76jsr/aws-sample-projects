"""
Multiple Linear Regression - Multiple Features
===============================================
Predicting house price based on ALL features.

Formula: price = b0 + b1*size + b2*bedrooms + b3*age + b4*distance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load data
df = pd.read_csv('housing_data.csv')

# Multiple features
X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Model parameters
print("="*60)
print("MULTIPLE LINEAR REGRESSION RESULTS")
print("="*60)

print("\nFeature Coefficients:")
print("-" * 40)
for feature, coef in zip(X.columns, model.coef_):
    print(f"  {feature:20s}: {coef:>10.4f}")
print(f"  {'Intercept':20s}: {model.intercept_:>10.4f}")

# Interpretation
print("\n" + "="*60)
print("COEFFICIENT INTERPRETATION")
print("="*60)
print("""
Each coefficient shows the effect on price when that feature
increases by 1 unit, holding all other features constant:
""")
for feature, coef in zip(X.columns, model.coef_):
    direction = "increases" if coef > 0 else "decreases"
    print(f"  • {feature}: price {direction} by {abs(coef):.2f} lakhs per unit")

# Predictions and evaluation
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

# Compare actual vs predicted
print("\n" + "="*60)
print("ACTUAL VS PREDICTED (Test Set)")
print("="*60)
comparison = pd.DataFrame({
    'Actual': y_test.values,
    'Predicted': y_pred.round(2),
    'Error': (y_test.values - y_pred).round(2)
})
print(comparison.to_string(index=False))

# Predict for new house
print("\n" + "="*60)
print("PREDICTION EXAMPLE")
print("="*60)
new_house = {
    'size_sqft': 2000,
    'bedrooms': 3,
    'age_years': 5,
    'distance_city_km': 10
}
new_house_df = pd.DataFrame([new_house])
predicted_price = model.predict(new_house_df)[0]

print(f"New house features:")
for key, value in new_house.items():
    print(f"  • {key}: {value}")
print(f"\nPredicted price: {predicted_price:.2f} lakhs")

# Visualize actual vs predicted
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, color='blue', alpha=0.7)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', linewidth=2, label='Perfect prediction')
plt.xlabel('Actual Price (lakhs)')
plt.ylabel('Predicted Price (lakhs)')
plt.title('Multiple Regression: Actual vs Predicted Prices')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('02_multiple_regression_plot.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nPlot saved as '02_multiple_regression_plot.png'")
