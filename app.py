from flask import Flask, render_template, request, session, redirect, url_for, Response
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import io
import json

from matplotlib.pyplot import figure, table

app = Flask(__name__)
app.secret_key = 'P0L1T36HN1K4'
CSV_FILE = "sensor_data.csv"
JSON_FILE = "client_data.json"


def load_data():
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

def save_data(temerature, humidity, light):
    with open(JSON_FILE, "w") as f:
        t_data =  dict(temperature=temerature, humidity=humidity, light=light)
        json.dump(t_data, f)



@app.route('/centrum', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        temp = request.form.get('slider_temp')
        humandity = request.form.get('slider_humandity')
        light = True if request.form.get('light') == '1' else False

        session['temp'] = temp
        session['humandity'] = humandity
        session['light'] = light

        print(temp, humandity, light)
        save_data(temp, humandity, light)

        return redirect(url_for('result'))

    return render_template('sliders.html')


@app.route('/results', methods=['GET','POST'])
def result():
    temp = session.get('temp')
    humandity = session.get('humandity')
    light = session.get('light')

    return render_template('results.html', slider_temp=temp, slider_humandity=humandity, checkbox_light=light)

@app.route("/plot_temp.png")
def plot_temp():
    df = load_data()
    if df.empty:
        return Response(status=204)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Rysowanie danych na wykresie
    ax.plot(df["Time"], df["Temperature"], label="Temperatura", color="red")
    ax.set_title("Temperatura", color="#1b5e20")
    ax.set_xlabel("Czas (Dzień godzina:minuta)")
    ax.set_ylabel("°C")
    ax.set_facecolor('#e8f5e9')  # Tło osi (obszar wykresu)
    fig.patch.set_facecolor('#e8f5e9')  # Tło całego wykresu

    ax.legend()
    ax.grid()

    # Formatowanie osi czasu
    date_format = DateFormatter("%m-%d %H:%M")  # Format: dzień godzina:minuta
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()  # Automatyczne obracanie etykiet dla lepszej czytelności

    # Zapis wykresu do strumienia jako PNG
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)  # Zamknięcie wykresu w pamięci

    return Response(img.getvalue(), mimetype="image/png")


@app.route("/plot_humidity.png")
def plot_humidity():
    df = load_data()
    if df.empty:
        return Response(status=204)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["Time"], df["Humidity"], label="Wilgotnosc gleby", color="blue")
    ax.set_title("Wilgotnosc gleby", color="#1b5e20")
    ax.set_xlabel("Czas (Dzień godzina:minuta)")
    ax.set_ylabel("Wartość")

    ax.set_facecolor('#e8f5e9')  # Tło osi (obszar wykresu)
    fig.patch.set_facecolor('#e8f5e9')  # Tło całego wykresu

    ax.legend()
    ax.grid()

    # Formatowanie osi czasu
    date_format = DateFormatter("%m-%d %H:%M")  # Format: dzień godzina:minuta
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()  # Automatyczne obracanie etykiet dla lepszej czytelności

    # Zapis wykresu do strumienia jako PNG
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)  # Zamknięcie wykresu w pamięci

    return Response(img.getvalue(), mimetype="image/png")

@app.route("/plots")
def plots():
    df = load_data()
    table_data = df.to_dict(orient="records")
    return render_template("index.html", table_data=table_data)

@app.route('/')
def str_start():
    return render_template('menu.html')


def run_flask():
    app.run()