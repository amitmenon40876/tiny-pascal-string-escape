# tiny-pascal-string-escape

Decodes Pascal and Delphi string literals containing hex (`#xFF`), unicode (`#1234`), and named escape sequences into Python strings.

```python
from tiny_pascal_string_escape import decode_pascal_string

assert decode_pascal_string(r"Hello\nWorld") == "Hello\nWorld"
assert decode_pascal_string("#65#66#67") == "ABC"
assert decode_pascal_string("#$41#x42") == "AB"
assert decode_pascal_string("#1234") == "\u04d2"
```

## Why this exists

Pascal and Delphi source files use a compact escape syntax that is close to, but not the same as, Python's.  The standard library's `unicode_escape` codec is a poor fit: it accepts octal escapes and variable-length `\x` escapes that Pascal does not, and it silently drops backslashes for unknown escapes.  This library makes one deliberate trade-off: **unknown backslash escapes are preserved verbatim** rather than being guessed at or discarded.  That keeps the decoder round-trippable for source files that contain vendor-specific or future escape sequences, at the cost of not being able to decode those sequences into characters.

## The awkward edge

A backslash at the very end of the input is treated as a literal backslash, matching Delphi's compiler.  Numeric escapes above `0x10FFFF` raise `ValueError` instead of producing a surrogate or replacement character, so malformed input fails loudly rather than silently corrupting data.

## API

### `decode_pascal_string(s: str) -> str`

Decodes a Pascal or Delphi string literal.

Recognised escapes:

- Named: `\a`, `\b`, `\f`, `\n`, `\r`, `\t`, `\v`, `\\`, `\'`, `\"`, `\?`.
- Numeric: `#65` (decimal), `#$41` (hex), `#x41` (hex with `x` prefix).

Any other backslash escape is passed through unchanged.  A trailing backslash is a literal backslash.  Numeric escapes outside the Unicode range raise `ValueError`.  Passing a non-string raises `TypeError`.
