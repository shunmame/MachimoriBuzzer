#include <TinyGPS++.h>
#include <WioLTEforArduino.h>
#include <stdio.h>
#include <time.h>
#define BUZZER_PIN (WIOLTE_D38)
#define BUTTON_PIN (WIOLTE_A6)
#define RECEIVE_TIMEOUT (10000)
#define GPS_OVERFLOW_STRING "OVERFLOW"
#define DEFAULT_TIME (1200) //unit: s, not ms.
TinyGPSPlus gps;
WioLTE Wio;
int RegularTime = DEFAULT_TIME;
char data[100];
char url[200];
HardwareSerial* GpsSerial;
char GpsData[100];
char GpsDataLength;
char incoming;
int flag = 0;
struct tm now;
time_t saver = 0;
int r = 0;
double gpslat;
double gpslng;
int himo=0;
//////////////////////////////////////////
void GpsBegin(HardwareSerial* serial){
  GpsSerial = serial;
  GpsSerial->begin(9600);
  GpsDataLength = 0;
}
const char* GpsRead(){
  while (GpsSerial->available()) {
    incoming = GpsSerial->read();
    // SerialUSB.print(incoming);
    gps.encode(incoming);
    if (incoming == '\r') continue;
    if (incoming == '\n') {
      GpsData[GpsDataLength] = '\0';
      GpsDataLength = 0;
      if (gps.location.isUpdated()) {
        gpslat = gps.location.lat();
        gpslng = gps.location.lng();
        if(gpslat < -90 || gpslat > 90) continue;
        if(gpslng < -180 || gpslng > 180) continue;
        sprintf(data, "http://machimori.japanwest.cloudapp.azure.com/wio?lat=%.5f&lon=%.5f&parent_ID=P10000&buzzer_num=B10000&flag=%d", gpslat, gpslng, flag);
        return data;
      }
    }
    if (GpsDataLength > sizeof (GpsData) - 1) { // Overflow
      GpsDataLength = 0;
    }
    GpsData[GpsDataLength++] = incoming;
  }
  return NULL;
}
  
  
  
  
///////////////////////////////////////////////////////////
bool getWioTime(){
  time_t timer;
  if (!Wio.GetTime(&now)) {
    return false;
  }else{
    timer=mktime(&now);
    if(timer-saver>=RegularTime){
      saver = timer;
      RegularTime = DEFAULT_TIME;
      return true;
    }
    else{
      return false;
    }
  }
}
//////////////////////////////////////////////////////
void setup() {
  SerialUSB.println("");
  Wio.Init();
  Wio.PowerSupplyLTE(true);
  Wio.PowerSupplyGrove(true);
  delay(500);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  Wio.TurnOnOrReset();
  GpsBegin(&Serial);
  Wio.Activate("soracom.io", "sora", "sora");
  delay(5000);
  SerialUSB.println("setup-end");
}
void loop() {
  const char* gpsdata;
  if(getWioTime()){
    flag = 0;
    gpsdata = GpsRead();
    while(gpsdata == NULL){
      gpsdata = GpsRead();
    }
    SerialUSB.println(gpsdata);
    r = Wio.HttpGet(gpsdata, data,sizeof(data), 6000);
    SerialUSB.println(r);  
    SerialUSB.println(saver);
  }
  if(digitalRead(BUTTON_PIN) == HIGH && himo == 0){ 
    digitalWrite(BUZZER_PIN, HIGH);
    flag = 1;
    himo = 1;
    gpsdata = GpsRead();
    while(gpsdata == NULL){
      gpsdata = GpsRead();
    }
    SerialUSB.println(gpsdata);
    int r = Wio.HttpGet(gpsdata, data, sizeof(data), 6000); 
    SerialUSB.println(r);  
    SerialUSB.println("OK");
    
  }else{                                                                                                                                                                                                                                                                                                                                                                     
    Wio.LedSetRGB(255, 0, 0); 
  }
    if(digitalRead(BUTTON_PIN) == HIGH && himo == 1){
      digitalWrite(BUZZER_PIN,LOW);
      himo = 0;
      delay(1000);
    }
  if(r == 1){
    digitalWrite(BUZZER_PIN, HIGH);
    delay(2000);
    digitalWrite(BUZZER_PIN, LOW);
    r = 0;
  }
  else if(r == 3){
    RegularTime = 60;
    r = 0;
  }
}
