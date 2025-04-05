from flask import Flask, render_template, request, session, redirect, url_for, Response
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import io
import json

app = Flask(__name__)
with open('../secret_key.txt', 'r') as file:
    app.secret_key = file.read().strip()
CSV_FILE = "sensor_data.csv"
JSON_FILE = "client_data.json"


def load_data(): # funkcja otwiera plik CSV, prasuje dane i zapisuje je do Dataframe
    try: # otworzenie danych z dataframe oraz sprasowanie daty
        df = pd.read_csv(CSV_FILE, header=0)  # Wzięcie pod uwagę nagłówków z danymi
        df["Time"] = pd.to_datetime(df["Time"], format="%Y:%m:%d:%H:%M:%S", errors="coerce")

        # Powiadomienie w konsoli, jeśli dane są niepoprawne
        if df["Time"].isnull().any():
            print("Uwaga: Niektóre daty nie zostały poprawnie sparsowane. Sprawdź format danych.")

        return df.dropna()  # Usunięcie błędnych wierszy, jeśli występują
    except Exception as e: # zawarcie wyjątku na wypadek błędu odczytywania danych
        print(f"Nie udało się wczytać danych: {e}")
        return pd.DataFrame()  # Zwrócony zostaje pusty DataFrame w razie błędu

def save_data(temerature, humidity, light): # otworzenie pliku JSON i zapisanie danych
    with open(JSON_FILE, "w") as f:
        t_data =  dict(temperature=temerature, humidity=humidity, light=light)
        json.dump(t_data, f) # nadpisanie danych



@app.route('/centrum', methods=['GET', 'POST']) # strona gdzie użytkownik ma możliwość dostosowania parametrów
def index():
    if request.method == 'POST': # odczytanie danych ze strony
        temp = request.form.get('slider_temp')
        humandity = request.form.get('slider_humandity')
        light = True if request.form.get('light') == '1' else False

        #wyświetlenie danych i przypisanie ich do sessions oraz zapisano do pliku po przez funkcje save_data()
        print(temp, humandity, light)
        save_data(temp, humandity, light)

        session['temp'] = temp
        session['humandity'] = humandity
        session['light'] = light

        return redirect(url_for('result'))

    return render_template('sliders.html') # wygenerowanie strony


# strona internetowa, która wyświetla parametry użytkownika oraz daje możliwość powrotu do menu
@app.route('/results', methods=['GET','POST'])
def result(): # odczytanie danych z kontenera sessions
    temp = session.get('temp')
    humandity = session.get('humandity')
    light = session.get('light')

    # wygenerowanie strony, która jest jako wyświetlnie parametrów
    return render_template('results.html', slider_temp=temp, slider_humandity=humandity, checkbox_light=light)

@app.route("/plot_temp.png") # utworzenie obrazu png, aby była możliwosć wyświetlić na stronie wykres
def plot_temp(): #odczytanie danych z dataframe
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
    date_format = DateFormatter("%m-%d %H:%M") # Format: dzień godzina:minuta
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()  # Obrócenie etykiet dla lepszej czytelności

    # Zapis wykresu do strumienia jako PNG
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)  # Zamknięcie wykresu w pamięci

    return Response(img.getvalue(), mimetype="image/png") # zwrócenie jako obraz png


@app.route("/plot_humidity.png") # utworzenie obrazu png, aby była możliwosć wyświetlić na stronie wykres
def plot_humidity(): #odczytanie danych z dataframe
    df = load_data()
    if df.empty:
        return Response(status=204)

    # Rysowanie danych na wykresie
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
    fig.autofmt_xdate()  # Obrócenie etykiet dla lepszej czytelności

    # Zapis wykresu do strumienia jako PNG
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close(fig)  # Zamknięcie wykresu w pamięci

    return Response(img.getvalue(), mimetype="image/png")

@app.route("/plots") # strona wyświetlająca wygenerowane wykresy
def plots():
    return render_template("plots.html")

@app.route('/') # strona będąca menu aplikacji
def str_start():
    return render_template('menu.html')
