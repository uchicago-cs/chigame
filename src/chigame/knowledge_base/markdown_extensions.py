import re
from xml.etree import ElementTree

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor


class SectionWrapperTreeprocessor(Treeprocessor):
    def run(self, root):
        # Find all headers
        headers = (
            root.findall(".//h1")
            + root.findall(".//h2")
            + root.findall(".//h3")
            + root.findall(".//h4")
            + root.findall(".//h5")
            + root.findall(".//h6")
        )

        for header in headers:
            # Create a new section div
            section_div = ElementTree.Element("div")
            section_div.set("class", "kb-section")
            section_div.set("data-section-id", header.text.strip().lower().replace(" ", "-"))

            # Find the parent of the header
            def find_parent(element, tree):
                for child in tree:
                    if child is element:
                        return tree
                    result = find_parent(element, child)
                    if result is not None:
                        return result
                return None

            parent = find_parent(header, root)
            if parent is None:
                continue

            # Get the index of the header in its parent
            header_index = list(parent).index(header)

            # Get all siblings after the header until the next header
            siblings = list(parent)[header_index + 1 :]
            elements_to_move = []

            for sibling in siblings:
                if sibling.tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    break
                elements_to_move.append(sibling)

            # Move the elements into our section div
            for elem in elements_to_move:
                parent.remove(elem)
                section_div.append(elem)

            # Insert the section div after the header
            parent.insert(header_index + 1, section_div)

            # Move the header into the section div as the first child
            parent.remove(header)
            section_div.insert(0, header)
        # Build a parent map for fast lookups
        parent_map = {child: parent for parent in root.iter() for child in parent}

        # Gather only H2 headers for section wrapping
        headers = [el for el in root.iter() if el.tag == "h2"]

        for header in headers:
            parent = parent_map.get(header)
            if not parent:
                continue

            idx = list(parent).index(header)
            section_id = header.text.strip().lower().replace(" ", "-")

            # Create wrapper <div>
            section_div = ElementTree.Element(
                "div",
                {
                    "class": "kb-section",
                    "data-section-id": section_id,
                },
            )

            # Move header into wrapper first
            parent.remove(header)
            section_div.append(header)

            # Pull siblings until the next H2 into the wrapper
            siblings = list(parent)[idx:]
            for sib in siblings:
                if sib.tag == "h2":
                    break
                parent.remove(sib)
                section_div.append(sib)

            # Insert the wrapper back at the original index
            parent.insert(idx, section_div)

        return root


class SectionWrapperExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(SectionWrapperTreeprocessor(md), "sectionwrapper", 0)


class HtmlSanitizerPreprocessor(Preprocessor):
    """Preprocessor that sanitizes HTML tags before they are re-injected."""

    def sanitize_html(self, tag):
        text = re.sub(r"<[^>]+>", "", tag)
        print(f"tag: {tag}, text: {text}")
        if tag.startswith("<pre><code ") and tag.endswith("</code></pre>"):
            return tag
        return f"<span class='render-warning'>{text}</span>"

    def run(self, lines):
        # (1) Grab the raw HTML tags from the markdown instance
        raw_html_tags = self.md.htmlStash.rawHtmlBlocks

        # Sanitize each HTML tag
        for i, html in enumerate(raw_html_tags):
            # Replace the original HTML with a sanitized version
            # For now, we'll just strip all HTML tags
            # Later we can add more sophisticated sanitization
            raw_html_tags[i] = self.sanitize_html(raw_html_tags[i])

        return lines


class LinkSanitizerPostprocessor(Postprocessor):
    def run(self, text):
        # There are two types of links that will be rendered by our feature. We
        # want to ensure that we sanitize both of them
        # First, <a href="..."> tags
        html_link_pattern = re.compile(r'<a\s+[^>]*href=[\'"][^\'"]+[\'"][^>]*>.*?</a>', re.IGNORECASE)
        # Additionally, [link text](link) markdown elements
        markdown_link_pattern = re.compile(r"\[.*?\]\([^\)]+\)")

        # Then we can replace the HTML text as it exists in the parser
        # text = unmatched_tags.sub("<span class='render-warning'>Unmatched Tag</span>", text)
        text = html_link_pattern.sub("<span class='render-warning'>Hard-coded link</span>", text)
        text = markdown_link_pattern.sub("<span class='render-warning'>Hard-coded link</span>", text)

        return text


class HtmlSanitizerExtension(Extension):
    """Extension that sanitizes HTML content in markdown."""

    def extendMarkdown(self, md):
        # Register our preprocessor with high priority to ensure it runs before other processors
        md.preprocessors.register(HtmlSanitizerPreprocessor(md), "html_sanitizer", 0)
        md.postprocessors.register(LinkSanitizerPostprocessor(md), "html_sanitizer", 0)
        md.treeprocessors.register(SectionWrapperTreeprocessor(md), "sectionwrapper", priority=30)
