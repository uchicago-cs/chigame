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

Second page

# Advanced Features

More content and <a href="...">link</a>
"""


def markdown_content_view(request):
    # Get the requested section from query parameters
    requested_section = request.GET.get("section", "introduction")

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
    template = "md_app/markdown_content.html"

    return render(request, template, context=context)
