import markdown
from django.shortcuts import render

from .markdown_extensions import SectionWrapperExtension

MARKDOWN_STRING = """
# Introduction
Welcome to our knowledge base guide. This is the introduction section.

# Getting Started
Here's how to get started with our product.

# Advanced Features
Learn about advanced features and capabilities.
"""


def markdown_content_view(request):
    # Get the requested section from query parameters
    requested_section = request.GET.get("section", "introduction")

    # Initialize markdown with our section wrapper extension
    md = markdown.Markdown(extensions=["fenced_code", SectionWrapperExtension()])

    # Convert markdown to HTML
    html_content = md.convert(MARKDOWN_STRING)

    # Create context with the rendered content
    context = {
        "html_content": html_content,
        "requested_section": requested_section,
    }

    return render(request, "md_app/markdown_content.html", context=context)
