from flask import Flask, request, abort
from datetime import datetime
import requests

app = Flask(__name__)
recognized = False                      # 是否识别到猫咪，会随着服务器EasyDL API返回的结果而改变（confidence大于0.8时为true）
# app.config['DEBUG'] = True
@app.route('/', methods = ['POST'])     # 服务器通过此API从摄像头接收照片
def get_photo():                        # 接收照片，并发送给EasyDL API进行识别，同时更新recognized的值
    if(request.content_type != 'image/jpeg' or not request.data):       # 请求数据异常则返回HTTP 415 (Unsupported Media Type)
        abort(415)
    img = request.data
    time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')                 # 当前系统时间，用于保存照片的文件命名
    with open(r'C:\Users\13595\Desktop\丁子杨\大一下\大作业服务器部署\pictures' + time + '.jpg', 'wb+') as file:
        file.write(img)
    ret = requests.post('http://192.168.0.103:24403', data=img).json()      # 向EasyDL API请求识别结果
    print(ret)
    confidence = 0.0                    # 识别结果中的置信度总和
    if 'results' in ret:
        for line in ret['results']:
            confidence += line['confidence']
    global recognized                   # 是否识别到猫咪
    recognized = (confidence >= 0.6)
    return 'success'

@app.route('/recognized', methods = ['GET', 'POST'])
def is_recognized():        # 服务器通过此API，向ESP32单片机返回是否识别成功猫咪的结果
    if recognized:          # true表示识别到猫咪
        return '1'
    else:
        return '0'

if __name__ == '__main__':
    app.run(host='0.0.0.0')