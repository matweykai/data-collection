from pathlib import Path

from ultralytics import YOLO
import dagster as dg
import math


@dg.op
def predict_with_yolo(model_path: str, images_folder: str):
    model = YOLO(model_path)

    images_folder_path = Path(images_folder)
    preds = []
    
    for img_path in images_folder_path.rglob('*.jpg'):
        pred_list = model.predict(source=img_path)

        img_preds = []

        for temp_pred in pred_list:
            for box in temp_pred.boxes:
                class_id = int(box.cls)
                class_name = model.names[class_id]

                if class_name == 'dog':
                    confidence = float(box.conf)
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                    img_preds.append({
                        'bbox': bbox,
                        'confidence': confidence,
                        'path': str(img_path),
                    })

        preds.append(img_preds)

    return preds


@dg.op
def calculate_entropy(preds: list[list[dict]]):
    result = []

    for temp_pred in preds:
        pred_conf = temp_pred[0]['confidence']
        temp_pred['entropy'] = -math.log(pred_conf) * pred_conf
        result.append(temp_pred)

    return result
