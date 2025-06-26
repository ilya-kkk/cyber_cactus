#include <SPI.h>
#include <Ethernet.h>
#include <DHT.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(10, 0, 0, 2);          // IP Arduino
IPAddress gateway(10, 0, 0, 1);     // IP Raspberry Pi
IPAddress subnet(255, 255, 255, 0);

EthernetServer server(5000);

const int soilPin = A0;
const int dhtPin = 4;
#define DHTTYPE DHT11
DHT dht(dhtPin, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Ethernet.begin(mac, ip, gateway, subnet);  // Статический IP
  delay(1000);
  Serial.print("IP-адрес Arduino: ");
  Serial.println(Ethernet.localIP());
  server.begin();
  dht.begin();
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

            if (isnan(t) || isnan(h)) {
              client.println("{\"error\":\"DHT read failed\"}");
            } else {
              client.print("{\"temperature\":");
              client.print(t);
              client.print(",\"humidity_air\":");
              client.print(h);
              client.print(",\"humidity_soil\":");
              client.print(soil);
              client.println("}");
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
