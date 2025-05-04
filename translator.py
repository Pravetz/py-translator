import os
import sys
import re
from googletrans import Translator
from datetime import datetime
from time import sleep
import httpx

def safe_translate(translator, text, dest, retries=3, delay=1):
	for attempt in range(retries):
		try:
			translated = translator.translate(text, dest=dest)
			if translated and translated.text:
				return translated.text
			else:
				raise ValueError("Received None from translator.")
		except Exception as e:
			print(f"Retry attempt {attempt + 1} failed: {e}")
			if attempt < retries - 1:
				sleep(delay)
				delay *= 2
			else:
				print(f"Can't translate after {retries} attempts, return None.")
				return None

def open_text(path):
	ftext = ""
	with open(path, 'r', encoding = 'utf-8') as file:
		ftext = file.read()
	return ftext

def write_text(text, path, translator_out_path, dir_name):
	filename = os.path.basename(path).split(os.sep)[-1]
	if not os.path.exists(translator_out_path + dir_name):
		os.makedirs(translator_out_path + dir_name)
	with open(translator_out_path + dir_name + filename, 'a', encoding = 'utf-8') as file:
		file.write(text)

def find_delim(text):
	for char in ['.', '?', '!', '\n', '\v']:
		dotpos = text.rfind(char)
		if dotpos != -1:
			return dotpos
	return -1

def translate_lines(translator, path, translator_out_path, dir_name, destl, retries):
	ftext = ""
	queue = ""
	dotpos = 0
	with open(path, 'r', encoding='utf-8') as file:
		while True:
			rd = file.read(3000 - len(ftext))
			if not rd:
				break
			ftext += rd
			dotpos = find_delim(ftext)
			if dotpos != -1:
				queue = ftext[:dotpos + 1]
				ftext = ftext[dotpos + 1:]
				
				translated_text = safe_translate(translator, queue, dest=destl, retries=retries)
				if translated_text:
					write_text(translated_text, path, translator_out_path, dir_name)
			sleep(0.35)
	sleep(0.25)

if __name__ == "__main__":
	fpath_list = []
	dpath_list = []
	translator_out_path = f"outputs{os.sep}"
	lines = False
	extended_out_path = False
	ignore_files = []
	destl = 'uk'
	retries = 3
	
	if len(sys.argv) == 1:
		print(f"""
Usage: {sys.argv[0]} <parameters>
Parameters:
-f <path> = specify single file path.
	{sys.argv[0]} -f path{os.sep}to{os.sep}my{os.sep}file.txt
-d <path> = specify directory path.
	{sys.argv[0]} -d path{os.sep}to{os.sep}my{os.sep}dir{os.sep}
-o <path> = specify output directory path(must be located in outputs), if directory contains already translated files, they will be treated as already translated and skipped. It is useful when utility has crashed while translating a large dataset of texts to resume process from the break point.
	{sys.argv[0]} -o checkpoint{os.sep}
-l = save every translated line to a separate file.
-dl = specify destination language for translation(Ukrainian(\'uk\') by default)
-rc <integer> = specify translation retry count, if googletrans couldn\'t fetch it first time.""")
		exit()
	else:
		i = 1
		while i < len(sys.argv):
			if sys.argv[i] == "-f" and i + 1 < len(sys.argv):
				fpath_list.append(sys.argv[i + 1])
				i = i + 1
			elif sys.argv[i] == "-d" and i + 1 < len(sys.argv):
				dpath_list.append(sys.argv[i + 1])
				i = i + 1
			elif sys.argv[i] == "-l":
				lines = not lines
			elif sys.argv[i] == "-dl" and i + 1 < len(sys.argv):
				destl = sys.argv[i + 1]
				i += 1
			elif sys.argv[i] == '-o' and i + 1 < len(sys.argv):
				translator_out_path += sys.argv[i + 1]
				extended_out_path = True
				i += 1
			elif sys.argv[i] == '-rc':
				try:
					retries = int(sys.argv[i + 1])
				except:
					retries = 3
			
			i += 1
	
	if os.path.exists(translator_out_path) and extended_out_path:
		dir_list = os.listdir(translator_out_path)
		for entry in dir_list:
			if os.path.isdir(translator_out_path + entry):
				ignore_files.extend([f.split(os.sep)[-1] for f in os.listdir(translator_out_path + entry)])
			else:
				ignore_files.append(entry.split(os.sep)[-1])
	
	if not os.path.exists(translator_out_path):
		os.makedirs(translator_out_path)
	if not os.path.exists(translator_out_path + str(datetime.now()).replace(' ', '_').replace(':', '_').replace('.', '_')) and not extended_out_path:
		translator_out_path += str(datetime.now()).replace(' ', '_').replace(':', '_').replace('.', '_') + os.sep
		os.makedirs(translator_out_path)
	
	translator = Translator()
	for fpath in fpath_list:
		if fpath.split(os.sep)[-1] in ignore_files:
			continue
		print(f"Translating {fpath}...")
		if not lines:
			text_to_translate = open_text(fpath)
			translated_text = safe_translate(translator, text_to_translate, dest=destl, retries=retries)
			if translated_text:
				write_text(translated_text, fpath, translator_out_path, f"files{os.sep}")
			sleep(0.5)
		else:
			translate_lines(translator, fpath, translator_out_path, f"files{os.sep}", destl, retries)
	
	for dpath in dpath_list:
		print(f"Translating {dpath}...")
		dir_name = os.path.basename(os.path.normpath(dpath))
		filenames = []
		filetexts = []
		
		filetext = []
		filenames_batch = []
		lencounter = 0
		for filename in os.listdir(dpath):
			if filename.split(os.sep)[-1] in ignore_files:
				continue
			rd_text = open_text(os.path.join(dpath, filename))
			if len(rd_text) >= 1000:
				print(f"File \'{filename}\' is too large to be put into batch, translating separately...")
				translate_lines(translator, os.path.join(dpath, filename), translator_out_path, f"files{os.sep}", destl, retries)
				continue
			
			if lencounter + len(rd_text) >= 14000:
				filenames.append(filenames_batch[:])
				filetexts.append(filetext[:])
				filetext.clear()
				filenames_batch.clear()
				lencounter = 0
			filetext.append(rd_text)
			filenames_batch.append(filename)
			lencounter += len(filetext[-1])
		
		if filetext:
			filenames.append(filenames_batch[:])
			filetexts.append(filetext[:])
			filetext.clear()
			filenames_batch.clear()
		
		for i, batch in enumerate(filetexts):
			print(f"\tTranslating a batch of {len(batch)} texts")
			translated_texts = translator.translate(batch, dest=destl)
			
			for j, translated in enumerate(translated_texts):
				write_text(translated.text, filenames[i][j], translator_out_path, dir_name + os.sep)
