import math
import os

try:
    import joblib
    SKLEARN_MODEL_PATH = os.path.join(os.path.dirname(__file__), "password_strength_model.pkl")
    if os.path.exists(SKLEARN_MODEL_PATH):
        sklearn_model = joblib.load(SKLEARN_MODEL_PATH)
    else:
        sklearn_model = None
except ImportError:
    sklearn_model = None

def extract_features(password: str):
    # Basit örnek: uzunluk, büyük harf, küçük harf, rakam, sembol sayısı
    length = len(password)
    upper = sum(1 for c in password if c.isupper())
    lower = sum(1 for c in password if c.islower())
    digit = sum(1 for c in password if c.isdigit())
    symbol = sum(1 for c in password if not c.isalnum())
    return [[length, upper, lower, digit, symbol]]

def estimate_crack_time(password: str) -> float:
    """
    Parola için tahmini kırılma süresi (saniye) döndürür.
    Eğer sklearn modeli varsa onu kullanır, yoksa dummy fonksiyona döner.
    """
    if sklearn_model is not None:
        features = extract_features(password)
        # Modelin çıktısı log(saniye) ise, üstelini al
        log_crack_time = sklearn_model.predict(features)[0]
        crack_time = float(2 ** log_crack_time)
        return crack_time
    length = len(password)
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(not c.isalnum() for c in password):
        charset += 32
    if charset == 0:
        return 0
    entropy = length * math.log2(charset)
    guesses = 2 ** entropy
    crack_time = guesses / 1e9
    return crack_time
