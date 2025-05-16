import re



BANNED_WORDS = {
     "buy now",
     "free money",
     "click here",
     "subscribe",
     "limited time offer",
     "urgent",
     "winner",
     "cash prize",
     "risk-free",
     "guaranteed",
     "act now",
 }


def is_spam(content: str | None) -> bool:
    if not content:
        return False  # Consider empty or None content as non-spam
    content_lower = content.lower()

    # Rule 1: check for banned phrases
    if any(banned in content_lower for banned in BANNED_WORDS):
        return True

    # Rule 2: repeated characters (e.g., "!!!!!!!", "loooool")
    if re.search(r"(.)\1{6,}", content):
        return True

    # Rule 3: content too short or too repetitive
    words = content.split()
    if len(words) < 3 or len(set(words)) <= 2:
        return True

    return False