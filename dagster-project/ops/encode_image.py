import cv2
import numpy as np

import torch
from transformers import AutoImageProcessor, AutoModel


def encode_image(image_path):
    """Calculate DINOv2 embedding for a single image"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "facebook/dinov2-small"
    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device)

    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        inputs = processor(images=img, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)

        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy().flatten()
        
        return embedding
    
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None


