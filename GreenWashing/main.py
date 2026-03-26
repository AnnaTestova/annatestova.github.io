import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

from src.pipeline import process_pdf
from src.features import create_tfidf_features, add_numeric_feature
from src.preprocessing import preprocess


csv_path = "data/sustainability_sentences.csv"

df = pd.read_csv(csv_path)
print(f"Loaded {len(df)} sentences for training")

clean_text = df["text"].apply(preprocess)

X, vectorizer = create_tfidf_features(clean_text)
X = add_numeric_feature(X, df["text"])
y = df["label"]

model = LogisticRegression(max_iter=1000)
model.fit(X, y)

print("Model training complete!!\n")

joblib.dump(model, "greenwashing_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")


reports_folder = "data/raw_reports"

for filename in os.listdir(reports_folder):
    if filename.endswith(".txt"):

        file_path = os.path.join(reports_folder, filename)
        print(f"\nProcessing: {filename}")

        sentences, X_pdf = process_pdf(file_path, vectorizer=vectorizer)

        predictions = model.predict(X_pdf)

        total = len(sentences)
        greenwash_count = sum(predictions)
        percentage = (greenwash_count / total * 100) if total > 0 else 0

        print(f"Total sentences: {total}")
        print(f"Greenwashing sentences: {greenwash_count}")
        print(f"Percentage greenwashing: {percentage:.2f}%")

        results_df = pd.DataFrame({
            "sentence": sentences,
            "greenwashing_prediction": predictions
        })

        output_path = os.path.join("data", f"{filename}_results.csv")
        results_df.to_csv(output_path, index=False,  encoding="utf-8-sig")

        print(f"Results saved to: {output_path}")
