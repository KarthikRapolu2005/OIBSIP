"""
password_generator.py
----------------------
Core password generation engine for SecurePass.

SECURITY DESIGN:
    * Uses Python's `secrets` module exclusively (secrets.choice, secrets.SystemRandom)
      for all random selection. `secrets` is built on os.urandom() and is suitable
      for generating cryptographically strong security tokens/passwords.
    * The `random` module is NEVER imported or used anywhere in this project.
    * Passwords are generated, returned, and held only in memory (a Python list /
      string) for the lifetime of the running process. Nothing here writes to
      disk, a database, environment variables, or any log file.
    * The final password characters are shuffled using secrets.SystemRandom().shuffle
      (a CSPRNG-backed shuffle) so that the "guaranteed" characters from each
      selected category are not predictably placed at the start of the string.
"""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass, field
from typing import List


# --------------------------------------------------------------------------- #
# Character pools
# --------------------------------------------------------------------------- #

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>/?~"

# Characters that are visually ambiguous / easy to mis-type or mis-read.
AMBIGUOUS_CHARS = set("0O1lI|`'\"{}[]()/\\;:,.<>")


class PasswordGenerationError(Exception):
    """Raised when password generation cannot proceed due to invalid input."""


@dataclass
class PasswordOptions:
    """Holds the validated options required to generate a password."""

    length: int
    use_upper: bool = False
    use_lower: bool = False
    use_digits: bool = False
    use_symbols: bool = False
    exclude_ambiguous: bool = False

    MIN_LENGTH: int = field(default=8, init=False, repr=False)
    MAX_LENGTH: int = field(default=128, init=False, repr=False)

    def selected_type_count(self) -> int:
        return sum(
            [self.use_upper, self.use_lower, self.use_digits, self.use_symbols]
        )

    def validate(self) -> None:
        """
        Validates the options and raises PasswordGenerationError with a
        human-readable message describing exactly what is wrong.
        """
        if not isinstance(self.length, int):
            raise PasswordGenerationError("Password length must be a whole number.")

        if self.length < self.MIN_LENGTH:
            raise PasswordGenerationError(
                f"Password length must be at least {self.MIN_LENGTH} characters."
            )

        if self.length > self.MAX_LENGTH:
            raise PasswordGenerationError(
                f"Password length must not exceed {self.MAX_LENGTH} characters."
            )

        if self.selected_type_count() < 2:
            raise PasswordGenerationError(
                "Select at least 2 character types "
                "(uppercase, lowercase, numbers, symbols)."
            )

        # Make sure that, after excluding ambiguous characters, every
        # selected pool still has at least one usable character.
        for name, pool in self._active_pools().items():
            cleaned = _strip_ambiguous(pool) if self.exclude_ambiguous else pool
            if len(cleaned) == 0:
                raise PasswordGenerationError(
                    f"The '{name}' character set is empty after excluding "
                    "ambiguous characters. Deselect 'Exclude ambiguous "
                    "characters' or choose another character type."
                )

        # If ambiguous exclusion would leave too few total unique characters
        # to satisfy the requested length in a sane way, warn (not fatal —
        # repetition is fine for passwords) but still guard against a
        # pathological zero-length pool.
        if len(self._combined_pool()) == 0:
            raise PasswordGenerationError(
                "No character types selected. Please select at least 2."
            )

    def _active_pools(self) -> dict:
        pools = {}
        if self.use_upper:
            pools["Uppercase"] = UPPERCASE
        if self.use_lower:
            pools["Lowercase"] = LOWERCASE
        if self.use_digits:
            pools["Numbers"] = DIGITS
        if self.use_symbols:
            pools["Symbols"] = SYMBOLS
        return pools

    def _combined_pool(self) -> str:
        pools = self._active_pools().values()
        combined = "".join(pools)
        if self.exclude_ambiguous:
            combined = _strip_ambiguous(combined)
        return combined


def _strip_ambiguous(pool: str) -> str:
    return "".join(ch for ch in pool if ch not in AMBIGUOUS_CHARS)


def generate_password(options: PasswordOptions) -> str:
    """
    Generates a cryptographically secure password satisfying `options`.

    Guarantees:
        * Length exactly matches options.length.
        * At least one character from every SELECTED character type is present.
        * Only secrets.choice / secrets.SystemRandom are used for randomness.

    Raises:
        PasswordGenerationError: if options are invalid.
    """
    options.validate()

    active_pools = options._active_pools()  # {name: pool_str}
    if options.exclude_ambiguous:
        active_pools = {
            name: _strip_ambiguous(pool) for name, pool in active_pools.items()
        }

    combined_pool = "".join(active_pools.values())

    # Step 1: guarantee at least one char from each selected type.
    required_chars: List[str] = [
        secrets.choice(pool) for pool in active_pools.values()
    ]

    # Step 2: fill the remaining length with secure random choices from
    # the combined pool of all selected (and possibly ambiguous-stripped)
    # character sets.
    remaining = options.length - len(required_chars)
    filler_chars: List[str] = [secrets.choice(combined_pool) for _ in range(remaining)]

    all_chars = required_chars + filler_chars

    # Step 3: cryptographically secure shuffle so the guaranteed characters
    # aren't always in the first N positions.
    secrets.SystemRandom().shuffle(all_chars)

    return "".join(all_chars)
