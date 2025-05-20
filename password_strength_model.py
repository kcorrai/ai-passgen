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

# LSTM model ve tokenizer yükleme (varsa)
try:
    from keras.models import load_model
    import numpy as np
    import pickle
    LSTM_MODEL_PATH = os.path.join(os.path.dirname(__file__), "password_strength_lstm.h5")
    TOKENIZER_PATH = os.path.join(os.path.dirname(__file__), "password_tokenizer.pkl")
    if os.path.exists(LSTM_MODEL_PATH) and os.path.exists(TOKENIZER_PATH):
        lstm_model = load_model(LSTM_MODEL_PATH)
        with open(TOKENIZER_PATH, "rb") as f:
            lstm_tokenizer = pickle.load(f)
    else:
        lstm_model = None
        lstm_tokenizer = None
except ImportError:
    lstm_model = None
    lstm_tokenizer = None

def extract_features(password: str):
    # Uzunluk, büyük harf, küçük harf, rakam, sembol sayısı, yaygınlık (örnek)
    length = len(password)
    upper = sum(1 for c in password if c.isupper())
    lower = sum(1 for c in password if c.islower())
    digit = sum(1 for c in password if c.isdigit())
    symbol = sum(1 for c in password if not c.isalnum())
    # Basit bir wordlist kontrolü (örnek)
    common_words = {"password", "123456", "qwerty", "admin", "letmein"}
    is_common = int(password.lower() in common_words)
    return [[length, upper, lower, digit, symbol, is_common]]

def estimate_crack_time(password: str) -> float:
    """
    Parola için tahmini kırılma süresi (saniye) veya sınıf etiketi döndürür.
    sklearn modeli varsa onu, yoksa LSTM, o da yoksa dummy fonksiyonu kullanır.
    """
    # 1. scikit-learn model (ör: RandomForest, SVM, LogisticRegression)
    if sklearn_model is not None:
        features = extract_features(password)
        # Sınıf etiketi ("weak", "medium", "strong") döndürürse
        pred = sklearn_model.predict(features)[0]
        # Tahmini süre yerine sınıf etiketi döndürülür
        return pred

    # 2. LSTM model (keras)
    if lstm_model is not None and lstm_tokenizer is not None:
        seq = lstm_tokenizer.texts_to_sequences([password])
        from keras.preprocessing.sequence import pad_sequences
        X = pad_sequences(seq, maxlen=20)
        pred = lstm_model.predict(X)
        # Sınıf etiketi veya skor döndürülür
        if pred.shape[-1] == 1:
            return "strong" if pred[0][0] > 0.5 else "weak"
        else:
            idx = int(np.argmax(pred[0]))
            classes = ["weak", "medium", "strong"]
            return classes[idx]

    # 3. Dummy brute-force tahmini (varsayılan)
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
