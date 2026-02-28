import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np



# Step 1: Create dataset
data = {
    "experience": [1, 2, 3, 4, 5, 6, 7],
    "salary": [30000, 40000, 70000, 80000, 1000000, 1200000, 130000]
}

df = pd.DataFrame(data)

# Step 2: Split input (X) and output (y)
X = df[["experience"]]   # Input (must be 2D)
y = df["salary"]         # Output

# Step 3: Create model
model = LinearRegression()

# Step 4: Train model
model.fit(X, y)

# Step 5: Make prediction
predicted_salary = model.predict([[15]])

print("Predicted salary for 8 years experience:", predicted_salary[0])