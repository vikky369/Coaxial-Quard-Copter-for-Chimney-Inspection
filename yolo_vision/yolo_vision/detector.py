from ultralytics import YOLO

class YoloDetector:

    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame, conf=0.5)

        boxes = results[0].boxes

        selected_center = None
        label = None

        for box in boxes:
            cls_id = int(box.cls[0])

            # 0 = person
            if cls_id == 0:
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                selected_center = (cx, cy)
                label = "Person"

                break   # PRIORITY: person first

        # If no person found → pick first object
        if selected_center is None and len(boxes) > 0:
            box = boxes[0]

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            selected_center = (cx, cy)
            label = "Object"

        annotated = results[0].plot()

        return annotated, selected_center, label