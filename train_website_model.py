import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_csv("datasets/Phishing_Websites.csv")

# Remove Index column
data = data.drop("Index", axis=1)

# Features
X = data.drop("class", axis=1)

# Labels
y = data["class"]

# Convert labels
# Phishing = 1
# Legitimate = 0

y = y.replace({
    -1: 1,
     1: 0
})

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# Test accuracy
predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("Accuracy:", accuracy)

# Save model
with open("models/website_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Website model saved successfully")