import sys
import os
import glob
import cv2
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
parser.add_argument('--yolo_in', help='Path to the yolo results')
parser.add_argument('--images', help='Path to the images used')
parser.add_argument('--out', help='Output path')
args = parser.parse_args()


# read the class_list.txt to a list
with open("class_list.txt") as f:
  obj_list = f.readlines()
## remove whitespace characters like `\n` at the end of each line
  obj_list = [x.strip() for x in obj_list]

# create VOC format files
txt_list = glob.glob(f'{args.yolo_in}/*.txt')
if len(txt_list) == 0:
  print("Error: no .txt files found in ground-truth")
  exit(-1)
  
for tmp_file in txt_list:
  txt_name = str(tmp_file.split("/")[-1])
  image_name = txt_name.removesuffix(".txt")
  print(image_name)
  ## check if image exists
  for fname in os.listdir(args.images):
    if fname.startswith(image_name):
      ## image found
      print(fname)
      img = cv2.imread(args.images + '/' + fname)
      ## get image width and height
      img_height, img_width = img.shape[:2]
      break
  else:
    ## image not found
    print("Error: image not found, corresponding to " + tmp_file)
    sys.exit()
  # 2. open txt file lines to a list
  with open(tmp_file) as f:
    content = f.readlines()
  ## remove whitespace characters like `\n` at the end of each line
  content = [x.strip() for x in content]
  # 3. create new file (VOC format)
  with open(args.out + '/' + txt_name, "w") as new_f:
    for line in content:
      ## split a line by spaces.
      ## "c" stands for center and "n" stands for normalized
      obj_id, x_c_n, y_c_n, width_n, height_n = line.split()
      obj_name = obj_list[int(obj_id)]
      left, top, right, bottom = convert_yolo_coordinates_to_voc(x_c_n, y_c_n, width_n, height_n, img_width, img_height)
      ## add new line to file
      #print(obj_name + " " + str(left) + " " + str(top) + " " + str(right) + " " + str(bottom))
      new_f.write(obj_name + " " + str(left) + " " + str(top) + " " + str(right) + " " + str(bottom) + '\n')
print(f"Conversion completed! {len(txt_list)} files")
