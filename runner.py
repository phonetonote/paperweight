from script.script import extract_links

pdf_links, arxiv_pdf_links, arxiv_abs_links = extract_links("data")

print("General PDF Links:")
for link in pdf_links:
    print(link)

print("\nArXiv PDF Links:")
for link in arxiv_pdf_links:
    print(link)

print("\nArXiv Abstract Links:")
for link in arxiv_abs_links:
    print(link)
