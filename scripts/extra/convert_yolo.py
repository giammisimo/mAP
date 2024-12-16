import sys
import os
import glob
from PIL import Image
import argparse

def convert_yolo_coordinates_to_voc(x_c_n, y_c_n, width_n, height_n, img_width, img_height):
  ## remove normalization given the size of the image
  x_c = float(x_c_n) * img_width
  y_c = float(y_c_n) * img_height
  width = float(width_n) * img_width
  height = float(height_n) * img_height
  ## compute half width and half height
  half_width = width / 2
  half_height = height / 2
  ## compute left, top, right, bottom
  ## in the official VOC challenge the top-left pixel in the image has coordinates (1;1)
  left = int(x_c - half_width) + 1
  top = int(y_c - half_height) + 1
  right = int(x_c + half_width) + 1
  bottom = int(y_c + half_height) + 1
  return left, top, right, bottom

parser = argparse.ArgumentParser(description="")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--ground-truth', help='Path to the yolo ground truth')
group.add_argument('--detection-results', help='Path to the yolo detection results')
parser.add_argument('--images', help='Path to the images used',required=True)
parser.add_argument('--out', help='Output path',required=True)
args = parser.parse_args()
print(args)

path = None
if args.ground_truth:
    print('ground')
    files = os.listdir(args.ground_truth)
    path = args.ground_truth
else:
    print('detection')
    files = os.listdir(args.detection_results)
    path = args.detection_results

if len(files) == 0:
    print('No label files found')
    exit(-1)

for txt_file in files:
    basename = txt_file.removesuffix('.txt')
    
    for image_name in os.listdir(args.images):
        if image_name.startswith(basename):
            img = Image.open(args.images + '/' + image_name)
            img_width, img_height = img.size
            break
    else:
        ## image not found
        print("Error: image not found, corresponding to " + basename)
        exit(-2)

    with open(path + '/' + txt_file) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    with open(args.out + '/' + txt_file, "w") as new_f:
        for line in content:
            #obj_id, x_c_n, y_c_n, width_n, height_n = line.split()
            #obj_name = obj_list[int(obj_id)]
            params = line.split(' ')
            #left, top, right, bottom = convert_yolo_coordinates_to_voc(x_c_n, y_c_n, width_n, height_n, img_width, img_height)
            left, top, right, bottom = convert_yolo_coordinates_to_voc(params[1], params[2], params[3], params[4], img_width, img_height)

            #new_f.write(obj_name + " " + str(left) + " " + str(top) + " " + str(right) + " " + str(bottom) + '\n')
            if args.ground_truth:
                new_f.write("{} {} {} {} {}\n".format(params[0], left, top, right, bottom))
            else:
                new_f.write("{} {} {} {} {} {}\n".format(params[0], float(params[5]), left, top, right, bottom))
    
print(f"Conversion completed! {len(files)} files")