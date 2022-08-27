import random
import io
import json
import re
from .const import marsey_mappings

WORD_DELIMITER = " "
MAX_EMOJIS_PER_BLOCK = 2
BLOCK_REGEX = re.compile(r"\s*[^\s]*")
TRIM_REGEX = re.compile(r"^\W*|\W*$")

def split_into_blocks(text):
	if text == "" or BLOCK_REGEX.search(text) is None:
		return [text]
	blocks = []
	start = 0
	while start < len(text):
		block_match = BLOCK_REGEX.search(text, start)
		blocks.append(block_match.group())
		start = block_match.end()
	return blocks

def trim_nonalphabetical_characters(text):
	return TRIM_REGEX.sub("", text)

def marsify(text):
	blocks = split_into_blocks(text)
	new_blocks = []
	for i, block in enumerate(blocks):
		new_blocks.append(block)
		emojis = generate_emojis_from(block)
		if emojis:
			new_blocks.append(" " + emojis)
	return "".join(new_blocks)

def generate_emojis_from(block):
	trimmed_block = trim_nonalphabetical_characters(block)
	matching_emojis = get_matching_emojis(trimmed_block)
	emojis = []
	if matching_emojis:
		num_emojis = random.randint(0, MAX_EMOJIS_PER_BLOCK)
		for x in range(num_emojis):
			emojis.append(random.choice(matching_emojis))
	return "".join(emojis)

def get_matching_emojis(trimmed_block):
	key = get_alphanumeric_prefix(trimmed_block.lower())
	if key in  marsey_mappings:
		return  marsey_mappings[get_alphanumeric_prefix(key)]
	return []

def get_alphanumeric_prefix(s):
	i = 0
	while i < len(s) and s[i].isalnum():
		i += 1
	return s[:i]