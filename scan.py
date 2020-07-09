# imports
import cv2
import numpy as np 
from matplotlib import pyplot as plt 
import argparse
import os
import imutils 
from skimage.filters import threshold_local
from perspective import four_point_transform

# parsing arguments
parser = argparse.ArgumentParser()
parser.add_argument('-ipdir', '--input_dir', required=False, help='Path to the input dir')
parser.add_argument('-opdir', '--output_dir', required=False, help='Path to the output dir')
parser.add_argument('-opdirn', '--output_dir_name', required=False, help='Name of the output dir')

args = vars(parser.parse_args())


# print('Path to the input dir is {}'.format(args['input_dir']))
# print('Path to the output dir is {}'.format(args['output_dir']))

def test(img_path):

	# reding image
	image = cv2.imread(img_path)

	# validation
	if image is None:
		print('[ERROR] Image insertion failed...for ', filename)
		return None

	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height = 500)

		
	# converting the image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# applying gaussian blur
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	# finding edges using canny edge detection method
	edged = cv2.Canny(gray, 75, 200)

	# cv2.imshow('canny', edged)
	# cv2.waitKey(0)

	# finding th econtous in the image
	cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	# print('contours : ', cnts)

	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
	cnt = 0

	# loop over the contours
	for c in cnts:
		# finding the perimeter of the page
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)

		# cnt = approx
		if len(approx) == 4:
			cnt = approx
			break

	# drawing the contour of paper
	try:
		cv2.drawContours(image, [cnt], -1, (0, 255, 0), 2)

	except:
		print("[ERROR] Couldn't find document properly...")
		return None
	
	# cv2.imshow('scanned', image)

	# applying for-point-transformation
	warped = four_point_transform(orig, cnt.reshape(4, 2) * ratio)

	# for scanned effect
	warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
	T = threshold_local(warped, 11, offset = 10, method = "gaussian")
	warped = (warped > T).astype("uint8") * 255

		
	# saving image to the output directory
	# cv2.imwrite(os.path.join(dir_path, 'scanned'+filename), imutils.resize(warped, height=650))
	return imutils.resize(warped, height=650)

def adjust(img_path):
	pass


# if args
if args['input_dir'] is not None:
	i_path = args['input_dir']
else:
	i_path = os.getcwd()
if args['output_dir'] is not None:
	o_path = args['output_dir']
else:
	o_path = os.getcwd()
if args['output_dir_name'] is not None:
	dir_path = args['output_dir_name']
else:
	dir_path = 'Docs'


# creating output dir
path = os.path.join(o_path, dir_path)
if not os.path.exists(path):
    os.mkdir(path)


# looping through the dir
for (dirpath, dirnames, filenames) in os.walk(i_path):
	# looping through files
	
	for filename in filenames:
		print('-------->', filename)

		# checking for images
		if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
			print('[WARNING] Skipping {} as it is not image...'.format(filename))
			continue
		
		# loading image
		print('path : ', os.path.join(i_path, filename))
		
		# # saving image to the output directory
		final = test(os.path.join(i_path, filename))

		# cv2.imshow('image', final)
		# cv2.waitKey(0)

		if final is not None:
			cv2.imwrite(os.path.join(dir_path, 'scanned_'+filename), final)
		# cv2.waitKey(0)

	break

# cv2.destroyAllWindows()