#include <WiFi.h>  // Dla ESP8266 lub ESP32 można użyć <WiFi.h>
#include <DHT11.h>

DHT11 dht11(2);

const char* ssid = "H3";         // Nazwa sieci Wi-Fi
const char* password = "1234567890"; // Hasło do sieci Wi-Fi
const char* server_ip = "192.168.188.118";  // Adres IP serwera Python
const uint16_t server_port = 4000;      // Port, na którym działa serwer
int Moisture_ain = A0;
int ad_value;
int temperature = 0;
int humidity = 0;
String data;

const int relay4 = 4;
const int relay5 = 5;
const int relay6 = 6;
const int relay7 = 7;

WiFiClient client;

void setup() {
  Serial.begin(4800);
  pinMode(Moisture_ain, INPUT);

  pinMode(relay4, OUTPUT);
  pinMode(relay5, OUTPUT);
  pinMode(relay6, OUTPUT);
  pinMode(relay7, OUTPUT);

  // Wyłączenie przekaźników na starcie
  digitalWrite(relay4, HIGH); // światło
  digitalWrite(relay5, HIGH); // ogrzewanie 1
  digitalWrite(relay6, HIGH); // pompa
  digitalWrite(relay7, HIGH); // ogrzewanie 2

  // Łączenie się z siecią Wi-Fi
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Łączenie z Wi-Fi...");
  }

  Serial.println("Połączono z Wi-Fi");
}

void s_encode(String mess) {
  int firstDelimiter = mess.indexOf('|');
  int secondDelimiter = mess.indexOf('|', firstDelimiter + 1);

  String t_temp = mess.substring(0, firstDelimiter); // Temperatura
  String t_hum = mess.substring(firstDelimiter + 1, secondDelimiter); // Wilgotność
  String t_light = mess.substring(secondDelimiter + 1); // Światło

  float c_temp = t_temp.toFloat(); // Temperatura jako float
  int c_hum = t_hum.toInt();       // Wilgotność jako int
  bool c_light = (t_light.toInt() == 1);

  digitalWrite(relay4, c_light ? LOW : HIGH);

  if (temperature <= c_temp) {
    digitalWrite(relay5, LOW);
    digitalWrite(relay7, LOW);
  } else {
    digitalWrite(relay5, HIGH);
    digitalWrite(relay7, HIGH);
  }

  digitalWrite(relay6, humidity >= c_hum ? LOW : HIGH);
}

void loop() {
  int result = dht11.readTemperatureHumidity(temperature, humidity);
  ad_value = analogRead(Moisture_ain);

  if (result == 0) {
    data = "temperature=" + String(temperature) + "&humidity=" + String(ad_value);
    Serial.println(data); // Wyświetlenie wysyłanych danych
  } else {
    Serial.println("Błąd odczytu z czujnika");
    return; // Jeśli jest błąd, przerywamy pętlę
  }

  if (client.connect(server_ip, server_port)) {
    Serial.println("Połączono z serwerem");

    // Wysłanie danych do serwera
    client.print(data);
    client.flush(); // Upewniamy się, że dane zostały wysłane

    delay(600); // Krótka przerwa przed odbiorem odpowiedzi

    // Odbieranie odpowiedzi z serwera
    String response = "";
    while (client.available()) {
      response += (char)client.read();
    }

    if (response.length() > 0) {
      Serial.println("Otrzymano odpowiedź: " + response);
      s_encode(response);
    } else {
      Serial.println("Brak odpowiedzi od serwera.");
    }

    client.stop(); // Zamknięcie połączenia
  } else {
    Serial.println("Nie udało się połączyć z serwerem");
  }

  delay(6000); // Oczekiwanie przed kolejnym wysłaniem danych
}
