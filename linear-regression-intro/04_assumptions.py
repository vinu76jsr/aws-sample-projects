"""
Linear Regression Assumptions
=============================
Check if your data meets the assumptions for linear regression.

WHAT YOU'LL LEARN:
- The 4 key assumptions of linear regression
- How to check each assumption visually and statistically
- What to do if assumptions are violated

WHY ASSUMPTIONS MATTER:
Linear regression works best when certain conditions are met.
If assumptions are violated, predictions may be unreliable.

THE 4 ASSUMPTIONS:
1. Linearity - Relationship between X and y is linear
2. Normality - Residuals (errors) are normally distributed
3. Homoscedasticity - Residual variance is constant
4. No Multicollinearity - Features aren't highly correlated
"""

# ============================================================
# IMPORT LIBRARIES
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# scipy.stats provides statistical tests
# - shapiro: Tests if data is normally distributed
from scipy import stats

# ============================================================
# LOAD AND PREPARE DATA
# ============================================================
df = pd.read_csv('housing_data.csv')

X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# ============================================================
# CALCULATE RESIDUALS
# ============================================================
# RESIDUALS = Actual values - Predicted values
# They represent the "errors" or what the model didn't capture
# We analyze residuals to check if assumptions are met

y_pred = model.predict(X_train)
residuals = y_train - y_pred

print("="*60)
print("LINEAR REGRESSION ASSUMPTIONS")
print("="*60)

# Create a 2x2 grid of plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# ============================================================
# ASSUMPTION 1: LINEARITY
# ============================================================
print("\n1. LINEARITY")
print("-" * 40)
print("Assumption: Relationship between X and y is linear")
print("Check: Residuals vs Fitted plot should show no pattern")
print("""
WHAT TO LOOK FOR:
  ✓ Good: Points randomly scattered around zero
  ✗ Bad: Curved pattern, funnel shape, or clusters

If you see a curved pattern, try:
  - Adding polynomial features (x², x³)
  - Using a non-linear model
""")

# Plot: Residuals vs Fitted Values
ax1 = axes[0, 0]
ax1.scatter(y_pred, residuals, alpha=0.6)
ax1.axhline(y=0, color='r', linestyle='--')  # Reference line at y=0
ax1.set_xlabel('Fitted Values (Predictions)')
ax1.set_ylabel('Residuals (Errors)')
ax1.set_title('1. Linearity Check: Residuals vs Fitted')
ax1.grid(True, alpha=0.3)

# ============================================================
# ASSUMPTION 2: NORMALITY OF RESIDUALS
# ============================================================
print("\n2. NORMALITY OF RESIDUALS")
print("-" * 40)
print("Assumption: Residuals are normally distributed")
print("Check: Histogram should be bell-shaped, Q-Q plot should be linear")

# SHAPIRO-WILK TEST:
# - Tests the null hypothesis that data is normally distributed
# - If p-value > 0.05: Data appears normal
# - If p-value < 0.05: Data is NOT normal
stat, p_value = stats.shapiro(residuals)
print(f"\nShapiro-Wilk test:")
print(f"  Statistic: {stat:.4f}")
print(f"  P-value: {p_value:.4f}")

if p_value > 0.05:
    print("  Result: ✓ Residuals appear normal (p > 0.05)")
else:
    print("  Result: ✗ Residuals may not be normal (p < 0.05)")

print("""
If residuals aren't normal:
  - May need larger sample size
  - Try transforming the target (log, sqrt)
  - Consider robust regression methods
""")

# Plot: Histogram of Residuals
ax2 = axes[0, 1]
ax2.hist(residuals, bins=10, edgecolor='black', alpha=0.7)
ax2.set_xlabel('Residuals')
ax2.set_ylabel('Frequency')
ax2.set_title('2. Normality Check: Histogram of Residuals')
ax2.grid(True, alpha=0.3)

# ============================================================
# ASSUMPTION 3: HOMOSCEDASTICITY (CONSTANT VARIANCE)
# ============================================================
print("\n3. HOMOSCEDASTICITY (Constant Variance)")
print("-" * 40)
print("Assumption: Residual variance is constant across all X values")
print("Check: Residuals vs Fitted should have constant spread")
print("""
WHAT TO LOOK FOR:
  ✓ Good: Even spread of points across all fitted values
  ✗ Bad: Funnel shape (spread increases or decreases)

Funnel shape = "Heteroscedasticity"
If present, try:
  - Log transform the target
  - Weighted least squares
  - Robust standard errors
""")

# Plot: Absolute Residuals vs Fitted
# We use absolute values to see if spread changes
ax3 = axes[1, 0]
ax3.scatter(y_pred, np.abs(residuals), alpha=0.6)
ax3.set_xlabel('Fitted Values (Predictions)')
ax3.set_ylabel('Absolute Residuals')
ax3.set_title('3. Homoscedasticity Check: |Residuals| vs Fitted')
ax3.grid(True, alpha=0.3)

# ============================================================
# ASSUMPTION 4: NO MULTICOLLINEARITY
# ============================================================
print("\n4. NO MULTICOLLINEARITY")
print("-" * 40)
print("Assumption: Features are not highly correlated with each other")
print("Check: Correlation matrix - values > 0.8 are problematic")

# CORRELATION MATRIX:
# Shows how strongly each pair of features is related
# Values range from -1 to +1:
#   +1: Perfect positive correlation (as X goes up, Y goes up)
#   -1: Perfect negative correlation (as X goes up, Y goes down)
#    0: No correlation
correlation_matrix = X.corr()

print("\nCorrelation Matrix:")
print(correlation_matrix.round(2).to_string())

# Find problematic correlations
print("\nHigh correlations (|r| > 0.7):")
high_corr_found = False
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        corr = correlation_matrix.iloc[i, j]
        if abs(corr) > 0.7:
            print(f"  ⚠ {correlation_matrix.columns[i]} & {correlation_matrix.columns[j]}: {corr:.2f}")
            high_corr_found = True

if not high_corr_found:
    print("  ✓ None found - good!")

print("""
If multicollinearity is present:
  - Remove one of the correlated features
  - Use Ridge regression (handles multicollinearity)
  - Create a combined feature (PCA)
""")

# Plot: Correlation Heatmap
ax4 = axes[1, 1]
im = ax4.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
ax4.set_xticks(range(len(X.columns)))
ax4.set_yticks(range(len(X.columns)))
ax4.set_xticklabels(X.columns, rotation=45, ha='right')
ax4.set_yticklabels(X.columns)
ax4.set_title('4. Multicollinearity Check: Correlation Matrix')
plt.colorbar(im, ax=ax4)

# Add correlation values to heatmap cells
for i in range(len(X.columns)):
    for j in range(len(X.columns)):
        ax4.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                ha='center', va='center', fontsize=9)

# Adjust layout to prevent overlap
plt.tight_layout()
plt.savefig('04_assumptions_plot.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("SUMMARY: WHAT TO DO IF ASSUMPTIONS FAIL")
print("="*60)
print("""
┌─────────────────────┬────────────────────────────────────────┐
│ Assumption Failed   │ What To Do                             │
├─────────────────────┼────────────────────────────────────────┤
│ Non-linearity       │ Add polynomial features, use tree      │
│                     │ models, or other non-linear models     │
├─────────────────────┼────────────────────────────────────────┤
│ Non-normal residuals│ Larger sample, transform target,       │
│                     │ or use robust regression               │
├─────────────────────┼────────────────────────────────────────┤
│ Heteroscedasticity  │ Log transform target, weighted         │
│                     │ least squares, robust standard errors  │
├─────────────────────┼────────────────────────────────────────┤
│ Multicollinearity   │ Remove correlated features, use        │
│                     │ Ridge/Lasso, or apply PCA              │
└─────────────────────┴────────────────────────────────────────┘
""")

print("Plot saved as '04_assumptions_plot.png'")
