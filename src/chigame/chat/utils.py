"""
Utilities for the chat app. Includes profanity filtering.
"""

import re


class ProfanityFilter:
    """
    A simple class that allows for filtering of profanity and censoring of messages.
    """

    # a list of profane words
    # this list should be updated with new profane words as they are discovered
    profanity_list = [
        "uchicago sucks",
        "uchicago is a bad school",
        "uchicago is a bad university",
        "uchicago is a bad college",
    ]

    def __init__(self):
        """
        Initialize the profanity filter.
        """
        escaped_words = [re.escape(word) for word in self.profanity_list]  # create the regex patterns
        self.pattern = re.compile(r"\b(" + "|".join(escaped_words) + r")\b", re.IGNORECASE)

    def contains_profanity(self, message):
        """
        Check if the message contains any profane words.

        Args:
            message (str): The message to check for profane words.

        Returns:
            bool: True if the message contains any profane words, False otherwise.
        """
        return bool(self.pattern.search(message))

    def censor_message(self, message):
        """
        Censor the message from profane words.

        Args:
            message (str): The message to censor.

        Returns:
            str: The censored message.
        """
        return self.pattern.sub(lambda m: '*' * len(m.group()), message)
