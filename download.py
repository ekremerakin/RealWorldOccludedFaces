import numpy as np
import cv2
import pickle
import os
import requests
import PIL.Image
import io
import argparse

from tqdm import tqdm

def main():
    dataset_dir = "images"
    if os.path.exists(dataset_dir) is False:
        os.mkdir(dataset_dir)
    
    sub_dataset_dir = ["masked", "sunglasses", "neutral"]

    for sub_dir in sub_dataset_dir:
        pkl_to_jpg(dataset_dir+'/'+sub_dir, sub_dir)

def pkl_to_jpg(dataset_dir, sub_dir):
    root_folder = dataset_dir
    files = os.listdir("ROF/"+sub_dir)

    if os.path.exists(root_folder) is False:
        os.mkdir(root_folder)

    for n in range(len(files)):
        name = files[n]
        target_folder = os.path.join(root_folder, name[:-4])
        index = 1
        if os.path.exists(target_folder) is False:
            os.mkdir(target_folder)
        
        with open(os.path.join("ROF/"+sub_dir, name), "rb") as f:
            annots = pickle.load(f)
        
        for key in annots:
            url = annots[key]['url']
            try:
                image_content = requests.get(url, timeout=4).content
            except Exception as e:
                print(f"[ERROR] - Could not download {url} - {e}")
            

            try:
                image_file = io.BytesIO(image_content)
                image = PIL.Image.open(image_file).convert('RGB')
            except Exception as e:
                continue

            cv2_image = np.array(image)
            
            try:
                ind = 1
                for face in annots[key]['faces']:
                    x,y,h,w = face['box']
                    face_img = cv2_image[y : np.min([y+w, cv2_image.shape[0]-1]), x : np.min([x+h, cv2_image.shape[1]-1])]
                    image = PIL.Image.fromarray(face_img)
                    with open(os.path.join(target_folder, str(index).zfill(6) + ".jpg"), "wb") as f:
                        image.save(f, "JPEG", quality=85)   
                        print(f"[SAVED] {name} {str(index).zfill(6)}")
                        ind = ind + 1
                    index = index + 1
            except Exception as e:
                pass

if __name__ == '__main__':
    main()
    