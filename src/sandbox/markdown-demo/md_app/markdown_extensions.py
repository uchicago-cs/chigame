from xml.etree import ElementTree

from markdown.extensions import Extension
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

        return root


class SectionWrapperExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(SectionWrapperTreeprocessor(md), "sectionwrapper", 0)
