from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Örnek parola ve etiketler (kendi verinizi buraya ekleyin)
passwords = [
    "password", "123456", "qwerty", "letmein", "admin", "welcome", "abc123", "P@ssw0rd", "QwErTy!2", "StrongPass123!"
]
labels = [
    "weak", "weak", "weak", "weak", "weak", "weak", "weak", "medium", "strong", "strong"
]

# Özellik çıkarımı (password_strength_model.py'deki extract_features fonksiyonu ile aynı olmalı)
def extract_features(password: str):
    length = len(password)
    upper = sum(1 for c in password if c.isupper())
    lower = sum(1 for c in password if c.islower())
    digit = sum(1 for c in password if c.isdigit())
    symbol = sum(1 for c in password if not c.isalnum())
    common_words = {"password", "123456", "qwerty", "admin", "letmein"}
    is_common = int(password.lower() in common_words)
    return [length, upper, lower, digit, symbol, is_common]

X = [extract_features(pw) for pw in passwords]
y = labels

# Eğitim ve test bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model eğitimi
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Değerlendirme
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Modeli kaydet
joblib.dump(model, "password_strength_model.pkl")
print("Model kaydedildi: password_strength_model.pkl")
