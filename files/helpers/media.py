from PIL import Image, ImageOps
from PIL.ImageSequence import Iterator
from webptools import gifwebp
import subprocess
import os
from flask import abort
import requests
import time
from .const import *


def process_audio(file):
	name = f'/audio/{time.time()}'.replace('.','') + '.' + file.filename.split('.')[-1].lower()
	file.save(name)

	if SITE_NAME == 'WPD' or os.stat(name).st_size > 8 * 1024 * 1024:
		with open(name, 'rb') as f:
			os.remove(name)
			req = requests.request("POST", "https://pomf2.lain.la/upload.php", files={'files[]': f}, timeout=20).json()
		return req['files'][0]['url']

	return f'{SITE_FULL}{name}'


def process_video(file):
	old = f'/videos/{time.time()}'.replace('.','')
	extension = file.filename.split('.')[-1]
	new = old + '.' + extension

	if extension == 'webm':
		file.save(new)
	else:
		file.save(old)
		os.system(f'ffmpeg -y -loglevel warning -i {old} -map_metadata -1 -c:v copy -c:a copy {new}')
		os.remove(old)

	size = os.stat(new).st_size
	if SITE_NAME == 'WPD' or os.stat(new).st_size > 8 * 1024 * 1024:
		with open(new, 'rb') as f:
			os.remove(new)
			req = requests.request("POST", "https://pomf2.lain.la/upload.php", files={'files[]': f}, timeout=20).json()
		return req['files'][0]['url']

	return f'{SITE_FULL}{new}'


def process_image(patron, filename=None, resize=0):
	size = os.stat(filename).st_size

	if size > 16 * 1024 * 1024 or not patron and size > 8 * 1024 * 1024:
		os.remove(filename)
		abort(413)

	i = Image.open(filename)

	if resize and i.width > resize:
		try: subprocess.call(["convert", filename, "-coalesce", "-resize", f"{resize}>", filename])
		except: pass
	elif i.format.lower() != "webp":

		exif = i.getexif()
		for k in exif.keys():
			if k != 0x0112:
				exif[k] = None
				del exif[k]
		i.info["exif"] = exif.tobytes()

		if i.format.lower() == "gif":
			gifwebp(input_image=filename, output_image=filename, option="-mixed -metadata none -f 100 -mt -m 6")
		else:
			i = ImageOps.exif_transpose(i)
			i.save(filename, format="WEBP", method=6)

	return filename