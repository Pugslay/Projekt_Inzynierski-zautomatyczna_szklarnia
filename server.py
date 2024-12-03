import socket
import sys
import csv
import time

CSV_FILE = "sensor_data.csv"

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Powiązanie gniazda z adresem IP i portem
    server_socket.bind(('0.0.0.0', 5000))

    # Rozpoczęcie nasłuchiwania na połączenia (maksymalnie 5 w kolejce)
    server_socket.listen(5)
    print("Serwer nasłuchuje na porcie 5000...")



    while True:
        try:
            with open(CSV_FILE, mode="x", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Time","Temperature", "Humidity"])
        except FileExistsError:
            pass  # Plik już istnieje, więc nic nie robimy

        # Akceptowanie połączenia od klienta (Arduino)
        client_socket, addr = server_socket.accept()
        print(f"Połączono z {addr}")

        # Odbieranie danych od Arduino
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            print(f"Otrzymano dane: {data}")

            # Można odesłać odpowiedź do Arduino, jeśli potrzebne
            client_socket.send("Dane odebrane".encode('utf-8'))

            t = time.localtime()
            ttime = time.strftime("%Y:%m:%d:%H:%M:%S", t)
            params = dict(param.split("=") for param in data.split("&"))
            temperature = params.get("temperature", "0")
            humidity = params.get("humidity", "0")

            with open(CSV_FILE, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([ttime,temperature, humidity, ])

        # Zamknięcie połączenia z klientem
        client_socket.close()

start_server()
