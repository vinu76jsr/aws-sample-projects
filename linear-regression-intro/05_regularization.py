"""
Regularization: Ridge and Lasso Regression
==========================================
Prevent overfitting by penalizing large coefficients.

WHAT YOU'LL LEARN:
- What overfitting is and why it's a problem
- How regularization prevents overfitting
- The difference between Ridge (L2) and Lasso (L1)
- How to choose the right regularization strength (alpha)
- When to use each method

THE OVERFITTING PROBLEM:
Imagine a student who memorizes answers instead of learning concepts.
They score 100% on practice tests but fail on new questions.

In ML terms:
- Model fits training data too perfectly
- But performs poorly on new data
- It learned noise instead of patterns

REGULARIZATION SOLUTION:
Add a "penalty" for large coefficients.
This forces the model to find simpler patterns.
"""

# ============================================================
# IMPORT LIBRARIES
# ============================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# sklearn regression models:
# - LinearRegression: No regularization
# - Ridge: L2 penalty (shrinks coefficients)
# - Lasso: L1 penalty (can zero out coefficients)
# - ElasticNet: Combination of L1 and L2
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

# ============================================================
# LOAD AND PREPARE DATA
# ============================================================
df = pd.read_csv('housing_data.csv')

X = df[['size_sqft', 'bedrooms', 'age_years', 'distance_city_km']]
y = df['price_lakhs']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================================================
# SCALE FEATURES (IMPORTANT FOR REGULARIZATION!)
# ============================================================
# Regularization penalizes coefficient size
# If features have different scales, larger-scale features
# would be unfairly penalized more
# Scaling ensures fair comparison
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ============================================================
# EXPLAIN REGULARIZATION
# ============================================================
print("="*60)
print("REGULARIZATION: Ridge, Lasso, ElasticNet")
print("="*60)

print("""
┌─────────────────────────────────────────────────────────────┐
│                 WHY REGULARIZATION?                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Regular Linear Regression minimizes:                       │
│      Error = Σ(actual - predicted)²                        │
│                                                             │
│  Regularized Regression minimizes:                          │
│      Error = Σ(actual - predicted)² + α × penalty          │
│                                                             │
│  The penalty term discourages large coefficients,          │
│  forcing the model to find simpler patterns.               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  α (alpha) controls regularization strength:               │
│    • α = 0: No regularization (same as LinearRegression)   │
│    • α small: Weak regularization                          │
│    • α large: Strong regularization (simpler model)        │
└─────────────────────────────────────────────────────────────┘

THREE TYPES OF REGULARIZATION:

• RIDGE (L2): penalty = α × Σ(coefficient²)
  - Shrinks all coefficients toward zero
  - But never makes them exactly zero
  - Good when all features might be useful

• LASSO (L1): penalty = α × Σ|coefficient|
  - Can shrink coefficients to exactly zero
  - Effectively removes unimportant features
  - Good for feature selection

• ELASTICNET: penalty = α × (L1_ratio × L1 + (1-L1_ratio) × L2)
  - Combines both Ridge and Lasso
  - Best of both worlds
  - Good when features are correlated
""")

# ============================================================
# COMPARE DIFFERENT MODELS
# ============================================================
# Create a dictionary of models to compare
# Each model has different regularization settings
models = {
    'Linear Regression': LinearRegression(),
    'Ridge (α=1.0)': Ridge(alpha=1.0),
    'Ridge (α=10.0)': Ridge(alpha=10.0),
    'Lasso (α=1.0)': Lasso(alpha=1.0),
    'Lasso (α=0.1)': Lasso(alpha=0.1),
    'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5)  # 50% L1, 50% L2
}

print("\n" + "="*60)
print("MODEL COMPARISON")
print("="*60)
print(f"\n{'Model':<25} {'R² Score':<12} {'RMSE':<10}")
print("-" * 50)

results = []
for name, model in models.items():
    # Train
    model.fit(X_train_scaled, y_train)

    # Predict
    y_pred = model.predict(X_test_scaled)

    # Evaluate
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Store results
    results.append({'name': name, 'r2': r2, 'rmse': rmse, 'model': model})
    print(f"{name:<25} {r2:<12.4f} {rmse:<10.2f}")

# ============================================================
# COEFFICIENT COMPARISON
# ============================================================
print("\n" + "="*60)
print("COEFFICIENT COMPARISON")
print("="*60)
print("""
Notice how regularization affects coefficient sizes:
- Ridge shrinks coefficients but keeps all non-zero
- Lasso can make coefficients exactly zero (feature selection!)
- Higher α = more shrinkage
""")

# Create a DataFrame showing coefficients for each model
coef_df = pd.DataFrame({'Feature': X.columns})
for result in results:
    coef_df[result['name']] = result['model'].coef_

print("\n" + coef_df.to_string(index=False))

# ============================================================
# FINDING OPTIMAL ALPHA WITH CROSS-VALIDATION
# ============================================================
print("\n" + "="*60)
print("FINDING OPTIMAL ALPHA (Cross-Validation)")
print("="*60)
print("""
How do we choose the best α?
- Too small: Underfitting (not enough regularization)
- Too large: Overfitting (too much regularization)

Solution: Try different values and use cross-validation
to find which α gives the best performance on unseen data.
""")

# Test different alpha values
alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
ridge_scores = []
lasso_scores = []

for alpha in alphas:
    # CROSS-VALIDATION:
    # - Splits data into 5 parts
    # - Trains on 4 parts, tests on 1
    # - Repeats 5 times (each part gets to be test set)
    # - Returns average score across all 5 tests
    # This gives a more reliable estimate than a single train/test split

    # Ridge cross-validation
    ridge = Ridge(alpha=alpha)
    ridge_cv = cross_val_score(ridge, X_train_scaled, y_train, cv=5, scoring='r2')
    ridge_scores.append(ridge_cv.mean())

    # Lasso cross-validation
    lasso = Lasso(alpha=alpha)
    lasso_cv = cross_val_score(lasso, X_train_scaled, y_train, cv=5, scoring='r2')
    lasso_scores.append(lasso_cv.mean())

print(f"\n{'Alpha':<10} {'Ridge R²':<15} {'Lasso R²':<15}")
print("-" * 40)
for i, alpha in enumerate(alphas):
    print(f"{alpha:<10} {ridge_scores[i]:<15.4f} {lasso_scores[i]:<15.4f}")

# Find best alpha (highest R² score)
best_ridge_alpha = alphas[np.argmax(ridge_scores)]
best_lasso_alpha = alphas[np.argmax(lasso_scores)]
print(f"\nBest Ridge α: {best_ridge_alpha}")
print(f"Best Lasso α: {best_lasso_alpha}")

# ============================================================
# VISUALIZE
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Alpha vs R² Score
ax1 = axes[0]
ax1.plot(alphas, ridge_scores, 'b-o', label='Ridge', linewidth=2, markersize=8)
ax1.plot(alphas, lasso_scores, 'r-o', label='Lasso', linewidth=2, markersize=8)
ax1.set_xscale('log')  # Log scale because alphas span orders of magnitude
ax1.set_xlabel('Alpha (log scale)')
ax1.set_ylabel('R² Score (Cross-Validation)')
ax1.set_title('Effect of Alpha on Model Performance')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Coefficient Shrinkage Path
# Shows how coefficients change as alpha increases
ax2 = axes[1]
alphas_fine = np.logspace(-3, 2, 50)  # 50 values from 0.001 to 100
ridge_coefs = []

for alpha in alphas_fine:
    ridge = Ridge(alpha=alpha)
    ridge.fit(X_train_scaled, y_train)
    ridge_coefs.append(ridge.coef_)

ridge_coefs = np.array(ridge_coefs)

# Plot each feature's coefficient path
for i, feature in enumerate(X.columns):
    ax2.plot(alphas_fine, ridge_coefs[:, i], label=feature, linewidth=2)

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

# ============================================================
# SUMMARY: WHEN TO USE WHICH?
# ============================================================
print("\n" + "="*60)
print("WHEN TO USE WHICH?")
print("="*60)
print("""
┌────────────────────┬─────────────────────────────────────────┐
│ Method             │ Best When                               │
├────────────────────┼─────────────────────────────────────────┤
│ Linear Regression  │ Small dataset, low risk of overfitting  │
│                    │ Few features, interpretability needed   │
├────────────────────┼─────────────────────────────────────────┤
│ Ridge (L2)         │ Many features, most are useful          │
│                    │ Multicollinearity present               │
│                    │ Don't need feature selection            │
├────────────────────┼─────────────────────────────────────────┤
│ Lasso (L1)         │ Many features, some are irrelevant      │
│                    │ Want automatic feature selection        │
│                    │ Need sparse model (few non-zero coefs)  │
├────────────────────┼─────────────────────────────────────────┤
│ ElasticNet         │ Many correlated features                │
│                    │ Want benefits of both Ridge and Lasso   │
│                    │ Dataset has groups of related features  │
└────────────────────┴─────────────────────────────────────────┘

RULE OF THUMB:
  1. Start with Ridge - it's safer and usually works well
  2. Try Lasso if you suspect many irrelevant features
  3. Use ElasticNet for complex datasets with correlations
  4. Always use cross-validation to find optimal alpha
""")
