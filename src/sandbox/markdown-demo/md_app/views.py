import markdown
from django.shortcuts import render

MARKDOWN_STRING = """
# This is a title
##  And this is a subheader
Some content goes here

- with
- a
- list
"""


def markdown_content_view(request):
    md = markdown.Markdown(extensions=["fenced_code"])
    markdown_content = {
        "title": "Knowledge Base Markdown Sandbox",
        "content": MARKDOWN_STRING,
    }
    context = {"markdown_content": markdown_content}
    markdown_content["content"] = md.convert(markdown_content["content"])
    return render(request, "md_app/markdown_content.html", context=context)
