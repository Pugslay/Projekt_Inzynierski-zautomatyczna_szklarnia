#include <WiFi.h>
#include <DHT11.h>
#include <EEPROM.h>



const char* ssid = "H3";
const char* password = "1234567890";
const char* server_ip = "192.168.17.118";
const uint16_t server_port = 3000;

const int Moisture_ain = A0;
const int relay4 = 3; // Światło
const int relay5 = 5; // Ogrzewanie 1
const int relay6 = 6; // Pompa
const int relay7 = 7; // Ogrzewanie 2

int ad_value = 0;
int temperature = 0;
int humidity = 0;
int i = 0;
String data;

DHT11 dht11(2);
WiFiClient client;

struct Variables {
  float c_temp;
  int c_hum;
  bool c_light;
};

void applySettings(Variables var) {
  // Sterowanie przekaźnikami na podstawie danych
  digitalWrite(relay4, var.c_light ? LOW : HIGH); // Światło 
  digitalWrite(relay5, temperature <= var.c_temp ? LOW : HIGH); // Ogrzewanie 1
  digitalWrite(relay7, temperature <= var.c_temp ? LOW : HIGH); // Ogrzewanie 2
  digitalWrite(relay6, humidity <= var.c_hum ? LOW : HIGH); // Pompa
}

void setup() {
  Serial.begin(115200);
  pinMode(Moisture_ain, INPUT);

  pinMode(relay4, OUTPUT);
  pinMode(relay5, OUTPUT);
  pinMode(relay6, OUTPUT);
  pinMode(relay7, OUTPUT);

  // Wyłączenie przekaźników na starcie
  digitalWrite(relay4, HIGH);
  digitalWrite(relay5, HIGH);
  digitalWrite(relay6, HIGH);
  digitalWrite(relay7, HIGH);



  // Łączenie z Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED && i < 18) {
    delay(10000);
    Serial.println("Łączenie z Wi-Fi...");
    i++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Połączono z Wi-Fi");
    Serial.print("Adres IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Nie udało się połączyć z Wi-Fi, wczytywanie danych z EEPROM");

    // Wczytywanie danych z EEPROM przy starcie, gdy połączenie Wi-Fi się nie powiedzie
    Variables savedVar;
    EEPROM.get(0, savedVar);
    Serial.println("Wczytane dane z EEPROM:");
    Serial.print("Temp: ");
    Serial.println(savedVar.c_temp);
    Serial.print("Hum: ");
    Serial.println(savedVar.c_hum);
    Serial.print("Light: ");
    Serial.println(savedVar.c_light ? "On" : "Off");
  }


}

void s_encode(String mess) {
  int Delimiter_1 = mess.indexOf('|');
  int Delimiter_2 = mess.indexOf('|', Delimiter_1 + 1);

  if (Delimiter_1 == -1 || Delimiter_2 == -1) {
    Serial.println("Nieprawidłowy format wiadomości");
    return;
  }

  String t_temp = mess.substring(0, Delimiter_1);
  String t_hum = mess.substring(Delimiter_1 + 1, Delimiter_2);
  String t_light = mess.substring(Delimiter_2 + 1);

  float s_temp = t_temp.toFloat();
  int s_hum = t_hum.toInt();
  bool s_light = (t_light.toInt() == 1);

  Variables var = {s_temp, s_hum, s_light};

  // Zapis do EEPROM
  EEPROM.put(0, var);
  Serial.println("Dane zapisane do EEPROM");
  applySettings(var);
}

void loop() {
  int result = dht11.readTemperatureHumidity(temperature, ad_value);
  humidity = analogRead(Moisture_ain);

  if (result == 0) {
    data = "temperature=" + String(temperature) + "&humidity=" + String(humidity);
    Serial.println(data);
  } else {
    Serial.println("Błąd odczytu z czujnika");
    return;
  }

  if (client.connect(server_ip, server_port)) {
    Serial.println("Połączono z serwerem");

    client.print(data);
    client.flush();

    delay(600);

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

    client.stop();
  } else {
    Serial.println("Nie udało się połączyć z serwerem. Odczyt danych z EEPROM.");
    Variables savedVar;
    EEPROM.get(0, savedVar);
    applySettings(savedVar); // Ustawienia przekaźników na podstawie EEPROM
  }

  delay(6000);
}
