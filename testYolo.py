import torch
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
import numpy as np

checkpoint = "./checkpoints/sam2.1_hiera_large.pt"
model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
predictor = SAM2ImagePredictor(build_sam2(model_cfg, checkpoint))
test = np.array([(0,0),(0,0),(0,1313),(0,983)])

with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    predictor.set_image(r"C:\Users\Hans\Documents\AiCore Tester\NewDataStructure\DataTest\assets\floor.png")
    masks, _, _ = predictor.predict(test)