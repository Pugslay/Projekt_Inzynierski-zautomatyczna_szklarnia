from flask import Flask, render_template, Response
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Ścieżka do pliku CSV
CSV_FILE = "sensor_data.csv"


def load_data():
    """Wczytuje dane z pliku CSV i zwraca DataFrame."""
    try:
        df = pd.read_csv(CSV_FILE, header=0)  # Zakładamy, że plik ma nagłówki
        df["Time"] = pd.to_datetime(df["Time"], format="%Y:%m:%d:%H:%M:%S", errors="coerce")

        # Obsługa potencjalnych błędów parsowania dat
        if df["Time"].isnull().any():
            print("Uwaga: Niektóre daty nie zostały poprawnie sparsowane. Sprawdź format danych.")

        return df.dropna()  # Usunięcie błędnych wierszy, jeśli występują
    except Exception as e:
        print(f"Nie udało się wczytać danych: {e}")
        return pd.DataFrame()  # Zwróć pusty DataFrame w razie błędu


@app.route("/")
def index():
    """Strona główna z tabelą danych i wykresem."""
    df = load_data()
    table_data = df.to_dict(orient="records")  # Dane tabeli dla szablonu
    return render_template("index.html", table_data=table_data)

@app.route("/plot.png")
def plot_png():
    """Generuje wykres Matplotlib jako obraz PNG."""
    df = load_data()
    fig, ax = plt.subplots(figsize=(10, 6))

    # Rysowanie danych na wykresie
    ax.plot(df["Time"], df["Temperature"], label="Temperatura", color="red")
    ax.plot(df["Time"], df["Humidity"], label="Wilgotnosc gleby", color="blue")
    ax.set_title("Temperatura i wilgotnosc gleby")
    ax.set_xlabel("Czas (Dzien godzina:minuta)")
    ax.set_ylabel("Wartosci")
    ax.legend()
    ax.grid()

    # Formatowanie osi czasu
    fig.autofmt_xdate()

    # Zapis wykresu do strumienia jako PNG
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)  # Zamknięcie wykresu w pamięci

    return Response(img.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
