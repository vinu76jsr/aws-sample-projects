# Appendix: Python Libraries Tutorial

A beginner's guide to all libraries used in this project.

## Libraries Overview

| Library | Purpose | Why We Use It |
|---------|---------|---------------|
| **pandas** | Data manipulation | Load CSV, filter, transform data |
| **numpy** | Numerical computing | Math operations, arrays |
| **scikit-learn** | Machine learning | Models, metrics, preprocessing |
| **matplotlib** | Visualization | Create charts and plots |
| **scipy** | Scientific computing | Statistical tests |

---

## 1. Pandas - Data Manipulation

### What is Pandas?

Pandas is like Excel for Python. It lets you work with tabular data (rows and columns) easily.

### Installation

```bash
pip install pandas
```

### Core Concept: DataFrame

A DataFrame is a table with rows and columns:

```python
import pandas as pd

# Create from dictionary
data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
}
df = pd.DataFrame(data)
print(df)
```

Output:
```
      name  age     city
0    Alice   25      NYC
1      Bob   30       LA
2  Charlie   35  Chicago
```

### Reading Data

```python
# From CSV file
df = pd.read_csv('data.csv')

# From Excel
df = pd.read_excel('data.xlsx')

# From JSON
df = pd.read_json('data.json')
```

### Viewing Data

```python
# First 5 rows
df.head()

# Last 5 rows
df.tail()

# Random 5 rows
df.sample(5)

# Shape (rows, columns)
df.shape  # (100, 5) means 100 rows, 5 columns

# Column names
df.columns

# Data types
df.dtypes

# Summary statistics
df.describe()

# Info about DataFrame
df.info()
```

### Selecting Data

```python
# Single column (returns Series)
df['age']

# Multiple columns (returns DataFrame)
df[['name', 'age']]

# Single row by index
df.iloc[0]  # First row

# Multiple rows
df.iloc[0:5]  # First 5 rows

# Row by label
df.loc[0]

# Specific cell
df.iloc[0, 1]  # Row 0, Column 1
df.loc[0, 'age']  # Row 0, 'age' column
```

### Filtering Data

```python
# Filter rows where age > 25
df[df['age'] > 25]

# Multiple conditions (use & for AND, | for OR)
df[(df['age'] > 25) & (df['city'] == 'NYC')]

# Filter using isin
df[df['city'].isin(['NYC', 'LA'])]

# Filter nulls
df[df['age'].isna()]      # Rows where age is null
df[df['age'].notna()]     # Rows where age is not null
```

### Modifying Data

```python
# Add new column
df['country'] = 'USA'

# Calculate new column
df['age_in_months'] = df['age'] * 12

# Rename columns
df.rename(columns={'name': 'full_name'}, inplace=True)

# Drop column
df.drop('country', axis=1, inplace=True)

# Drop row
df.drop(0, axis=0, inplace=True)

# Replace values
df['city'].replace('NYC', 'New York', inplace=True)

# Fill missing values
df['age'].fillna(0, inplace=True)
df['age'].fillna(df['age'].mean(), inplace=True)  # Fill with mean
```

### Aggregations

```python
# Basic stats
df['age'].mean()
df['age'].median()
df['age'].std()
df['age'].min()
df['age'].max()
df['age'].sum()

# Group by
df.groupby('city')['age'].mean()

# Multiple aggregations
df.groupby('city').agg({
    'age': ['mean', 'max'],
    'name': 'count'
})
```

### Sorting

```python
# Sort by column
df.sort_values('age')

# Descending
df.sort_values('age', ascending=False)

# Multiple columns
df.sort_values(['city', 'age'])
```

### Saving Data

```python
# To CSV
df.to_csv('output.csv', index=False)

# To Excel
df.to_excel('output.xlsx', index=False)

# To JSON
df.to_json('output.json')
```

---

## 2. NumPy - Numerical Computing

### What is NumPy?

NumPy provides fast mathematical operations on arrays. It's the foundation for scientific Python.

### Installation

```bash
pip install numpy
```

### Core Concept: ndarray

NumPy's main object is the N-dimensional array:

```python
import numpy as np

# Create array from list
arr = np.array([1, 2, 3, 4, 5])
print(arr)  # [1 2 3 4 5]

# 2D array (matrix)
matrix = np.array([[1, 2, 3],
                   [4, 5, 6]])
print(matrix)
# [[1 2 3]
#  [4 5 6]]
```

### Creating Arrays

```python
# Zeros
np.zeros(5)           # [0. 0. 0. 0. 0.]
np.zeros((3, 4))      # 3x4 matrix of zeros

# Ones
np.ones(5)            # [1. 1. 1. 1. 1.]

# Range
np.arange(0, 10, 2)   # [0 2 4 6 8]

# Evenly spaced
np.linspace(0, 1, 5)  # [0. 0.25 0.5 0.75 1.]

# Random
np.random.rand(5)     # 5 random floats between 0-1
np.random.randn(5)    # 5 random floats from normal distribution
np.random.randint(0, 10, 5)  # 5 random integers 0-9
```

### Array Properties

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.shape      # (2, 3) - 2 rows, 3 columns
arr.ndim       # 2 - number of dimensions
arr.size       # 6 - total elements
arr.dtype      # dtype('int64') - data type
```

### Array Operations

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Element-wise operations
a + b    # [5, 7, 9]
a - b    # [-3, -3, -3]
a * b    # [4, 10, 18]
a / b    # [0.25, 0.4, 0.5]
a ** 2   # [1, 4, 9]

# Scalar operations
a + 10   # [11, 12, 13]
a * 2    # [2, 4, 6]
```

### Mathematical Functions

```python
arr = np.array([1, 4, 9, 16])

np.sqrt(arr)    # [1. 2. 3. 4.]
np.exp(arr)     # e^x for each element
np.log(arr)     # natural log
np.sin(arr)     # sine
np.abs(arr)     # absolute value
```

### Statistics

```python
arr = np.array([1, 2, 3, 4, 5])

np.mean(arr)    # 3.0 - average
np.median(arr)  # 3.0 - middle value
np.std(arr)     # 1.41 - standard deviation
np.var(arr)     # 2.0 - variance
np.min(arr)     # 1
np.max(arr)     # 5
np.sum(arr)     # 15
```

### Reshaping

```python
arr = np.array([1, 2, 3, 4, 5, 6])

# Reshape to 2x3
arr.reshape(2, 3)
# [[1 2 3]
#  [4 5 6]]

# Flatten to 1D
matrix.flatten()  # [1 2 3 4 5 6]

# Transpose
matrix.T
```

### Indexing and Slicing

```python
arr = np.array([10, 20, 30, 40, 50])

arr[0]      # 10 - first element
arr[-1]     # 50 - last element
arr[1:4]    # [20, 30, 40] - slice

# 2D indexing
matrix = np.array([[1, 2, 3], [4, 5, 6]])
matrix[0, 1]    # 2 - row 0, col 1
matrix[:, 0]    # [1, 4] - all rows, col 0
matrix[1, :]    # [4, 5, 6] - row 1, all cols
```

### Why NumPy over Python Lists?

```python
# Speed comparison
import time

size = 1000000

# Python list
py_list = list(range(size))
start = time.time()
py_result = [x * 2 for x in py_list]
print(f"Python list: {time.time() - start:.4f}s")

# NumPy array
np_arr = np.arange(size)
start = time.time()
np_result = np_arr * 2
print(f"NumPy array: {time.time() - start:.4f}s")

# NumPy is typically 10-100x faster!
```

---

## 3. Scikit-learn - Machine Learning

### What is Scikit-learn?

Scikit-learn (sklearn) is the most popular ML library for Python. It provides:
- Preprocessing tools
- ML algorithms
- Model evaluation metrics

### Installation

```bash
pip install scikit-learn
```

### The Sklearn Pattern

Almost everything in sklearn follows this pattern:

```python
from sklearn.some_module import SomeClass

# 1. Create instance
model = SomeClass()

# 2. Fit (learn from data)
model.fit(X_train, y_train)

# 3. Transform or Predict
result = model.transform(X_test)  # For preprocessors
result = model.predict(X_test)    # For models
```

### Train/Test Split

```python
from sklearn.model_selection import train_test_split

# X = features, y = target
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,     # 20% for testing
    random_state=42    # Reproducible split
)
```

**Parameters explained**:
- `test_size`: Fraction of data for testing (0.2 = 20%)
- `random_state`: Seed for randomness. Same number = same split every time.

### Preprocessing: StandardScaler

Scales features to have mean=0 and std=1:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

# Fit on training data (learns mean & std)
scaler.fit(X_train)

# Transform both sets
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Or fit and transform in one step
X_train_scaled = scaler.fit_transform(X_train)
```

**Important**: Only `fit` on training data to avoid data leakage!

### Preprocessing: MinMaxScaler

Scales features to range [0, 1]:

```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
```

### Linear Regression

```python
from sklearn.linear_model import LinearRegression

# Create model
model = LinearRegression()

# Train
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# View learned formula
print("Coefficients:", model.coef_)
print("Intercept:", model.intercept_)
```

### Ridge Regression (L2 Regularization)

```python
from sklearn.linear_model import Ridge

# alpha controls regularization strength
model = Ridge(alpha=1.0)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### Lasso Regression (L1 Regularization)

```python
from sklearn.linear_model import Lasso

model = Lasso(alpha=0.1)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# Lasso can zero out coefficients (feature selection)
print("Coefficients:", model.coef_)
```

### Evaluation Metrics

```python
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)

# Mean Squared Error
mse = mean_squared_error(y_test, predictions)

# Root Mean Squared Error
rmse = np.sqrt(mse)

# Mean Absolute Error
mae = mean_absolute_error(y_test, predictions)

# R² Score
r2 = r2_score(y_test, predictions)

print(f"MSE: {mse:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAE: {mae:.2f}")
print(f"R²: {r2:.4f}")
```

### Cross-Validation

Test model on multiple splits for more reliable evaluation:

```python
from sklearn.model_selection import cross_val_score

model = LinearRegression()

# 5-fold cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring='r2')

print(f"R² scores: {scores}")
print(f"Mean R²: {scores.mean():.4f}")
print(f"Std: {scores.std():.4f}")
```

### Pipeline

Chain preprocessing and model together:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

# Create pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LinearRegression())
])

# Use like a single model
pipe.fit(X_train, y_train)
predictions = pipe.predict(X_test)
```

---

## 4. Matplotlib - Visualization

### What is Matplotlib?

Matplotlib creates static charts and plots. It's the most widely used Python visualization library.

### Installation

```bash
pip install matplotlib
```

### Basic Plot

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

plt.plot(x, y)
plt.show()
```

### Line Plot with Styling

```python
plt.figure(figsize=(10, 6))  # Width, Height in inches

plt.plot(x, y,
         color='blue',
         linestyle='--',      # '--', '-', ':', '-.'
         linewidth=2,
         marker='o',          # 'o', 's', '^', 'x'
         markersize=8,
         label='My Data')

plt.xlabel('X Axis Label')
plt.ylabel('Y Axis Label')
plt.title('My Plot Title')
plt.legend()
plt.grid(True, alpha=0.3)

plt.savefig('plot.png', dpi=150, bbox_inches='tight')
plt.show()
```

### Scatter Plot

```python
plt.figure(figsize=(10, 6))

plt.scatter(x, y,
            c='red',          # color
            s=100,            # size
            alpha=0.7,        # transparency
            marker='o',
            label='Points')

plt.xlabel('X')
plt.ylabel('Y')
plt.title('Scatter Plot')
plt.legend()
plt.show()
```

### Histogram

```python
data = np.random.randn(1000)  # 1000 random numbers

plt.figure(figsize=(10, 6))
plt.hist(data,
         bins=30,             # Number of bars
         color='steelblue',
         edgecolor='black',
         alpha=0.7)

plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram')
plt.show()
```

### Bar Chart

```python
categories = ['A', 'B', 'C', 'D']
values = [25, 40, 30, 55]

plt.figure(figsize=(10, 6))
plt.bar(categories, values, color='teal', edgecolor='black')

plt.xlabel('Category')
plt.ylabel('Value')
plt.title('Bar Chart')
plt.show()
```

### Multiple Subplots

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Top-left
axes[0, 0].plot(x, y)
axes[0, 0].set_title('Line Plot')

# Top-right
axes[0, 1].scatter(x, y)
axes[0, 1].set_title('Scatter Plot')

# Bottom-left
axes[1, 0].bar(categories, values)
axes[1, 0].set_title('Bar Chart')

# Bottom-right
axes[1, 1].hist(data, bins=20)
axes[1, 1].set_title('Histogram')

plt.tight_layout()  # Prevent overlap
plt.show()
```

### Heatmap (Correlation Matrix)

```python
import pandas as pd

# Create correlation matrix
df = pd.DataFrame(np.random.randn(100, 4), columns=['A', 'B', 'C', 'D'])
corr = df.corr()

plt.figure(figsize=(8, 6))
plt.imshow(corr, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
plt.colorbar()

# Add labels
plt.xticks(range(len(corr.columns)), corr.columns)
plt.yticks(range(len(corr.columns)), corr.columns)

# Add values
for i in range(len(corr)):
    for j in range(len(corr)):
        plt.text(j, i, f'{corr.iloc[i, j]:.2f}',
                ha='center', va='center')

plt.title('Correlation Matrix')
plt.show()
```

---

## 5. SciPy - Scientific Computing

### What is SciPy?

SciPy extends NumPy with advanced mathematical functions, including statistical tests.

### Installation

```bash
pip install scipy
```

### Statistical Tests

#### Shapiro-Wilk Test (Normality)

Tests if data is normally distributed:

```python
from scipy import stats

data = np.random.randn(100)

statistic, p_value = stats.shapiro(data)

print(f"Statistic: {statistic:.4f}")
print(f"P-value: {p_value:.4f}")

if p_value > 0.05:
    print("Data appears normally distributed")
else:
    print("Data is NOT normally distributed")
```

#### T-Test (Compare Two Groups)

```python
group1 = [85, 90, 78, 92, 88]
group2 = [75, 80, 72, 85, 79]

statistic, p_value = stats.ttest_ind(group1, group2)

print(f"T-statistic: {statistic:.4f}")
print(f"P-value: {p_value:.4f}")

if p_value < 0.05:
    print("Groups are significantly different")
else:
    print("No significant difference between groups")
```

#### Pearson Correlation

```python
x = [1, 2, 3, 4, 5]
y = [2, 4, 5, 4, 5]

correlation, p_value = stats.pearsonr(x, y)

print(f"Correlation: {correlation:.4f}")
print(f"P-value: {p_value:.4f}")
```

### Descriptive Statistics

```python
data = [23, 45, 67, 32, 56, 78, 45, 34, 67, 89]

# All at once
description = stats.describe(data)

print(f"Count: {description.nobs}")
print(f"Min: {description.minmax[0]}")
print(f"Max: {description.minmax[1]}")
print(f"Mean: {description.mean:.2f}")
print(f"Variance: {description.variance:.2f}")
print(f"Skewness: {description.skewness:.2f}")
print(f"Kurtosis: {description.kurtosis:.2f}")
```

---

## Quick Reference Card

### Pandas
```python
import pandas as pd
df = pd.read_csv('file.csv')    # Load data
df.head()                        # View first rows
df['column']                     # Select column
df[df['col'] > 5]               # Filter rows
df.groupby('col').mean()        # Aggregate
df.to_csv('out.csv')            # Save
```

### NumPy
```python
import numpy as np
arr = np.array([1, 2, 3])       # Create array
np.zeros((3, 3))                # Array of zeros
np.mean(arr)                    # Average
np.sqrt(arr)                    # Square root
arr.reshape(1, 3)               # Change shape
```

### Scikit-learn
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
model = LinearRegression()
model.fit(X_train_scaled, y_train)
predictions = model.predict(scaler.transform(X_test))
print(r2_score(y_test, predictions))
```

### Matplotlib
```python
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='data')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Title')
plt.legend()
plt.savefig('plot.png')
plt.show()
```

### SciPy
```python
from scipy import stats
stats.shapiro(data)             # Normality test
stats.ttest_ind(a, b)           # T-test
stats.pearsonr(x, y)            # Correlation
stats.describe(data)            # Summary stats
```
