from __future__ import annotations

WORD_BITS = 16
WORD_MASK = 0xFFFF
WORD_SIGN_BIT = 0x8000
WORD_MAX_SIGNED = 0x7FFF
WORD_MIN_SIGNED = -0x8000


def word(value: int) -> int:
    return value & WORD_MASK


def signed16(value: int) -> int:
    w = value & WORD_MASK
    if w >= WORD_SIGN_BIT:
        return w - (WORD_MASK + 1)
    return w


def is_negative16(value: int) -> bool:
    return (value & WORD_SIGN_BIT) != 0
