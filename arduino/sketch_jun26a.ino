#include <SPI.h>
#include <Ethernet.h>
#include <DHT.h>

// Настройки Ethernet
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(10, 0, 0, 2);         
IPAddress gateway(10, 0, 0, 1);     
IPAddress subnet(255, 255, 255, 0);

EthernetServer server(5000);

// Пины
const int soilPin = A0;
const int mq135Pin = A1;  // <-- Новый пин CO2
const int dhtPin = 7;
#define DHTTYPE DHT11
DHT dht(dhtPin, DHTTYPE);

// Реле подключены к пинам 8, 9, 10, 11
const int relayPins[4] = {8, 9, 10, 11};

void setup() {
  Serial.begin(9600);
  Ethernet.begin(mac, ip, gateway, subnet);
  delay(1000);
  Serial.print("IP-адрес Arduino: ");
  Serial.println(Ethernet.localIP());
  server.begin();
  dht.begin();

  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);
  }
}

void loop() {
  EthernetClient client = server.available();
  if (client) {
    String command = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n') {
          command.trim();

          if (command == "GET") {
            float t = dht.readTemperature();
            float h = dht.readHumidity();
            int soil = analogRead(soilPin);
            int co2 = analogRead(mq135Pin);  // <-- Чтение CO2

            if (isnan(t) || isnan(h)) {
              client.println("{\"error\":\"DHT read failed\"}");
            } else {
              client.print("{\"temperature\":");
              client.print(t);
              client.print(",\"humidity_air\":");
              client.print(h);
              client.print(",\"humidity_soil\":");
              client.print(soil);
              client.print(",\"co2_adc\":");  // <-- Добавлено
              client.print(co2);
              client.println("}");
            }

          } else if (command.length() >= 3 && isDigit(command[0])) {
            int index = command[0] - '1';
            String action = command.substring(1);

            if (index >= 0 && index < 4) {
              if (action == "ON") {
                digitalWrite(relayPins[index], HIGH);
                client.println("{\"status\":\"Relay " + String(index + 1) + " ON\"}");
              } else if (action == "OFF") {
                digitalWrite(relayPins[index], LOW);
                client.println("{\"status\":\"Relay " + String(index + 1) + " OFF\"}");
              } else {
                client.println("{\"error\":\"Invalid action\"}");
              }
            } else {
              client.println("{\"error\":\"Invalid relay index\"}");
            }

          } else {
            client.println("{\"error\":\"Unknown command\"}");
          }

          break;
        } else {
          command += c;
        }
      }
    }
    client.stop();
  }
}
