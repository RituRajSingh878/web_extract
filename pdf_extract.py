from pdf2image import convert_from_path
from link_utils import links
import cv2
import pytesseract
import urllib.request
import os
import requests
from urllib.parse import urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup
from PIL import Image
import json
import numpy


def download(url):
	
	# Requests URL and get response object 
	response = requests.get(url, allow_redirects=True) 
	
	open('filename.pdf', 'wb').write(response.content) 

	
def get_contour_precedence(contour, cols):
	tolerance_factor = 10
	origin = cv2.boundingRect(contour)
	return ((origin[1] // tolerance_factor) * tolerance_factor) * cols + origin[0]



def mark_region(image_path):
    
	im = cv2.imread(image_path)

	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	blur = cv2.GaussianBlur(gray, (9,9), 0)
	thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)
	
	# Dilate to combine adjacent text contours
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
	dilate = cv2.dilate(thresh, kernel, iterations=4)
	
	# Find contours, highlight text areas, and extract ROIs
	cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if len(cnts) == 2 else cnts[1]
	list(cnts).sort(key=lambda x:get_contour_precedence(x, im.shape[1]))
	
	
	line_items_coordinates = []
	for c in cnts:
		area = cv2.contourArea(c)
		x,y,w,h = cv2.boundingRect(c)

		if y >= 600 and x <= 1000:
			if area > 10000:
				
				line_items_coordinates.append([(x,y), (2200, y+h)])

		if y >= 2400 and x<= 2000:
			
			line_items_coordinates.append([(x,y), (2200, y+h)])


	return line_items_coordinates


def utl():
	path = 'x.jpg'
	
	line_items_coordinates = mark_region(path)
	
	image = cv2.imread(path)
	
	text = ""
	for c in line_items_coordinates:
		# print(c)
		# cropping image img = image[y0:y1, x0:x1]
		img = image[c[0][1]:c[1][1], c[0][0]:c[1][0]]
	
		# convert the image to black and white for better OCR
		ret,thresh1 = cv2.threshold(img,120,255,cv2.THRESH_BINARY)
	
		# pytesseract image to string to get results
		text += (pytesseract.image_to_string(thresh1, lang='hin', config='--psm 6'))
	# print(text)
	
	return text


def get_format():

	extract = []
	i = 0;
	for url in links:
		print("Formating Link ", i)
		i = i+1
		d = {}
		d.update({'page-url':url})
		
		if(url[-4:]=='.pdf'):
			d.update({'pdf-url':url})
		else:
			
			response = requests.get(url)
			soup= BeautifulSoup(response.text, "html.parser")
			for link in soup.select("a[href$='.pdf']"):	
				try:
					
					link = urljoin(url,link['href'])
					# urllib.request.urlretrieve(link, "filename.pdf")
					d.update({'pdf-url':link})
					break
				except:
					pass
			           	
	
		extract.append(d)
	
	
	
	return extract



def result():

	extr = get_format()
	i = 0;
	for dt in extr:
		print("Processing pdf No.", i)
		i=i+1
		lnk = dt['pdf-url']
		
		if(dt['pdf-url']==['page-url']):
			urllib.request.urlretrieve(lnk, "filename.pdf")
		else:
			download(lnk)	
		pages =  convert_from_path('filename.pdf', 200)
		text = ""
		for page in pages:
			page.save('x.jpg', 'JPEG')
			text += utl() # extract text
			
		dt.update({'pdf-content':text})
		# print(text)
		
			
	return extr
	
def get_result():
	res = result()
	
	with open('pdf-extract.json', 'w', encoding='utf-8') as f:
		json.dump(res, f, ensure_ascii=True, indent=4)
	return res	

get_result()