<<<<<<< Updated upstream
import socket
import sys


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Powiązanie gniazda z adresem IP i portem
    server_socket.bind(('0.0.0.0', 5000))

    # Rozpoczęcie nasłuchiwania na połączenia (maksymalnie 5 w kolejce)
    server_socket.listen(5)
    print("Serwer nasłuchuje na porcie 5000...")

    while True:
        # Akceptowanie połączenia od klienta (Arduino)
        client_socket, addr = server_socket.accept()
        print(f"Połączono z {addr}")

        # Odbieranie danych od Arduino
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            print(f"Otrzymano dane: {data}")

            # Można odesłać odpowiedź do Arduino, jeśli potrzebne
            client_socket.send("Dane odebrane".encode('utf-8'))

        # Zamknięcie połączenia z klientem
        client_socket.close()
=======
import socket
import csv
import time
import json
from datetime import datetime, timedelta

CSV_FILE = "sensor_data.csv"
JSON_FILE = "client_data.json"

def clear_data(csv_file):
    try:
        old_date = datetime.now() - timedelta(days=3)

        data = []
        with open(csv_file, mode = "r" , newline = "") as file:
            read = csv.reader(file)
            head = next(read)
            for row in read:
                try:
                    row_time = datetime.strptime(row[0], "%Y:%m:%d:%H:%M:%S")
                    if row_time >= old_date:
                        data.append(row)
                except ValueError:
                    continue


        with open(csv_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(head)
                writer.writerows(data)
    except FileNotFoundError:
        print(f"Plik {csv_file} nie istnieje.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 3000))
    server_socket.listen(5)
    print("Serwer nasłuchuje na porcie 3000...")

    try:
        with open(CSV_FILE, mode="x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Time", "Temperature", "Humidity"])
    except FileExistsError:
        pass

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Połączono z {addr}")

        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                print(f"Otrzymano dane: {data}")
                try:
                    params = dict(param.split("=") for param in data.split("&"))
                    temperature = params.get("temperature", "0")
                    humidity = params.get("humidity", "0")
                except ValueError:
                    print("Błąd: niepoprawny format danych.")
                    temperature = "0"
                    humidity = "0"

                t = time.localtime()
                ttime = time.strftime("%Y:%m:%d:%H:%M:%S", t)
                with open(CSV_FILE, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([ttime, temperature, humidity])

                try:
                    with open(JSON_FILE, mode="r") as file:
                        json_data = json.load(file)
                        t_temp = json_data.get("temperature", "0")
                        t_hum = json_data.get("humidity", "0")
                        t_light = 1 if json_data.get("light", False) else 0
                    message = t_temp + '|' + t_hum + '|' + str(t_light)
                    print(f"Wysłanie wiadomości: {message}")
                    client_socket.send(message.encode('utf-8'))
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Błąd wczytywania JSON: {e}")
        except ConnectionResetError:
            print("Klient zakończył połączenie gwałtownie.")
        finally:
            client_socket.close()
            clear_data(CSV_FILE)

if __name__ == "__main__":
    start_server()

>>>>>>> Stashed changes
