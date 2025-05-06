import markdown
from django.shortcuts import render

from .markdown_extensions import HtmlSanitizerExtension, SectionWrapperExtension

MARKDOWN_STRING = """
<script>console.log("Injected code")</script>
# Introduction
Welcome to our knowledge base guide. This is the introduction section.

This is the first example of a <a href="https://google.com">link</a>.

This is the second example of a [link](https://google.com).

# Getting Started
Here's how to get started with our product.

# Advanced Features
Learn about advanced features and capabilities.
=======
"""


def markdown_content_view(request):
    # Get the requested section from query parameters
    requested_section = request.GET.get("section", "introduction")
    # Check if minimal UI is requested
    is_minimal = request.GET.get("minimal", "false").lower() == "true"

    # Initialize markdown with our extensions
    md = markdown.Markdown(extensions=["fenced_code", SectionWrapperExtension(), HtmlSanitizerExtension()])

    # Convert markdown to HTML
    html_content = md.convert(MARKDOWN_STRING)

    # Create context with the rendered content
    context = {
        "html_content": html_content,
        "requested_section": requested_section,
    }

    # Choose template based on UI mode
    template = "md_app/minimal_content.html" if is_minimal else "md_app/markdown_content.html"

    return render(request, template, context=context)
