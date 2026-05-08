from textnode import TextNode, TextType
from htmlnode import HTMLNode, ParentNode, LeafNode
from markdownfuncs import extract_markdown_images, extract_markdown_links, markdown_to_blocks, block_to_block_type, BlockType

def main():

    print(TextNode("Random Stuff", TextType.LINK, "https://www.amigaforever.com"))

def text_node_to_html_node(text_node):

    value = text_node.text
    props = None
    if text_node.text_type == TextType.TEXT:
        tag = None
    if text_node.text_type == TextType.BOLD:
        tag = "b"
    if text_node.text_type == TextType.ITALIC:
        tag = "i"
    if text_node.text_type == TextType.CODE:
        tag = "code"
    if text_node.text_type == TextType.LINK:
        tag = "a"
        props = {"href": text_node.url}
    if text_node.text_type == TextType.IMAGE:
        tag = "img"
        value = ""
        props = {"src": text_node.url, "alt": text_node.text}
    if text_node.text_type not in TextType:
        raise Exception("Invalid text type.")
   
    return LeafNode(tag, value, props)

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            count = node.text.count(delimiter)
            if count % 2 > 0:
                raise Exception(f"Missing closing {delimiter}")
            parts = node.text.split(delimiter)
            for i, part in enumerate(parts):
                if part == "":
                    continue
                if i % 2 == 0:
                    new_nodes.append(TextNode(part, TextType.TEXT))
                else:
                    new_nodes.append(TextNode(part, text_type))
    return new_nodes
            
def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text == "":
            continue
        elif node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            remaining_text = node.text
            image_tuples = extract_markdown_images(remaining_text)
            if len(image_tuples) == 0:
                new_nodes.append(node)
                continue
            for tuple in image_tuples:
                sections = remaining_text.split(f"![{tuple[0]}]({tuple[1]})", 1)
                if sections[0] != "":
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(tuple[0], TextType.IMAGE, tuple[1]))
                remaining_text = sections[1]
            if remaining_text != "":
                new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text == "":
            continue
        elif node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            remaining_text = node.text
            link_tuples = extract_markdown_links(remaining_text)
            if len(link_tuples) == 0:
                new_nodes.append(node)
                continue
            for tuple in link_tuples:
                sections = remaining_text.split(f"[{tuple[0]}]({tuple[1]})", 1)
                if sections[0] != "":
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(tuple[0], TextType.LINK, tuple[1]))
                remaining_text = sections[1]
            if remaining_text != "":
                new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    new_nodes = [TextNode(text, TextType.TEXT)]
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    return new_nodes

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    return [text_node_to_html_node(node) for node in text_nodes]

def quote_to_html_node(block):
    split_block = block.split("\n")
    clean_block = []
    for line in split_block:
        clean_block.append(line.replace(">", "", 1).lstrip())
    text = " ".join(clean_block)
    return ParentNode("blockquote", None, text_to_children(text))

def markdown_to_html_node(markdown):
    nodes = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.QUOTE:
            nodes.append(quote_to_html_node(block))


if __name__ == "__main__":
    main()