import easyocr as eocr
from ultralytics import YOLO
import cv2

YOLO_INFER_SOURCE   =   'test_img.jpg'
YOLO_TRAIN_SOURCE   =   rf'dataset\data.yaml'
PLATE_CLASS_ID      =   0

class ANPRsystem():
    def __init__(self):
        self.detector   =   YOLO('yolo26n.pt')
        self.ocr        =   eocr.Reader(['en'],gpu=False)

    def __train__(self):
        self.detector.train(data=YOLO_TRAIN_SOURCE, epochs=50, imgsz=640)
        print('Training Complete')

    def detect_frame(self,frame):
        results = self.detector.predict(source=frame)
        return results

    def process_detections(self,detections):
        for r in detections: # core attributes of r - boxes, names
            if len(r.boxes) == 0:
                continue
            for box in r.boxes:
                if(PLATE_CLASS_ID not in r.boxes.cls):
                    continue
                return box.xyxy
            

    def crop_frame(self,frame,xyxy):
        h,w,_ = frame.shape
        xyxy=xyxy[0]
        xmin,ymin,xmax,ymax = map(int,xyxy)
        xmin = max(0, xmin)
        ymin = max(0, ymin)
        xmax = min(w, xmax)
        ymax = min(h, ymax)
        roi = frame[ymin:ymax,xmin:xmax]
        return roi 
    
    def process_roi(self,roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=8, fy=8, interpolation=cv2.INTER_LANCZOS4)
        gaussian_blur = cv2.GaussianBlur(resized, (0, 0), 3)
        sharpened = cv2.addWeighted(resized, 1.5, gaussian_blur, -0.5, 0)
        final_roi = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return final_roi

    def ocr_processing(self, processed_roi):
        result = self.ocr.readtext(processed_roi,allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return result[0][-2]

if '__main__' == __name__ :

    anpr = ANPRsystem()

    # anpr.__train__()
    test_image = cv2.imread(YOLO_INFER_SOURCE)
    detections = anpr.detect_frame(test_image)
    test_image = test_image
    xyxy = anpr.process_detections(detections)
    roi = anpr.crop_frame(test_image,xyxy)
    processed_roi = anpr.process_roi(roi=roi)
    final = anpr.ocr_processing(processed_roi)
    cv2.imshow("img",processed_roi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    