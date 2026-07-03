import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# ---------------------------------------------------------------------
# Load datasets
# ---------------------------------------------------------------------

dfs = []

# 1. Email scam dataset (ham=0, spam=1)
try:
    df1 = pd.read_csv("datasets/Email scam.csv", encoding="latin1")
    df1 = df1.rename(columns={df1.columns[0]: "label", df1.columns[1]: "text"})
    df1["label"] = df1["label"].map({"ham": 0, "spam": 1, "phishing": 1})
    df1.dropna(inplace=True)
    dfs.append(df1)
    print(f"Email scam.csv: {len(df1)} rows")
except Exception as e:
    print(f"Could not load Email scam.csv: {e}")

# 2. Enron dataset (if it has label + text columns)
try:
    df2 = pd.read_csv("datasets/Enron.csv", encoding="latin1")
    df2 = df2.rename(columns={df2.columns[0]: "label", df2.columns[1]: "text"})
    df2["label"] = df2["label"].map({"ham": 0, "spam": 1, "phishing": 1, 0: 0, 1: 1})
    df2.dropna(inplace=True)
    dfs.append(df2)
    print(f"Enron.csv: {len(df2)} rows")
except Exception as e:
    print(f"Could not load Enron.csv: {e}")

# 3. Nazario phishing dataset
try:
    df3 = pd.read_csv("datasets/Nazario.csv", encoding="latin1")
    df3 = df3.rename(columns={df3.columns[0]: "label", df3.columns[1]: "text"})
    df3["label"] = df3["label"].map({"ham": 0, "spam": 1, "phishing": 1, 0: 0, 1: 1})
    df3.dropna(inplace=True)
    dfs.append(df3)
    print(f"Nazario.csv: {len(df3)} rows")
except Exception as e:
    print(f"Could not load Nazario.csv: {e}")

# Combine all datasets
data = pd.concat(dfs, ignore_index=True)
data = data[["label", "text"]].dropna()
data["label"] = pd.to_numeric(data["label"], errors="coerce")
data.dropna(inplace=True)
data["label"] = data["label"].astype(int)

print(f"\nCombined dataset: {len(data)} rows")
print("Label distribution:")
print(data["label"].value_counts())
print(f"Phishing ratio: {data['label'].mean()*100:.1f}%")

# ---------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------

X = data["text"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000,   # more features than before
    ngram_range=(1, 2),   # also capture bigrams like "click here", "account suspended"
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# class_weight='balanced' is the key fix — compensates for ham/spam imbalance
model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
)

model.fit(X_train_tfidf, y_train)

# ---------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------

y_pred = model.predict(X_test_tfidf)
print("\nModel performance on test set:")
print(classification_report(y_test, y_pred, target_names=["ham", "phishing/spam"]))

# Quick sanity check
test_phishing = "urgent verify your password click here account suspended bank security alert login"
test_ham = "Hi, just checking in about our meeting tomorrow. See you at 10am!"

v_phish = vectorizer.transform([test_phishing])
v_ham = vectorizer.transform([test_ham])

print("Sanity check:")
print(f"  Phishing text -> predict={model.predict(v_phish)[0]}, proba={model.predict_proba(v_phish)[0]}")
print(f"  Ham text      -> predict={model.predict(v_ham)[0]}, proba={model.predict_proba(v_ham)[0]}")

# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------

pickle.dump(model, open("models/email_model.pkl", "wb"))
pickle.dump(vectorizer, open("models/email_vectorizer.pkl", "wb"))

print("\nEmail model trained and saved successfully!")