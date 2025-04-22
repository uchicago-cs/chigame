# Knowledge Base Markdown Library Sandbox

This sandbox was implemented from Real Python's [tutorial](https://realpython.com/django-markdown/).
The only significant changes was implementing the markdown file as a string to allow
for easier in-line editing. This should be changed once we implement file storage for markdown files,
per issue #514.

## Running the Sandbox

Assuming that you start from the root of the repo:
```
source venv/bin/activate
cd src/sandbox/markdown-demo
python manage.py runserver
```

## How the Sandbox Works

You can edit the markdown string and see how the corresponding HTML changes.
Hopefully, this can give you a sense of how markdown is translated to/from HTML.
Then, we can begin to add extensions to customize this HTML rendering, ideally
such that we can format the guide page to render as multiple pages.
