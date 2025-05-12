import re

from django.core.exceptions import ValidationError


def validate_emoji(content):
    """
    Given a char value (content attribute), raises exception if not a single emoji.
    """
    content = content.strip()

    emoji_pattern = re.compile(
        r"^(?:"
        r"[\u2600-\u26FF\u2700-\u27BF]"
        r"|[\U0001F300-\U0001F5FF]"
        r"|[\U0001F600-\U0001F64F]"
        r"|[\U0001F680-\U0001F6FF]"
        r"|[\U0001F700-\U0001F77F]"
        r"|[\U0001F780-\U0001F7FF]"
        r"|[\U0001F800-\U0001F8FF]"
        r"|[\U0001F900-\U0001F9FF]"
        r"|[\U0001FA00-\U0001FAFF]"
        r")$"
    )

    if not emoji_pattern.match(content):
        raise ValidationError("Icon is not a valid single emoji.")
