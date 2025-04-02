from bs4 import BeautifulSoup, Tag


def extract_preview_blocks(preview_div):
	"""Extract block‐level text from a markdown-preview-view element."""
	blocks = []
	# Process only immediate block-level children
	for child in preview_div.find_all(recursive=False):
		if child.name in ["h1", "h2", "h3", "h4", "h5", "h6", "p"]:
			text = child.get_text(" ", strip=True)
			if text:
				blocks.append(text)
		elif child.name == "ul":
			for li in child.find_all("li", recursive=False):
				text = li.get_text(" ", strip=True)
				if text:
					blocks.append(text)
	return blocks


def extract_embed_content(embed):
	"""Extract content that is directly inside the embed (its title and preview)."""
	content = []
	# Get the title (if any)
	title_div = embed.find("div", class_="markdown-embed-title")
	if title_div:
		t = title_div.get_text(" ", strip=True)
		if t:
			content.append(t)
	# Get the preview view blocks (if any)
	preview_div = embed.find("div", class_="markdown-preview-view")
	if preview_div:
		blocks = extract_preview_blocks(preview_div)
		content.extend(blocks)
	# Remove duplicates (preserving order)
	deduped = []
	for line in content:
		if line and (not deduped or deduped[-1] != line):
			deduped.append(line)
	return deduped


def extract_sibling_content(sibling):
	"""Extract text from a sibling block (ignoring pre/code)."""
	if isinstance(sibling, Tag):
		if sibling.name in ["pre", "code"]:
			return []
		text = sibling.get_text(" ", strip=True)
		return [text] if text else []
	else:
		s = sibling.strip()
		return [s] if s else []


def parse_embeds_to_markdown(html):
	soup = BeautifulSoup(html, "html.parser")
	results = []
	embeds = soup.find_all("span", class_="internal-embed")
	for embed in embeds:
		src = embed.get("src", "")
		# First, get content from inside the embed
		embed_content = extract_embed_content(embed)
		# Then, get sibling content from the embed’s container (typically the parent <p>'s next siblings)
		sibling_content = []
		parent_p = embed.find_parent("p")
		if parent_p:
			for sib in parent_p.next_siblings:
				# Stop if we hit another embed block
				if isinstance(sib, Tag) and sib.find("span", class_="internal-embed"):
					break
				sibling_content.extend(extract_sibling_content(sib))
		# If both groups exist, add an empty string between for spacing
		combined = embed_content[:]
		if embed_content and sibling_content:
			combined.append("")
		combined.extend(sibling_content)
		# Remove any consecutive duplicates
		final_lines = []
		for line in combined:
			if not final_lines or final_lines[-1] != line:
				final_lines.append(line)
		results.append((src, final_lines))
	# Build the Markdown output
	md_lines = []
	for src, lines in results:
		md_lines.append(f"[{src}]:")
		for line in lines:
			if line == "":
				md_lines.append("")
			else:
				md_lines.append(f"  - {line}")
		md_lines.append("")
	return "\n".join(md_lines)
