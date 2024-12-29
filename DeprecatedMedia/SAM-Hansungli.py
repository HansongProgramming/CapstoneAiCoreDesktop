import numpy as np
import matplotlib
from segment_anything import SamPredictor, sam_model_registry
import torch
from segment_anything.utils.transforms import ResizeLongestSide
from collections import defaultdict
from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import supervision as sv
from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator

def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)

def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels==1]
    neg_points = coords[labels==0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)

def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2))

image_org = cv2.imread(r'C:\Users\flore\OneDrive - University of the Cordilleras\CapstoneProject\3-Images\blood1.png')
image = cv2.cvtColor(image_org, cv2.COLOR_BGR2RGB)

# ---------------------------------

model_type = 'vit_b'
checkpoint = r"C:\Users\flore\Documents\Academics\CIT6\CapstoneRepository\2-Codes\Computer Vision\sam_vit_b_01ec64.pth"
device = 'cuda' if torch.cuda.is_available() else 'cpu'

sam_model = sam_model_registry[model_type](checkpoint=checkpoint)
sam_model.to(device)

predictor_tuned = SamPredictor(sam_model)

input_box = np.array([250, 400, 600, 630    ])

predictor_tuned.set_image(image)

masks_tuned,_, _= predictor_tuned.predict(
    box=input_box[None,:],
    multimask_output=False,
)

plt.figure(figsize=(10, 10))
plt.imshow(image)
show_mask(masks_tuned[0], plt.gca())
#show_points(input_point, input_label, plt.gca())
show_box(input_box, plt.gca())
plt.axis('on')
plt.show()