"""Split text"""
from __future__ import annotations

import re

from models.domain import Chunk


async def chunk(
    text: str,
    content_type: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    if content_type == "markdown":
        chunks = _heading_aware_split(text, chunk_size, chunk_overlap)
    else:
        chunks = _recursive_character_split(text, chunk_size, chunk_overlap)
    for i, c in enumerate(chunks):
        c.chunk_index = i
    return chunks


def _heading_aware_split(
    text: str, chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    sections: list[tuple[str | None, str]] = []
    last_end = 0
    current_heading = None

    for match in heading_pattern.finditer(text):
        if match.start() > last_end:
            content = text[last_end : match.start()].strip()
            if content:
                sections.append((current_heading, content))
        current_heading = match.group(2).strip()
        last_end = match.end()

    remaining = text[last_end:].strip()
    if remaining:
        sections.append((current_heading, remaining))

    chunks: list[Chunk] = []
    for heading, content in sections:
        if len(content) <= chunk_size:
            chunks.append(
                Chunk(content=content, section_title=heading)
            )
        else:
            sub_chunks = _recursive_character_split(
                content, chunk_size, chunk_overlap
            )
            for sc in sub_chunks:
                sc.section_title = heading
            chunks.extend(sub_chunks)
    return chunks


def _recursive_character_split(
    text: str, chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    separators = ["\n\n", "\n", ". ", " "]
    return _split_recursive(text, separators, chunk_size, chunk_overlap)


def _split_recursive(
    text: str,
    separators: list[str],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    if len(text) <= chunk_size:
        return [Chunk(content=text)] if text.strip() else []

    sep = separators[0] if separators else " "
    remaining_seps = separators[1:] if len(separators) > 1 else separators

    parts = text.split(sep)
    chunks: list[Chunk] = []
    current = ""

    for part in parts:
        candidate = f"{current}{sep}{part}" if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current.strip():
                if len(current) <= chunk_size:
                    chunks.append(Chunk(content=current.strip()))
                else:
                    chunks.extend(
                        _split_recursive(
                            current, remaining_seps, chunk_size, chunk_overlap
                        )
                    )
            if chunk_overlap > 0 and current:
                overlap_text = current[-chunk_overlap:]
                current = overlap_text + sep + part
            else:
                current = part

    if current.strip():
        if len(current) <= chunk_size:
            chunks.append(Chunk(content=current.strip()))
        else:
            chunks.extend(
                _split_recursive(
                    current, remaining_seps, chunk_size, chunk_overlap
                )
            )
    return chunks