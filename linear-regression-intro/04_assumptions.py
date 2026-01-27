"""
Linear Regression Assumptions
=============================
Check if your data meets the assumptions for linear regression.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from scipy import stats

# Load data
df = pd.read_csv('housing_data.csv')

X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_train)
residuals = y_train - y_pred

print("="*60)
print("LINEAR REGRESSION ASSUMPTIONS")
print("="*60)

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# ============================================================
# Assumption 1: Linearity
# ============================================================
print("\n1. LINEARITY")
print("-" * 40)
print("Assumption: Relationship between X and y is linear")
print("Check: Residuals vs Fitted plot should show no pattern")

ax1 = axes[0, 0]
ax1.scatter(y_pred, residuals, alpha=0.6)
ax1.axhline(y=0, color='r', linestyle='--')
ax1.set_xlabel('Fitted Values')
ax1.set_ylabel('Residuals')
ax1.set_title('1. Linearity Check: Residuals vs Fitted')
ax1.grid(True, alpha=0.3)

# ============================================================
# Assumption 2: Normality of Residuals
# ============================================================
print("\n2. NORMALITY OF RESIDUALS")
print("-" * 40)
print("Assumption: Residuals are normally distributed")
print("Check: Histogram should be bell-shaped, Q-Q plot should be linear")

# Shapiro-Wilk test
stat, p_value = stats.shapiro(residuals)
print(f"Shapiro-Wilk test: statistic={stat:.4f}, p-value={p_value:.4f}")
if p_value > 0.05:
    print("Result: Residuals appear normal (p > 0.05)")
else:
    print("Result: Residuals may not be normal (p < 0.05)")

ax2 = axes[0, 1]
ax2.hist(residuals, bins=10, edgecolor='black', alpha=0.7)
ax2.set_xlabel('Residuals')
ax2.set_ylabel('Frequency')
ax2.set_title('2. Normality Check: Histogram of Residuals')
ax2.grid(True, alpha=0.3)

# ============================================================
# Assumption 3: Homoscedasticity (Constant Variance)
# ============================================================
print("\n3. HOMOSCEDASTICITY (Constant Variance)")
print("-" * 40)
print("Assumption: Residual variance is constant across all X values")
print("Check: Residuals vs Fitted should have constant spread")

ax3 = axes[1, 0]
ax3.scatter(y_pred, np.abs(residuals), alpha=0.6)
ax3.set_xlabel('Fitted Values')
ax3.set_ylabel('Absolute Residuals')
ax3.set_title('3. Homoscedasticity Check: |Residuals| vs Fitted')
ax3.grid(True, alpha=0.3)

# ============================================================
# Assumption 4: No Multicollinearity
# ============================================================
print("\n4. NO MULTICOLLINEARITY")
print("-" * 40)
print("Assumption: Features are not highly correlated with each other")
print("Check: Correlation matrix - values > 0.8 are problematic\n")

correlation_matrix = X.corr()
print("Correlation Matrix:")
print(correlation_matrix.round(2).to_string())

# Find high correlations
print("\nHigh correlations (|r| > 0.7):")
high_corr_found = False
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        corr = correlation_matrix.iloc[i, j]
        if abs(corr) > 0.7:
            print(f"  {correlation_matrix.columns[i]} & {correlation_matrix.columns[j]}: {corr:.2f}")
            high_corr_found = True
if not high_corr_found:
    print("  None found - good!")

ax4 = axes[1, 1]
im = ax4.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
ax4.set_xticks(range(len(X.columns)))
ax4.set_yticks(range(len(X.columns)))
ax4.set_xticklabels(X.columns, rotation=45, ha='right')
ax4.set_yticklabels(X.columns)
ax4.set_title('4. Multicollinearity Check: Correlation Matrix')
plt.colorbar(im, ax=ax4)

# Add correlation values to heatmap
for i in range(len(X.columns)):
    for j in range(len(X.columns)):
        ax4.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                ha='center', va='center', fontsize=9)

plt.tight_layout()
plt.savefig('04_assumptions_plot.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("""
If assumptions are violated:
• Non-linearity → Try polynomial features or other models
• Non-normal residuals → May need larger sample or transformation
• Heteroscedasticity → Try weighted least squares or log transform
• Multicollinearity → Remove correlated features or use Ridge regression
""")

print("Plot saved as '04_assumptions_plot.png'")
