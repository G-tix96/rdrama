from PIL import Image, ImageOps
from PIL.ImageSequence import Iterator
from webptools import gifwebp
import subprocess
import os
from flask import abort
import requests
import time
from .const import *

def process_video(file):
	name = f'/videos/{time.time()}'.replace('.','')
	file.save(name)
	os.system(f'ffmpeg -y -loglevel warning -i {name} -map_metadata -1 {name}.mp4')
	os.remove(name)

	size = os.stat(f'{name}.mp4').st_size

	with open(f"{name}.mp4", 'rb') as f:
		try: req = requests.request("POST", "https://pomf2.lain.la/upload.php", files={'files[]': f}, timeout=20).json()
		except requests.Timeout: return {"error": "Video upload timed out, please try again!"}
		try: url = req['files'][0]['url']
		except: return {"error": req['description']}
		return url

	if SITE_NAME != 'rDrama' or size > 8 * 1024 * 1024: os.remove(f"{name}.mp4")


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