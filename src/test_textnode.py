import unittest

from textnode import TextNode, TextType
from main import text_node_to_html_node, split_nodes_delimiter, split_nodes_image, split_nodes_link, text_to_textnodes

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_ineq_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is also a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://boot.dev")
        node2 = TextNode("This is a text node", TextType.BOLD, "https://boot.dev")
        self.assertEqual(node, node2)

    
class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is an image", TextType.IMAGE, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev", "alt": "This is an image"},
        )

    def test_bold(self):
        node = TextNode("This is bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold")

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_bold(self):
        node = TextNode("**This** is bold", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This", TextType.BOLD),
            TextNode(" is bold", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_italic(self):
        node = TextNode("This _is_ italic", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This ", TextType.TEXT),
            TextNode("is", TextType.ITALIC),
            TextNode(" italic", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_not_text(self):
        node = TextNode("This is too bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [TextNode("This is too bold", TextType.BOLD)]
        self.assertEqual(new_nodes, expected)

    def test_no_delimiter_match(self):
        node = TextNode("This **is** totally** incorrect.", TextType.TEXT)
        with self.assertRaises(Exception) as ctx:
            split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertIn("closing", str(ctx.exception))

class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_not_text(self):
        node = TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")], new_nodes)

    def test_split_images_no_image(self):
        node = TextNode("This contains no images.", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("This contains no images.", TextType.TEXT)], new_nodes)

    def test_split_images_starts_with_image(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) is the beginning of the node",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" is the beginning of the node", TextType.TEXT),
            ],
            new_nodes,
        )

class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and another [second link](https://www.amigaforever.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://www.amigaforever.com"),
            ],
            new_nodes,
        )

    def test_split_images_not_text(self):
        node = TextNode("link", TextType.IMAGE, "https://boot.dev")
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("link", TextType.IMAGE, "https://boot.dev")], new_nodes)

class TestTexttoTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ], new_nodes,           
        )

    def test_text_textnodes_no_markdown(self):
        text = "This is a rather boring sentence with no markdown."
        new_nodes = text_to_textnodes(text)
        self.assertListEqual([TextNode("This is a rather boring sentence with no markdown.", TextType.TEXT)], new_nodes)

if __name__ == "__main__":
    unittest.main()