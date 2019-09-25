#include <TinyGPS++.h>
#include <WioLTEforArduino.h>
#include <stdio.h>
#include <time.h>

#define BUZZER_PIN (WIOLTE_D38)
#define BUTTON_PIN (WIOLTE_A6)
#define RECEIVE_TIMEOUT (10000)
#define REGULAR_TIME (60) //not ms.

TinyGPSPlus gps;
WioLTE Wio;


char data[100];
char url[200];
HardwareSerial* GpsSerial;
char GpsData[100];
char GpsDataLength;
char incoming;
int flag=0;
struct tm now;
time_t saver=0;


void GpsBegin(HardwareSerial* serial)
{
  GpsSerial = serial;
  GpsSerial->begin(9600);
  GpsDataLength = 0;
}

void GpsCheck() {
  incoming = GpsSerial->read();
  gps.encode(incoming);
 // if (gps.location.isUpdated()) {
        sprintf(url, "http://machimori.japanwest.cloudapp.azure.com/wio?lat=%.5f&lon=%.5f&parent_ID=P10000&buzzer_num=B10000&flag=%d",gps.location.lat(),gps.location.lng(),flag);
        SerialUSB.println(gps.location.lat());
        SerialUSB.println(gps.location.lng());
        SerialUSB.println(url);
 // }else{
 //   SerialUSB.println(###ERROR.notGPS###);
 // }
  
  
  int r = Wio.HttpGet(url, data,sizeof(data),6000);
  SerialUSB.println(r);
  SerialUSB.println("END");
  SerialUSB.println(data);
  if(r==1){
    digitalWrite(BUZZER_PIN,HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN,LOW);
  }
  SerialUSB.println("wio-end");
  delay(500);
}

///////////////////////////////////////////////////////////
bool getWioTime(){
  time_t timer;
  if (!Wio.GetTime(&now)) {
    SerialUSB.println("### ERROR! ###");
    return false;
  }else{
    timer=mktime(&now);
    if(timer-saver>=REGULAR_TIME){
      saver=timer;
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
  GpsBegin(&Serial);
  Wio.Init();
  Wio.PowerSupplyLTE(true);
  Wio.PowerSupplyGrove(true);
  delay(500);
  pinMode(BUZZER_PIN,OUTPUT);
  pinMode(BUTTON_PIN,INPUT);
  Wio.TurnOnOrReset();
  Wio.Activate("soracom.io", "sora", "sora");
  delay(5000);
  SerialUSB.println("setup-end");
}


void loop() {
  if(getWioTime()){
    flag = 0;
    GpsCheck();
    SerialUSB.println("OK");
    SerialUSB.println(saver);
  }
  if(digitalRead(BUTTON_PIN) == HIGH){ 
    flag = 1;
    digitalWrite(BUZZER_PIN,HIGH);
    Wio.LedSetRGB(0,255,0);
    delay(500);
    digitalWrite(BUZZER_PIN,LOW);
    delay(100);
    GpsCheck();
  }else{                                                                                                                                                                                                                                                                                                                                                                     
    Wio.LedSetRGB(255,0,0);
  }
}
