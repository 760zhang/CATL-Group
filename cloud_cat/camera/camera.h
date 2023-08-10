/* 头文件，包括常用函数、常量和全局变量的声明 */

// 防止头文件被重复包含
#ifndef CAMERA_H
#define CAMERA_H

#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoHttpClient.h>
#include <Ticker.h>
// Select camera model
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
#include "camera_pins.h"

extern WiFiClient wifi;
extern HttpClient client;
extern Ticker ticker;

const char ipAddress[] = "192.168.0.107";
const int port = 5000;
const char ssid[] = "TP-LINK_AFEB";
const char password[] = "15905238649";

camera_fb_t * capture();        // 拍照
bool get_api_result(camera_fb_t *);    // 请求识别结果
void process_error();           // 异常处理
void IRAM_ATTR onTimer();       // 计时器，每3s计数一次

#endif
