from files.helpers.const import LOG_DIRECTORY

def log_file(log_str:str, log_filename="rdrama.log", append_newline=True):
	'''
	Simple method to log a string to a file
	'''
	log_target = f"{LOG_DIRECTORY}/{log_filename}"
	try:
		with open(log_target, "a", encoding="utf-8") as f:
			f.write(f"{log_str}{'\n' if append_newline else ''}")
	except Exception as e:
		print(f"Failed to log to file {log_target} due to {e.__class__.__name__}")
