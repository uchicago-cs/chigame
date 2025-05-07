
# src/sandbox/markdown-demo/md_app/markdown_extensions.py

import xml.etree.ElementTree as ET


from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class SectionWrapperTreeprocessor(Treeprocessor):
    def run(self, root):

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
            section_div = ET.Element(
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

        # Use priority 30 (greater than the built-in TOC's 20)
        md.treeprocessors.register(SectionWrapperTreeprocessor(md), "sectionwrapper", priority=30)

