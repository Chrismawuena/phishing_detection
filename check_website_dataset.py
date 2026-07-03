import pandas as pd

data = pd.read_csv("datasets/Phishing_Websites.csv")

print("\nColumns:")
print(data.columns)

print("\nFirst 5 rows:")
print(data.head())