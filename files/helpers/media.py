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
import imagehash

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
	req = requests.post("https://pomf2.lain.la/upload.php", files={'files[]': file}, timeout=20).json()
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
			req = requests.post("https://pomf2.lain.la/upload.php", files={'files[]': f}, timeout=20).json()
		return req['files'][0]['url']

	return f'{SITE_FULL}{name}'


def process_video(file):
	old = f'/videos/{time.time()}'.replace('.','')
	file.save(old)

	extension = file.filename.split('.')[-1].lower()
	if extension not in ['avi', 'mp4', 'webm', 'm4v', 'mov', 'mkv']:
		extension = 'mp4'
	new = old + '.' + extension

	subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-i", old, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", new], check=True)
	os.remove(old)
	if os.stat(new).st_size > 8 * 1024 * 1024:
		with open(new, 'rb') as f:
			os.remove(new)
			req = requests.post("https://pomf2.lain.la/upload.php", files={'files[]': f}, timeout=20).json()
		return req['files'][0]['url']
	return f'{SITE_FULL}{new}'



def process_image(filename=None, resize=0, trim=False):
	size = os.stat(filename).st_size

	if size > 16 * 1024 * 1024 or not patron and size > 8 * 1024 * 1024:
		os.remove(filename)
		abort(413)

	i = Image.open(filename)

	if resize and i.width > resize:
		if trim and len(list(Iterator(i))) == 1:
			subprocess.run(["convert", filename, "-coalesce", "-trim", "-resize", f"{resize}>", filename])
		else:
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


	if resize in (300,400,1200):
		if os.stat(filename).st_size > 1 * 1024 * 1024:
			os.remove(filename)
			abort(413)

		if resize == 1200:
			path = f'files/assets/images/{SITE_NAME}/banners'
		elif resize == 400:
			path = f'files/assets/images/{SITE_NAME}/sidebar'
		else:
			path = f'files/assets/images/badges'

		hashes = {}

		for img in os.listdir(path):
			if resize == 400 and img in ('256.webp','585.webp'): continue
			img_path = f'{path}/{img}'
			if img_path == filename: continue
			img = Image.open(img_path)
			i_hash = str(imagehash.phash(img))
			if i_hash in hashes.keys():
				print(hashes[i_hash], flush=True)
				print(img_path, flush=True)
			else: hashes[i_hash] = img_path

		i = Image.open(filename)
		i_hash = str(imagehash.phash(i))
		if i_hash in hashes.keys():
			os.remove(filename)
			abort(417)

	return filename