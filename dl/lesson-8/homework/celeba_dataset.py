import os
import pandas as pd 
from PIL import Image
import torch
from torch.utils.data import Dataset


class CelebADataset(Dataset):
    def __init__(self, img_dir, attr_path, bbox_path, landmark_path, partition_path, split='train', transform=None):
        self.img_dir = img_dir
        self.transform = transform

        # 1. Read attributes
        attrs = pd.read_csv(attr_path, sep=r"\s+", skiprows=1)
        attrs.index = attrs.index.str.strip()
        if not attrs.index[0].endswith(".jpg"):
            attrs.index = attrs.index + ".jpg"

        # 2. Read bounding boxes
        bbox = pd.read_csv(bbox_path, sep=r"\s+", skiprows=1)
        bbox.index = bbox.index.map(str).str.strip()
        if not bbox.index[0].endswith(".jpg"):
            bbox.index = bbox.index + ".jpg"

        # 3. Read landmarks
        landmarks = pd.read_csv(landmark_path, sep=r"\s+", skiprows=1)
        landmarks.index = landmarks.index.map(str).str.strip()
        if not landmarks.index[0].endswith(".jpg"):
            landmarks.index = landmarks.index + ".jpg"

        # 4. Read partition file
        parts = pd.read_csv(partition_path, sep=r"\s+",
                            header=None, names=['image_id', 'split'])
        parts["image_id"] = parts["image_id"].str.strip()

        # Merge all tables
        df = parts.merge(attrs, left_on='image_id', right_index=True)
        df = df.merge(bbox, left_on='image_id', right_index=True, suffixes=('', '_bbox'))
        df = df.merge(landmarks, left_on='image_id', right_index=True, suffixes=('', '_lm'))

        # Filter split
        split_map = {"train": 0, "val": 1, "test": 2}
        df = df[df["split"] == split_map[split]]

        self.image_names = df["image_id"].values

        # Attributes (40 columns)
        with open(attr_path, "r") as f:
            lines = f.readlines()
        attr_cols = lines[1].split()  # second line has the 40 attribute names

        self.attrs = ((df[attr_cols].values + 1) // 2).astype("float32")


        # Bounding boxes
        bbox_cols = ["x_1", "y_1", "width", "height"]
        self.bbox = df[bbox_cols].values.astype("float32")

        # Landmarks (10 values)
        lm_cols = ["lefteye_x", "lefteye_y", "righteye_x", "righteye_y",
                   "nose_x", "nose_y", "leftmouth_x", "leftmouth_y",
                   "rightmouth_x", "rightmouth_y"]
        self.landmarks = df[lm_cols].values.astype("float32")

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_name = self.image_names[idx]
        img_path = os.path.join(self.img_dir, img_name)
        image = Image.open(img_path).convert('RGB')

        orig_w, orig_h = image.size  # (178, 218)

        bbox = self.bbox[idx].copy()
        landmarks = self.landmarks[idx].copy()

        if self.transform:
            image = self.transform(image)
            new_w, new_h = 128, 128  # because we resize to (128,128)
            scale_x, scale_y = new_w / orig_w, new_h / orig_h

            # scale bbox and landmarks
            bbox[0] *= scale_x
            bbox[1] *= scale_y
            bbox[2] *= scale_x
            bbox[3] *= scale_y
            landmarks[0::2] *= scale_x
            landmarks[1::2] *= scale_y

        attr = torch.tensor(self.attrs[idx])
        bbox = torch.tensor(bbox)
        landmarks = torch.tensor(landmarks)

        return {
            'image': image,
            'attributes': attr,
            'bbox': bbox,
            'landmarks': landmarks
        }
