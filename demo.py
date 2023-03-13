from ultralytics import YOLO
import cv2
from PIL import Image

model = YOLO("bestPCB_YoloV8.pt")

# Load the image
img = cv2.imread(r"C:\Users\beono\OneDrive\Desktop\PCB_defect detector\images\WhatsApp Image 2023-03-13 at 09.26.59.jpg")

# Convert the image to RGB format
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Predict on the image
results = model.predict(source=img, save=True, project='output_images',  hide_conf=False)

# # Iterate over the results and draw bounding boxes
# for res in results:
#     for box in res["boxes"]:
#         x1, y1, x2, y2, conf, cls = box.int().tolist()
#         color = (0, 255, 0)  # Green color for the boxes
#         cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

# # Display the image
# cv2.imshow("Image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
