/*
    代码部分借鉴于翻海小分队猫猫投喂机的单片机端代码
*/
#include <Ticker.h>
#include <WiFi.h>
#include <ArduinoHttpClient.h>

const int ch_buzz=0, ch_motor=1, ch_steer=2;      // 蜂鸣器、电机、舵机绑定的ledc_channel
const int pin_red=32, pin_green=33;               // LED灯对应引脚
const int S_LEFT=7, S_FORWARD=21, S_RIGHT=33;     // 舵机方向参数
const char ipAddress[] = "192.168.0.107";
const int port = 5000;
const char ssid[] = "TP-LINK_AFEB";
const char password[] = "15905238649";

WiFiClient wifi;
HttpClient client = HttpClient(wifi, ipAddress, port);

void init();          // 初始化各引脚
void wifi_init();     // 初始化WiFi模块
void do_feed();       // 放粮部分
void blink();         // 指示灯闪烁，指示作用

/* 使指示灯闪烁，默认时长为500ms */
// 参数：闪烁时长（可选），以毫秒为单位，默认为500
void blink(int time = 500) {
  digitalWrite(pin_green, 0);
  digitalWrite(pin_red, 0);
  delay(time);
  digitalWrite(pin_green, 1);
  digitalWrite(pin_red, 1);
}

/* 机器启动时的初始化 */
void setup() {
  Serial.begin(115200);     // 连接电脑串口
  init();         // 初始化各引脚
  Serial.println(WiFi.macAddress());
  wifi_init();    // 初始化WiFi模块
  blink(700);
}

/* 循环向服务器请求识别结果 */
void loop() {
  client.get("/recognized");  // 向服务器请求识别结果
  int status = client.responseStatusCode();
  Serial.println(status);
  // response：服务器返回的识别结果，包含两种，'0'表示未识别到猫咪，'1'表示识别到猫咪
  String response = client.responseBody();
  if(response[0] == '1')    // 返回'1'则表示识别成功，开始放粮
    do_feed();
}

/* 放粮部分 */
void do_feed() {
  // 流程开始，发出3次警报声
  for(int i = 3; i > 0; i--){
    ledcWriteTone(ch_buzz, 494);
    delay(200);
    ledcWriteTone(ch_buzz, 0);
    if(i) delay(30);
  }
  // 驱动电机旋转3圈
  ledcWrite(ch_motor, 200);
  delay(1200);
  ledcWrite(ch_motor, 0);
  // 舵机转动90度
  ledcWrite(ch_steer, S_LEFT);
  delay(5000);
  ledcWrite(ch_steer, S_FORWARD);
  // 蜂鸣器长报警，流程结束
  ledcWriteTone(ch_buzz, 494);
  delay(2000);
  ledcWriteTone(ch_buzz, 0);
}

/* 各引脚的初始化部分 */
void init() {
  // 将对应引脚设为输出模式
  pinMode(25, OUTPUT);    // 蜂鸣器
  pinMode(26, OUTPUT);    // 电机
  pinMode(15, OUTPUT);    // 舵机
  pinMode(pin_red, OUTPUT);
  pinMode(pin_green, OUTPUT);
  // 关闭LED灯
  digitalWrite(pin_red, 1);
  digitalWrite(pin_green, 1);
  // 将引脚与对应ledc频道绑定
  ledcAttachPin(25, ch_buzz);
  ledcAttachPin(26, ch_motor);
  ledcAttachPin(15, ch_steer);
  // 对电机和舵机的ledc进行初始化
  ledcSetup(ch_motor, 50, 10);
  ledcSetup(ch_steer, 50, 8);
  // 设定舵机状态
  ledcWrite(ch_steer, S_FORWARD);   // 默认居中
}

/* WiFi模块的初始化 */
void wifi_init(){
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
