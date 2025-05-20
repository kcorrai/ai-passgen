import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from password_strength_model import estimate_crack_time
import random
import string

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.2f} saniye"
    elif seconds < 3600:
        return f"{seconds/60:.2f} dakika"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} saat"
    elif seconds < 31536000:
        return f"{seconds/86400:.2f} gün"
    else:
        return f"{seconds/31536000:.2f} yıl"

def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation
    if not chars:
        chars = string.ascii_letters  # fallback
    return ''.join(random.choice(chars) for _ in range(length))

class PasswordStrengthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Yapay Zekâ ile Parola Gücü Analizörü")
        self.geometry("520x420")
        self.minsize(520, 420)

        self.tabview = ctk.CTkTabview(self, width=500, height=400)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        self.tab_analyze = self.tabview.add("Parola Analiz")
        self.tab_generate = self.tabview.add("Parola Oluşturucu")

        # --- Parola Analiz Bölümü ---
        self.password_entry = ctk.CTkEntry(self.tab_analyze, placeholder_text="Parolanızı girin")
        self.password_entry.pack(pady=20)
        self.analyze_btn = ctk.CTkButton(self.tab_analyze, text="Analiz Et", command=self.analyze_password)
        self.analyze_btn.pack(pady=10)
        self.result_label = ctk.CTkLabel(self.tab_analyze, text="")
        self.result_label.pack(pady=10)
        self.canvas_frame = ctk.CTkFrame(self.tab_analyze)
        self.canvas_frame.pack(fill="both", expand=True)

        # --- Parola Oluşturucu Bölümü ---
        self.length_label = ctk.CTkLabel(self.tab_generate, text="Parola Uzunluğu:")
        self.length_label.pack(pady=(20, 5))
        self.length_var = ctk.IntVar(value=12)
        self.length_slider = ctk.CTkSlider(self.tab_generate, from_=6, to=32, number_of_steps=26, variable=self.length_var, command=self.update_length_label)
        self.length_slider.pack(pady=5)
        self.length_value_label = ctk.CTkLabel(self.tab_generate, text=f"{self.length_var.get()} karakter")
        self.length_value_label.pack(pady=(0, 8))

        # Checkbox'lar
        self.upper_var = ctk.BooleanVar(value=True)
        self.lower_var = ctk.BooleanVar(value=True)
        self.digit_var = ctk.BooleanVar(value=True)
        self.symbol_var = ctk.BooleanVar(value=True)
        checkbox_opts = {
            "checkbox_height": 24,
            "checkbox_width": 24,
            "font": ("Arial", 12)
        }
        self.upper_cb = ctk.CTkCheckBox(self.tab_generate, text="Büyük Harf", variable=self.upper_var, **checkbox_opts)
        self.lower_cb = ctk.CTkCheckBox(self.tab_generate, text="Küçük Harf", variable=self.lower_var, **checkbox_opts)
        self.digit_cb = ctk.CTkCheckBox(self.tab_generate, text="Rakam", variable=self.digit_var, **checkbox_opts)
        self.symbol_cb = ctk.CTkCheckBox(self.tab_generate, text="Sembol", variable=self.symbol_var, **checkbox_opts)
        self.upper_cb.pack(anchor="w", padx=30, pady=(0, 4))
        self.lower_cb.pack(anchor="w", padx=30, pady=(0, 4))
        self.digit_cb.pack(anchor="w", padx=30, pady=(0, 4))
        self.symbol_cb.pack(anchor="w", padx=30, pady=(0, 8))

        self.generate_btn = ctk.CTkButton(self.tab_generate, text="Parola Oluştur", command=self.create_password)
        self.generate_btn.pack(pady=10)
        self.generated_entry = ctk.CTkEntry(self.tab_generate, width=300)
        self.generated_entry.pack(pady=10)
        self.copy_btn = ctk.CTkButton(self.tab_generate, text="Kopyala", command=self.copy_password)
        self.copy_btn.pack(pady=5)
        self.copy_label = ctk.CTkLabel(self.tab_generate, text="")
        self.copy_label.pack(pady=5)

    def analyze_password(self):
        password = self.password_entry.get()
        from password_strength_model import sklearn_model, lstm_model
        if sklearn_model is not None:
            print("Analiz yöntemi: scikit-learn (makine öğrenmesi)")
        elif lstm_model is not None:
            print("Analiz yöntemi: LSTM (derin öğrenme)")
        else:
            print("Analiz yöntemi: brute-force (dummy hesaplama)")
        crack_time = estimate_crack_time(password)
        # Sonucun türüne göre uygun mesajı göster
        if isinstance(crack_time, (int, float)):
            result_text = f"Tahmini kırılma süresi: {format_time(crack_time)}"
        else:
            result_text = f"Parola gücü: {crack_time}"
        self.result_label.configure(text=result_text)
        self.show_graph(crack_time)

    def show_graph(self, crack_time):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        # Sadece sayı ise kırılma süresi grafiği çiz
        if isinstance(crack_time, (int, float)):
            fig, ax = plt.subplots(figsize=(5,2.5))
            # Kırılma süresini farklı zaman dilimleriyle karşılaştır
            times = [1, 60, 3600, 86400, 31536000, crack_time]
            labels = ["1 sn", "1 dk", "1 sa", "1 gün", "1 yıl", "Parolanız"]
            colors = ["grey"]*5 + ["blue"]
            ax.bar(labels, times, color=colors)
            ax.set_yscale('log')
            ax.set_ylabel("Tahmini Kırılma Süresi (saniye, log ölçek)")
            ax.set_title("Parolanızın Tahmini Kırılma Süresi")
            # Parolanın kırılma süresini üstte göster
            ax.text(len(labels)-1, times[-1], format_time(crack_time), ha='center', va='bottom', color='blue', fontweight='bold')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        else:
            # Sınıf etiketi için görsel grafik (weak/medium/strong)
            fig, ax = plt.subplots(figsize=(4,2))
            classes = ["weak", "medium", "strong"]
            values = [0.5 if crack_time == c else 0.1 for c in classes]
            colors = ["red" if crack_time == "weak" else "grey",
                      "orange" if crack_time == "medium" else "grey",
                      "green" if crack_time == "strong" else "grey"]
            ax.bar(classes, values, color=colors)
            ax.set_ylim(0, 1)
            ax.set_ylabel("Güç Skoru (görsel)")
            ax.set_title("Parola Gücü Sınıfı")
            for i, v in enumerate(values):
                if v > 0.1:
                    ax.text(i, v + 0.05, crack_time.upper(), ha='center', fontweight='bold')
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

    def create_password(self):
        length = int(self.length_var.get())
        password = generate_password(
            length,
            use_upper=self.upper_var.get(),
            use_lower=self.lower_var.get(),
            use_digits=self.digit_var.get(),
            use_symbols=self.symbol_var.get()
        )
        self.generated_entry.delete(0, "end")
        self.generated_entry.insert(0, password)
        self.copy_label.configure(text="")

    def copy_password(self):
        password = self.generated_entry.get()
        if password:
            self.clipboard_clear()
            self.clipboard_append(password)
            self.copy_label.configure(text="Kopyalandı!")

    def update_length_label(self, value):
        self.length_value_label.configure(text=f"{int(float(value))} karakter")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = PasswordStrengthApp()
    app.mainloop()
