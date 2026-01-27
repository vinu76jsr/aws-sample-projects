"""
Regularization: Ridge and Lasso Regression
==========================================
Prevent overfitting by penalizing large coefficients.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

# Load data
df = pd.read_csv('housing_data.csv')

X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features (important for regularization!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("="*60)
print("REGULARIZATION: Ridge, Lasso, ElasticNet")
print("="*60)

print("""
Why Regularization?
-------------------
Prevents overfitting by adding a penalty for large coefficients:

• Ridge (L2): penalty = α * Σ(coefficient²)
  - Shrinks coefficients toward zero
  - Keeps all features

• Lasso (L1): penalty = α * Σ|coefficient|
  - Can shrink coefficients to exactly zero
  - Performs feature selection

• ElasticNet: Combines both L1 and L2 penalties
""")

# ============================================================
# Compare models
# ============================================================
models = {
    'Linear Regression': LinearRegression(),
    'Ridge (α=1.0)': Ridge(alpha=1.0),
    'Ridge (α=10.0)': Ridge(alpha=10.0),
    'Lasso (α=1.0)': Lasso(alpha=1.0),
    'Lasso (α=0.1)': Lasso(alpha=0.1),
    'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5)
}

print("\n" + "="*60)
print("MODEL COMPARISON")
print("="*60)
print(f"\n{'Model':<25} {'R² Score':<12} {'RMSE':<10}")
print("-" * 50)

results = []
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    results.append({'name': name, 'r2': r2, 'rmse': rmse, 'model': model})
    print(f"{name:<25} {r2:<12.4f} {rmse:<10.2f}")

# ============================================================
# Coefficient comparison
# ============================================================
print("\n" + "="*60)
print("COEFFICIENT COMPARISON")
print("="*60)

coef_df = pd.DataFrame({'Feature': X.columns})
for result in results:
    coef_df[result['name']] = result['model'].coef_

print("\n" + coef_df.to_string(index=False))

print("""
Observations:
• Ridge shrinks coefficients but keeps all non-zero
• Lasso can eliminate features (coefficients become 0)
• Higher α = more regularization = smaller coefficients
""")

# ============================================================
# Find optimal alpha using cross-validation
# ============================================================
print("\n" + "="*60)
print("FINDING OPTIMAL ALPHA (Cross-Validation)")
print("="*60)

alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
ridge_scores = []
lasso_scores = []

for alpha in alphas:
    # Ridge CV
    ridge = Ridge(alpha=alpha)
    ridge_cv = cross_val_score(ridge, X_train_scaled, y_train, cv=5, scoring='r2')
    ridge_scores.append(ridge_cv.mean())

    # Lasso CV
    lasso = Lasso(alpha=alpha)
    lasso_cv = cross_val_score(lasso, X_train_scaled, y_train, cv=5, scoring='r2')
    lasso_scores.append(lasso_cv.mean())

print(f"\n{'Alpha':<10} {'Ridge R²':<15} {'Lasso R²':<15}")
print("-" * 40)
for i, alpha in enumerate(alphas):
    print(f"{alpha:<10} {ridge_scores[i]:<15.4f} {lasso_scores[i]:<15.4f}")

best_ridge_alpha = alphas[np.argmax(ridge_scores)]
best_lasso_alpha = alphas[np.argmax(lasso_scores)]
print(f"\nBest Ridge α: {best_ridge_alpha}")
print(f"Best Lasso α: {best_lasso_alpha}")

# ============================================================
# Visualize
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Alpha vs R² Score
ax1 = axes[0]
ax1.plot(alphas, ridge_scores, 'b-o', label='Ridge')
ax1.plot(alphas, lasso_scores, 'r-o', label='Lasso')
ax1.set_xscale('log')
ax1.set_xlabel('Alpha (log scale)')
ax1.set_ylabel('R² Score (CV)')
ax1.set_title('Effect of Alpha on Model Performance')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Coefficient paths
ax2 = axes[1]
alphas_fine = np.logspace(-3, 2, 50)
ridge_coefs = []

for alpha in alphas_fine:
    ridge = Ridge(alpha=alpha)
    ridge.fit(X_train_scaled, y_train)
    ridge_coefs.append(ridge.coef_)

ridge_coefs = np.array(ridge_coefs)

for i, feature in enumerate(X.columns):
    ax2.plot(alphas_fine, ridge_coefs[:, i], label=feature)

ax2.set_xscale('log')
ax2.set_xlabel('Alpha (log scale)')
ax2.set_ylabel('Coefficient Value')
ax2.set_title('Ridge: Coefficient Shrinkage as Alpha Increases')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('05_regularization_plot.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nPlot saved as '05_regularization_plot.png'")

print("\n" + "="*60)
print("WHEN TO USE WHICH?")
print("="*60)
print("""
• Linear Regression: Small dataset, no overfitting
• Ridge: Many features, all potentially useful
• Lasso: Want automatic feature selection
• ElasticNet: Many correlated features
""")
