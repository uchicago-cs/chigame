import re

import markdown
from django.shortcuts import render

from .markdown_extensions import SectionWrapperExtension

MARKDOWN_STRING = """
# Game Guide: Basic Combat Mechanics

## Table of Contents
[TOC]

## Introduction
This guide covers the basic combat mechanics in our game.
New players should read this guide carefully before starting their adventure.

## Getting Started
Welcome to the game! This section will help you get set up and ready to play:

- **Create an account:** Sign up using your email or social login.
- **Download the game client:** Available for Windows, Mac, and Linux.
- **Set up your profile:** Choose your avatar and customize your settings.
- **Tutorial:** Complete the in-game tutorial to learn the basic controls and interface.
- **Join a lobby:** Find other new players and start your first match!

If you have any issues, visit the Help section or contact support.

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
| Attack Type  | Base Damage | Critical Chance |
|--------------|-------------|-----------------|
| Sword Slash  | 15          | 10%             |
| Shield Bash  | 10          | 5%              |
| Bow Shot     | 12          | 15%             |
| Magic Bolt   | 20          | 20%             |

## Code Examples
Here's how damage is calculated in the game:

```python
import random

def calculate_damage(base_damage: float, critical_chance: float) -> float:
    if random.random() < critical_chance:
        return base_damage * 2
    return base_damage
```

## Advanced Features

Unlock advanced gameplay with these features:

* **Skill Trees:** Customize your character's abilities by investing points in different skill branches.
* **Crafting System:** Gather resources and craft powerful weapons, armor, and potions.
* **Guilds:** Join or create a guild to team up with other players, participate in guild wars, and share resources.
* **Achievements:** Complete special challenges to earn badges and rewards.
* **PvP Arenas:** Test your skills against other players in ranked matches and tournaments.
* **Seasonal Events:** Participate in limited-time events for exclusive items and bonuses.

## Advanced Techniques

1. Combo Attacks
2. Defense Strategies

## Tips and Tricks

* Always keep your shield ready
* Use the environment to your advantage
* Learn enemy attack patterns
* Practice your timing for perfect blocks
  """


def markdown_content_view(request):
    # 1) What section to show/highlight
    requested_section = request.GET.get("section", "introduction")

    # 2) Build a simple TOC list from every H2 in the source
    #    - title: the text after "## "
    #    - id: slugified (lowercase, spaces→hyphens)
    raw_headings = re.findall(r"^##\s+(.*)$", MARKDOWN_STRING, flags=re.MULTILINE)
    toc_items = [
        {
            "title": title.strip(),
            "id": title.strip().lower().replace(" ", "-"),
        }
        for title in raw_headings
        if title.strip().lower() != "table of contents"
    ]

    # 3) Render Markdown ➔ HTML (no built-in TOC extension)
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.nl2br",
            "markdown.extensions.sane_lists",
            "markdown.extensions.codehilite",
            SectionWrapperExtension(),  # wrap each H1–H6 into <div class="kb-section">
        ]
    )
    html_content = md.convert(MARKDOWN_STRING)

    # 4) Pass both the HTML and our manual TOC into the template
    return render(
        request,
        "md_app/markdown_content.html",
        {
            "html_content": html_content,
            "toc_items": toc_items,
            "requested_section": requested_section,
        },
    )
