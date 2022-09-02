from PIL import Image, ImageOps
from PIL.ImageSequence import Iterator
from webptools import gifwebp
import subprocess
import os
from flask import abort, g
import requests
import time
from .const import *
import gevent


def process_files():
	body = ''
	if request.files.get("file") and request.headers.get("cf-ipcountry") != "T1":
		files = request.files.getlist('file')[:4]
		for file in files:
			if file.content_type.startswith('image/'):
				name = f'/images/{time.time()}'.replace('.','') + '.webp'
				file.save(name)
				url = process_image(name)
				body += f"\n\n![]({url})"
			elif file.content_type.startswith('video/'):
				body += f"\n\n{process_video(file)}"
			elif file.content_type.startswith('audio/'):
				body += f"\n\n{process_audio(file)}"
			else:
				abort(415)
	return body


def process_other(file):
	req = requests.request("POST", "https://pomf2.lain.la/upload.php", files={'files[]': file}, timeout=20).json()
	return req['files'][0]['url']


def process_audio(file):
	name = f'/audio/{time.time()}'.replace('.','')

	extension = file.filename.split('.')[-1].lower()
	if extension not in ['aac', 'amr', 'flac', 'm4a', 'm4b', 'mp3', 'ogg', 'wav']:
		extension = 'mp3'
	name = name + '.' + extension

	file.save(name)

	if os.stat(name).st_size > 8 * 1024 * 1024:
		with open(name, 'rb') as f:
			os.remove(name)
			req = requests.request("POST", "https://pomf2.lain.la/upload.php",
				files={'files[]': f}, timeout=20).json()
		return req['files'][0]['url']

	return f'{SITE_FULL}{name}'


def webm_to_mp4(old, new):
	subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-i", old, "-map_metadata", "-1", new], check=True, stderr=subprocess.STDOUT)
	os.remove(old)
	requests.post(f'https://api.cloudflare.com/client/v4/zones/{CF_ZONE}/purge_cache', headers=CF_HEADERS, data={'files': [f"{SITE_FULL}{new}"]}, timeout=5)

def process_video(file):
	old = f'/videos/{time.time()}'.replace('.','')
	file.save(old)

	extension = file.filename.split('.')[-1].lower()
	if extension not in ['avi', 'mp4', 'webm', 'm4v', 'mov', 'mkv']:
		extension = 'mp4'
	new = old + '.' + extension

	if file.filename.split('.')[-1].lower() == 'webm':
		file.save(new)
		if os.stat(new).st_size > 16 * 1024 * 1024:
			abort(418)
		else:
			gevent.spawn(webm_to_mp4, old, new)
			return f'{SITE_FULL}{new}'
	else:
		subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-i", old, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", new], check=True)
		os.remove(old)
		if os.stat(new).st_size > 8 * 1024 * 1024:
			with open(new, 'rb') as f:
				os.remove(new)
				req = requests.request("POST", "https://pomf2.lain.la/upload.php",
					files={'files[]': f}, timeout=20).json()
			return req['files'][0]['url']
		return f'{SITE_FULL}{new}'



def process_image(filename=None, resize=0):
	size = os.stat(filename).st_size

	if resize != 100:
		if size > 16 * 1024 * 1024 or not patron and size > 8 * 1024 * 1024:
			os.remove(filename)
			abort(413)

	i = Image.open(filename)

	if resize and i.width > resize:
		try: subprocess.run(["convert", filename, "-coalesce", "-resize", f"{resize}>", filename])
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
			i.save(filename, format="WEBP", method=6, quality=88)

	return filename
