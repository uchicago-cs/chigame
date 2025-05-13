"""
Utilities for the chat app. Includes profanity filtering.
"""

import re
import os

# this is the path to the file containing profane words
PATH_TO_PROFANITY_FILE = os.path.join(os.path.dirname(__file__), "PROFANITY.txt")


class ProfanityFilter:
    """
    A simple class that allows for filtering of profanity and censoring of messages.
    """

    def __init__(self):
        """
        Initialize the profanity filter from a comma separated file containing profane words.
        """
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        profanity_file = PATH_TO_PROFANITY_FILE
        
        # Read profane words from file (comma separated)
        try:
            with open(profanity_file, 'r') as f:
                profanity_text = f.read().strip()
                self.profanity_list = [word.strip() for word in profanity_text.split(',')]
        except FileNotFoundError:
            print(f"Warning: Profanity file not found at {profanity_file}")
            self.profanity_list = []
        
        # Create the regex pattern
        escaped_words = [re.escape(word) for word in self.profanity_list]
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
        return self.pattern.sub(lambda m: "*" * len(m.group()), message)
