#include <ArduinoBLE.h>
#include <Arduino_LSM6DS3.h>

BLEService imuService("183A");

// BLE IMU Characteristic - custom 128-bit UUID, read and writable by central
BLEByteCharacteristic imuCharacteristic("87654321-4321-4321-4321-abc987654321", BLERead | BLEWrite);

void setup() {
  Serial.begin(9600);
  // while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
  }

  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");
  Serial.println();

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  // set advertised local name and service UUID:
  BLE.setLocalName("Nano RP2040");
  BLE.setAdvertisedService(imuService);

  // add the characteristic to the service
  imuService.addCharacteristic(imuCharacteristic);

  // add service
  BLE.addService(imuService);

  // set the initial value for the characteristic:
  imuCharacteristic.writeValue(0);

  // start advertising
  BLE.advertise();

  Serial.println("BLE LED Peripheral");
}

void loop() {
  // listen for BLE peripherals to connect:
  BLEDevice central = BLE.central();
  float gx, gy, gz;

  // if a central is connected to peripheral:
  if (central) {
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    // while the central is still connected to peripheral:
    while (central.connected()) {

      if (IMU.gyroscopeAvailable()) {
        IMU.readGyroscope(gx, gy, gz);
      }
      
      imuCharacteristic.writeValue(gy);   
      // Serial.print("Sent data: ");
      // Serial.println(gy);

      delay(1);
    }

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
    digitalWrite(LED_BUILTIN, LOW);         // will turn the LED off
  }
}