import os
from markdown_blocks import markdown_to_html_node, extract_title

def generate_page(from_path, template_path, dest_path):
    print(f"Generating a page from {from_path} to {dest_path} using {template_path}.")
    with open(from_path, encoding="utf-8") as f:
        md = f.read()
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    new_node = markdown_to_html_node(md)
    new_html = new_node.to_html()
    title = extract_title(md)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", new_html)
    dest = os.path.dirname(dest_path)
    if not os.path.exists(dest):
        os.makedirs(dest)
    with open(dest_path, 'w', encoding="utf-8") as f:
        f.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    if not os.path.exists(dest_dir_path):
        os.mkdir(dest_dir_path)
    content = os.listdir(dir_path_content)
    for entry in content:
        from_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)
        if os.path.isfile(from_path):
            dest_path = dest_path.replace(".md", ".html")
            generate_page(from_path, template_path, dest_path)
        else:
            generate_pages_recursive(from_path, template_path, dest_path)


