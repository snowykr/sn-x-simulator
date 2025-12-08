from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Instruction:
    opcode: str
    operands: tuple[str, ...]
    raw: str


def parse_code(code_str: str) -> tuple[list[Instruction], dict[str, int]]:
    instructions: list[Instruction] = []
    labels: dict[str, int] = {}
    actual_line_idx = 0

    for line in code_str.strip().split("\n"):
        line = line.split(";")[0].strip()
        if not line:
            continue

        if ":" in line:
            label_part, code_part = line.split(":", 1)
            labels[label_part.strip()] = actual_line_idx
            line = code_part.strip()

        if not line:
            continue

        parts = re.split(r"[,\s]+", line)
        opcode = parts[0].upper()
        operands = tuple(parts[1:])

        instructions.append(Instruction(opcode=opcode, operands=operands, raw=line))
        actual_line_idx += 1

    return instructions, labels
