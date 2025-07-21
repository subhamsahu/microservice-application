"""
Utility class for string operations.
"""

import re

class StringUtils:
    """Utility class for string operations."""

    @staticmethod
    def to_first_letter_uppercase(input_str: str) -> str:
        """Converts the first letter of each word in a string to uppercase."""
        value_string = input_str.lower()
        return ' '.join(
            f"{word[0].upper()}{word[1:].lower()}" if word
            else '' for word in value_string.split(' ')
        )

    @staticmethod
    def to_lower_case(input_str: str) -> str:
        """Converts a string to lowercase."""
        return input_str.lower()

    @staticmethod
    def to_upper_case(input_str: str) -> str:
        """Converts a string to uppercase."""
        return input_str.upper() if input_str else input_str

    @staticmethod
    def is_email(email: str) -> bool:
        """Checks if a string is a valid email address."""
        regex_exp = re.compile(
            r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
            r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        )
        return bool(regex_exp.match(email))

    @staticmethod
    def is_data_url(value: str) -> bool:
        """Checks if a string is a valid data URL."""
        data_url_regex = re.compile(
            r"^\s*data:([a-z]+/[a-z0-9-+.]+(;[a-z-]+=[a-z0-9-]+)?)?(;base64)?,"
            r"([a-z0-9!$&',()*+;=\-._~:@\\/?%\s]*)\s*$", re.IGNORECASE
        )
        return bool(data_url_regex.match(value))
