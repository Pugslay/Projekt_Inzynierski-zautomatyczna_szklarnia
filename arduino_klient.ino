#include <WiFi.h>  // Dla ESP8266 lub ESP32 można użyć <WiFi.h>

const char* ssid = "NETIASPOT-2.4GHz-72E7C8";         // Nazwa sieci Wi-Fi
const char* password = "fbqY2PzVT3RC"; // Hasło do sieci Wi-Fi
const char* server_ip = "192.168.1.22";  // Adres IP serwera Python
const uint16_t server_port = 5000;      // Port, na którym działa serwer

WiFiClient client;

void setup() {
  Serial.begin(4800);

  // Łączenie się z siecią Wi-Fi
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Łączenie z Wi-Fi...");
  }

  Serial.println("Połączono z Wi-Fi");
}

void loop() {
  if (client.connect(server_ip, server_port)) {
    Serial.println("Połączono z serwerem");

    // Wysłanie danych do serwera
    String data = "temperature=25&humidity=60";
    client.print(data);

    // Odczytanie odpowiedzi z serwera
    while (client.available()) {
      String response = client.readString();
      Serial.println("Odpowiedź serwera: " + response);
    }

    client.stop();
  } else {
    Serial.println("Nie udało się połączyć z serwerem");
  }

  delay(10000); // Wysyłanie danych co 10 sekund
}
