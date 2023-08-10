from flask import Flask, request, abort
from datetime import datetime
import requests
import cv2
import numpy as np
import time


def plot_one_box(x, img, color=None, label=None, line_thickness=None):
    tl = (
            line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1
    )  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(
            img,
            label,
            (c1[0], c1[1] - 2),
            0,
            tl / 3,
            [225, 255, 255],
            thickness=tf,
            lineType=cv2.LINE_AA,
        )


def post_process_opencv(outputs, model_h, model_w, img_h, img_w, thred_nms, thred_cond):
    conf = outputs[:, 4].tolist()
    c_x = outputs[:, 0] / model_w * img_w
    c_y = outputs[:, 1] / model_h * img_h
    w = outputs[:, 2] / model_w * img_w
    h = outputs[:, 3] / model_h * img_h
    p_cls = outputs[:, 5:]
    if len(p_cls.shape) == 1:
        p_cls = np.expand_dims(p_cls, 1)
    cls_id = np.argmax(p_cls, axis=1)

    p_x1 = np.expand_dims(c_x - w / 2, -1)
    p_y1 = np.expand_dims(c_y - h / 2, -1)
    p_x2 = np.expand_dims(c_x + w / 2, -1)
    p_y2 = np.expand_dims(c_y + h / 2, -1)
    areas = np.concatenate((p_x1, p_y1, p_x2, p_y2), axis=-1)
    print(areas.shape)
    areas = areas.tolist()
    ids = cv2.dnn.NMSBoxes(areas, conf, thred_cond, thred_nms)
    return np.array(areas)[ids], np.array(conf)[ids], cls_id[ids]


def infer_image(net, img0, model_h, model_w, thred_nms=0.4, thred_cond=0.5):
    img = img0.copy()
    img = cv2.resize(img, [model_h, model_w])
    blob = cv2.dnn.blobFromImage(img, scalefactor=1 / 255.0, swapRB=True)
    net.setInput(blob)
    outs = net.forward()[0]
    print(outs[0])
    det_boxes, scores, ids = post_process_opencv(outs, model_h, model_w, img0.shape[0], img0.shape[1], thred_nms,
                                                 thred_cond)
    return det_boxes, scores, ids

app = Flask(__name__)
recognized = False
# app.config['DEBUG'] = True
@app.route('/', methods = ['POST'])
def get_photo():
    dic_labels = {0: 'cat',
                  1: 'buzzer',
                  2: 'teeth'}

    model_h = 640
    model_w = 640
    file_model = 'C:/Users/13595/Desktop/yolov5_train_cat/yolov5-master/runs/train/exp14/weights/best.onnx'
    net = cv2.dnn.readNet(file_model)

    if(request.content_type != 'image/jpeg' or not request.data):       # 请求数据异常则返回HTTP 415 (Unsupported Media Type)
        abort(415)
    img = request.data
    time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')                 # 当前系统时间，用于保存照片的文件命名
    with open(time + '.jpg', 'wb+') as file:
        file.write(img)
        img0 = cv2.imread('C:/Users/13595/Desktop/yolov5_train_cat/yolov5-master/' + time + ".jpg")
        det_boxes, scores, ids = infer_image(net, img0, model_h, model_w, thred_nms=0.4, thred_cond=0.5)
        print(scores[0])



        # for box, score, id in zip(det_boxes, scores, ids):
        #     label = '%s:%.2f' % (dic_labels[id], score)
        #     plot_one_box(box.astype(np.int16), img0, color=(255, 0, 0), label=label, line_thickness=None)
        # cv2.imshow('img', img0)
        #
        # cv2.waitKey(1000)

        global recognized  # 是否识别到猫咪
        recognized = (scores[0] >= 0.6)
        return 'success'

@app.route('/recognized', methods = ['GET', 'POST'])
def is_recognized():        # 服务器通过此API，向ESP32单片机返回是否识别成功猫咪的结果
    if recognized:          # true表示识别到猫咪
        return '1'
    else:
        return '0'

if __name__ == '__main__':
    app.run(host='0.0.0.0')