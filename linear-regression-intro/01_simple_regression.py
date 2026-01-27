"""
Simple Linear Regression - One Feature
=======================================
Predicting house price based on size only.

Formula: price = m * size + b
Where:
  - m = slope (how much price changes per sqft)
  - b = intercept (base price when size = 0)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load data
df = pd.read_csv('housing_data.csv')
print("Dataset shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

# Simple regression: price vs size only
X = df[['size_sqft']]  # Feature (must be 2D array)
y = df['price_lakhs']   # Target

# Split data: 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# Create and train model
model = LinearRegression()
model.fit(X_train, y_train)

# Model parameters
print("\n" + "="*50)
print("MODEL PARAMETERS")
print("="*50)
print(f"Slope (coefficient): {model.coef_[0]:.4f}")
print(f"Intercept: {model.intercept_:.4f}")
print(f"\nEquation: price = {model.coef_[0]:.4f} * size + {model.intercept_:.4f}")

# Interpretation
print(f"\nInterpretation:")
print(f"  For every 1 sqft increase, price increases by {model.coef_[0]:.2f} lakhs")
print(f"  For every 100 sqft increase, price increases by {model.coef_[0]*100:.2f} lakhs")

# Make predictions
y_pred = model.predict(X_test)

# Evaluate model
print("\n" + "="*50)
print("MODEL EVALUATION")
print("="*50)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root MSE (RMSE): {rmse:.2f} lakhs")
print(f"R² Score: {r2:.4f}")
print(f"\nR² Interpretation: Model explains {r2*100:.1f}% of price variance")

# Predict for new house
print("\n" + "="*50)
print("PREDICTION EXAMPLE")
print("="*50)
new_size = 1800
predicted_price = model.predict([[new_size]])[0]
print(f"For a {new_size} sqft house:")
print(f"  Predicted price: {predicted_price:.2f} lakhs")

# Visualize
plt.figure(figsize=(10, 6))
plt.scatter(X_train, y_train, color='blue', alpha=0.6, label='Training data')
plt.scatter(X_test, y_test, color='green', alpha=0.6, label='Test data')

# Plot regression line
X_line = np.linspace(X['size_sqft'].min(), X['size_sqft'].max(), 100).reshape(-1, 1)
y_line = model.predict(X_line)
plt.plot(X_line, y_line, color='red', linewidth=2, label='Regression line')

plt.xlabel('Size (sqft)')
plt.ylabel('Price (lakhs)')
plt.title('Simple Linear Regression: House Price vs Size')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('01_simple_regression_plot.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nPlot saved as '01_simple_regression_plot.png'")
