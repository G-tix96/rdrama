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
from shutil import copyfile
from files.classes.media import *
from files.helpers.cloudflare import purge_files_in_cache
from files.__main__ import db_session

def process_files():
	body = ''
	if request.files.get("file") and request.headers.get("cf-ipcountry") != "T1":
		files = request.files.getlist('file')[:4]
		for file in files:
			if file.content_type.startswith('image/'):
				name = f'/images/{time.time()}'.replace('.','') + '.webp'
				file.save(name)
				url = process_image(name, patron=g.v.patron)
				body += f"\n\n![]({url})"
			elif file.content_type.startswith('video/'):
				body += f"\n\n{SITE_FULL}{process_video(file)}"
			elif file.content_type.startswith('audio/'):
				body += f"\n\n{SITE_FULL}{process_audio(file)}"
			else:
				abort(415)
	return body


def process_audio(file):
	name = f'/audio/{time.time()}'.replace('.','')

	extension = file.filename.split('.')[-1].lower()
	if extension not in ['aac', 'amr', 'flac', 'm4a', 'm4b', 'mp3', 'ogg', 'wav']:
		extension = 'mp3'
	name = name + '.' + extension

	file.save(name)

	size = os.stat(name).st_size
	if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not g.v.patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
		os.remove(name)
		abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for {patron.lower()}s)")

	media = g.db.query(Media).filter_by(filename=name, kind='audio').one_or_none()
	if media: g.db.delete(media)

	media = Media(
		kind='audio',
		filename=name,
		user_id=g.v.id,
		size=size
	)
	g.db.add(media)

	return name


def webm_to_mp4(old, new, vid):
	tmp = new.replace('.mp4', '-t.mp4')
	subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-threads:v", "1", "-i", old, "-map_metadata", "-1", tmp], check=True, stderr=subprocess.STDOUT)
	os.replace(tmp, new)
	os.remove(old)
	purge_files_in_cache(f"{SITE_FULL}{new}")
	db = db_session()

	media = db.query(Media).filter_by(filename=new, kind='video').one_or_none()
	if media: db.delete(media)

	media = Media(
		kind='video',
		filename=new,
		user_id=vid,
		size=os.stat(new).st_size
	)
	db.add(media)
	db.commit()
	db.close()


def process_video(file):
	old = f'/videos/{time.time()}'.replace('.','')
	file.save(old)

	size = os.stat(old).st_size
	if (SITE_NAME != 'WPD' and
			(size > MAX_VIDEO_SIZE_MB_PATRON * 1024 * 1024
				or not g.v.patron and size > MAX_VIDEO_SIZE_MB * 1024 * 1024)):
		os.remove(old)
		abort(413, f"Max video size is {MAX_VIDEO_SIZE_MB} MB ({MAX_VIDEO_SIZE_MB_PATRON} MB for paypigs)")

	extension = file.filename.split('.')[-1].lower()
	if extension not in ['avi', 'mp4', 'webm', 'm4v', 'mov', 'mkv']:
		extension = 'mp4'
	new = old + '.' + extension

	if extension == 'webm':
		new = new.replace('.webm', '.mp4')
		copyfile(old, new)
		gevent.spawn(webm_to_mp4, old, new, g.v.id)
	else:
		subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-i", old, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", new], check=True)
		os.remove(old)

		media = g.db.query(Media).filter_by(filename=new, kind='video').one_or_none()
		if media: g.db.delete(media)

		media = Media(
			kind='video',
			filename=new,
			user_id=g.v.id,
			size=os.stat(new).st_size
		)
		g.db.add(media)

	return new



def process_image(filename=None, resize=0, trim=False, uploader=None, patron=False, db=None):
	size = os.stat(filename).st_size

	if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
		os.remove(filename)
		abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for paypigs)")

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


	if resize:
		if os.stat(filename).st_size > MAX_IMAGE_SIZE_BANNER_RESIZED_KB * 1024:
			os.remove(filename)
			abort(413, f"Max size for banners, sidebars, and badges is {MAX_IMAGE_SIZE_BANNER_RESIZED_KB} KB")

		if filename.startswith('files/assets/images/'):
			path = filename.rsplit('/', 1)[0]

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
				abort(409, "Image already exists!")

	db = db or g.db

	media = db.query(Media).filter_by(filename=filename, kind='image').one_or_none()
	if media: db.delete(media)

	media = Media(
		kind='image',
		filename=filename,
		user_id=uploader or g.v.id,
		size=os.stat(filename).st_size
	)
	db.add(media)

	return filename
