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
