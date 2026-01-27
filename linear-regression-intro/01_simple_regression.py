"""
Simple Linear Regression - One Feature
=======================================
Predicting house price based on size only.

WHAT YOU'LL LEARN:
- How to load and explore data with pandas
- How to split data into training and testing sets
- How to train a linear regression model
- How to interpret the model's formula
- How to evaluate model performance

FORMULA: price = m * size + b
WHERE:
  - m = slope (how much price changes per sqft)
  - b = intercept (base price when size = 0)
"""

# ============================================================
# STEP 1: IMPORT LIBRARIES
# ============================================================
# pandas: For loading and manipulating data (like Excel for Python)
import pandas as pd

# numpy: For mathematical operations (sqrt, arrays, etc.)
import numpy as np

# matplotlib: For creating charts and visualizations
import matplotlib.pyplot as plt

# sklearn (scikit-learn): The main machine learning library
# - LinearRegression: The algorithm we're using
# - train_test_split: Splits data into training and testing sets
# - mean_squared_error, r2_score: Metrics to evaluate our model
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# ============================================================
# STEP 2: LOAD AND EXPLORE DATA
# ============================================================
# pd.read_csv() reads a CSV file into a DataFrame (a table)
# Think of a DataFrame as a spreadsheet with rows and columns
df = pd.read_csv('housing_data.csv')

# .shape tells us (number of rows, number of columns)
print("Dataset shape:", df.shape)

# .head() shows the first 5 rows - good for quick inspection
print("\nFirst 5 rows:")
print(df.head())

# ============================================================
# STEP 3: PREPARE FEATURES AND TARGET
# ============================================================
# In ML, we separate:
# - X (features/inputs): What we use to make predictions
# - y (target/output): What we're trying to predict

# X must be a 2D array (rows × columns), even with one feature
# Double brackets [[]] create a DataFrame, single [] creates a Series
X = df[['size_sqft']]  # Feature: house size (2D: 25 rows × 1 column)
y = df['price_lakhs']   # Target: house price (1D: 25 values)

# ============================================================
# STEP 4: SPLIT INTO TRAINING AND TESTING SETS
# ============================================================
# WHY SPLIT?
# - Training set: Model learns patterns from this data
# - Testing set: We check if the model learned correctly on NEW data
# - If we tested on training data, we'd just be checking memorization

# train_test_split randomly divides our data
# - test_size=0.2 means 20% for testing, 80% for training
# - random_state=42 is a "seed" - same number = same split every time
#   (42 is just a convention, any number works)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# len() tells us how many samples in each set
print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# ============================================================
# STEP 5: CREATE AND TRAIN THE MODEL
# ============================================================
# LinearRegression() creates an empty model (no formula yet)
model = LinearRegression()

# .fit() is where the LEARNING happens!
# - The model looks at all training examples
# - It finds the best slope (m) and intercept (b)
# - "Best" means the line that minimizes prediction errors
model.fit(X_train, y_train)

# ============================================================
# STEP 6: EXAMINE THE LEARNED FORMULA
# ============================================================
print("\n" + "="*50)
print("MODEL PARAMETERS")
print("="*50)

# model.coef_ contains the slope(s) - one per feature
# Since we have one feature, we get one coefficient
print(f"Slope (coefficient): {model.coef_[0]:.4f}")

# model.intercept_ is the y-intercept (value when x=0)
print(f"Intercept: {model.intercept_:.4f}")

# The complete formula
print(f"\nEquation: price = {model.coef_[0]:.4f} * size + {model.intercept_:.4f}")

# INTERPRETING THE SLOPE:
# - If slope = 0.035, then for every 1 sqft increase, price goes up by 0.035 lakhs
# - For 100 sqft increase: 0.035 × 100 = 3.5 lakhs increase
print(f"\nInterpretation:")
print(f"  For every 1 sqft increase, price increases by {model.coef_[0]:.2f} lakhs")
print(f"  For every 100 sqft increase, price increases by {model.coef_[0]*100:.2f} lakhs")

# ============================================================
# STEP 7: MAKE PREDICTIONS
# ============================================================
# .predict() uses the formula to estimate prices for test data
# The model has NEVER seen X_test before - this is a true test
y_pred = model.predict(X_test)

# ============================================================
# STEP 8: EVALUATE MODEL PERFORMANCE
# ============================================================
print("\n" + "="*50)
print("MODEL EVALUATION")
print("="*50)

# MEAN SQUARED ERROR (MSE):
# - Average of (actual - predicted)² for all test samples
# - Squaring penalizes big errors more than small ones
# - Lower is better
mse = mean_squared_error(y_test, y_pred)

# ROOT MEAN SQUARED ERROR (RMSE):
# - Square root of MSE
# - Same units as target (lakhs), so easier to interpret
# - "On average, predictions are off by X lakhs"
rmse = np.sqrt(mse)

# R² SCORE (R-SQUARED):
# - Measures how much of the variance in prices is explained by size
# - Ranges from 0 to 1 (can be negative for very bad models)
# - 0.8 means "size explains 80% of price variation"
# - Higher is better
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root MSE (RMSE): {rmse:.2f} lakhs")
print(f"R² Score: {r2:.4f}")
print(f"\nR² Interpretation: Model explains {r2*100:.1f}% of price variance")

# ============================================================
# STEP 9: PREDICT FOR A NEW HOUSE
# ============================================================
print("\n" + "="*50)
print("PREDICTION EXAMPLE")
print("="*50)

new_size = 1800

# Note: predict() expects 2D array, so we use [[value]]
predicted_price = model.predict([[new_size]])[0]
print(f"For a {new_size} sqft house:")
print(f"  Predicted price: {predicted_price:.2f} lakhs")

# ============================================================
# STEP 10: VISUALIZE THE RESULTS
# ============================================================
# Create figure with specific size (width, height in inches)
plt.figure(figsize=(10, 6))

# Plot training data as blue dots
# alpha=0.6 makes points slightly transparent
plt.scatter(X_train, y_train, color='blue', alpha=0.6, label='Training data')

# Plot test data as green dots
plt.scatter(X_test, y_test, color='green', alpha=0.6, label='Test data')

# Draw the regression line
# np.linspace creates 100 evenly spaced points from min to max
# reshape(-1, 1) converts to 2D array (required by predict)
X_line = np.linspace(X['size_sqft'].min(), X['size_sqft'].max(), 100).reshape(-1, 1)
y_line = model.predict(X_line)
plt.plot(X_line, y_line, color='red', linewidth=2, label='Regression line')

# Add labels and title
plt.xlabel('Size (sqft)')
plt.ylabel('Price (lakhs)')
plt.title('Simple Linear Regression: House Price vs Size')

# Add legend to identify what each color means
plt.legend()

# Add grid for easier reading
plt.grid(True, alpha=0.3)

# Save the plot as an image file
# dpi=150 means 150 dots per inch (good quality)
# bbox_inches='tight' removes extra whitespace
plt.savefig('01_simple_regression_plot.png', dpi=150, bbox_inches='tight')

# Display the plot
plt.show()

print("\nPlot saved as '01_simple_regression_plot.png'")
