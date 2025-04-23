import markdown
from django.shortcuts import render

MARKDOWN_STRING = """
# Game Guide: Basic Combat Mechanics

## Table of Contents
[TOC]

## Introduction
This guide covers the basic combat mechanics in our game.  
New players should read this guide carefully before starting their adventure.

## Combat Basics
The combat system consists of several key elements:

### Attack Types
1. Melee Attacks
   - Sword Slash
   - Shield Bash
   - Kick

2. Ranged Attacks
   - Bow Shot
   - Magic Bolt
   - Throwing Knife

### Damage Calculation
| Attack Type | Base Damage | Critical Chance |
|------------|-------------|-----------------|
| Sword Slash | 15 | 10% |
| Shield Bash | 10 | 5% |
| Bow Shot | 12 | 15% |
| Magic Bolt | 20 | 20% |

## Code Examples
Here's how damage is calculated in the game:

```python
def calculate_damage(base_damage, critical_chance):
    if random.random() < critical_chance:
        return base_damage * 2
    return base_damage
```

## Advanced Techniques
1. Combo Attacks
   - Chain multiple attacks together
   - Each successful hit increases damage
   - Maximum of 5 hits in a combo

2. Defense Strategies
   - Block reduces damage by 50%
   - Dodge completely avoids damage
   - Parry can counter-attack

## Tips and Tricks
* Always keep your shield ready
* Use the environment to your advantage
* Learn enemy attack patterns
* Practice your timing for perfect blocks
"""


def markdown_content_view(request):
    md = markdown.Markdown(extensions=[
        "fenced_code",  # For code blocks
        "tables",      # For table support
        "toc",         # For table of contents
        "nl2br",       # For converting newlines to <br> tags
        "sane_lists",  # For better list handling
        "codehilite"   # For syntax highlighting
    ])
    markdown_content = {
        "title": "Knowledge Base Markdown Sandbox",
        "content": MARKDOWN_STRING,
    }
    context = {"markdown_content": markdown_content}
    markdown_content["content"] = md.convert(markdown_content["content"])
    return render(request, "md_app/markdown_content.html", context=context)
