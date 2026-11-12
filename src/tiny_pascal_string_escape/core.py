import re

# Matches a backslash escape sequence (e.g. \n, \t, \\) or a #-prefixed
# numeric escape (e.g. #65, #$41, #x41).
_ESCAPE_RE = re.compile(
    r"\\(?P<escaped>.|$)"  # backslash followed by any char (or end)
    r"|"
    r"#(?P<numeric>\$[0-9A-Fa-f]+|x[0-9A-Fa-f]+|[0-9]+)"
)

# Mapping of single-character Pascal/Delphi escape sequences to their
# literal Python equivalents.  We keep this small and explicit rather than
# using `codecs.decode(..., 'unicode_escape')` because that function also
# interprets octal escapes and `\x` with a variable number of digits, which
# would silently accept input that Pascal does not.
_NAMED_ESCAPES = {
    "a": "\a",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "\\": "\\",
    "'": "'",
    '"': '"',
    "?": "?",
}


def decode_pascal_string(s):
    """Decode a Pascal or Delphi string literal into a Python string.

    The function recognises three kinds of escape sequences:

    * Named escapes: ``\\n``, ``\\t``, ``\\r``, ``\\a``, ``\\b``, ``\\f``,
      ``\\v``, ``\\\\``, ``\\'``, ``\\"`` and ``\\?``.
    * Numeric escapes: ``#65`` (decimal), ``#$41`` (hex) and ``#x41``
      (hex with an ``x`` prefix).  The value must fit in a Unicode code point
      (0 to 0x10FFFF); values outside that range raise :class:`ValueError`.
    * Any other backslash escape is passed through unchanged.  Pascal does
      not define a meaning for e.g. ``\\q``, and silently dropping the
      backslash would corrupt the string.

    A backslash at the very end of the input is treated as a literal
    backslash, matching the behaviour of Delphi's compiler.

    The decoder operates on the raw characters of the string, not on a
    tokenised representation, so it is safe to call on strings that contain
    quotes, newlines or other whitespace.

    :param s: the escaped string to decode.
    :type s: str
    :returns: the decoded string.
    :rtype: str
    :raises TypeError: if *s* is not a string.
    :raises ValueError: if a numeric escape is out of range or malformed.
    """
    if not isinstance(s, str):
        raise TypeError("decode_pascal_string expects a str, got %r" % (type(s).__name__,))

    out = []
    pos = 0
    length = len(s)

    while pos < length:
        match = _ESCAPE_RE.search(s, pos)
        if match is None:
            # No further escape sequences: copy the remainder verbatim.
            out.append(s[pos:])
            break

        # Copy everything between the previous position and the escape.
        out.append(s[pos:match.start()])

        if match.group("escaped") is not None:
            escaped = match.group("escaped")
            if escaped == "":
                # Trailing backslash: Delphi treats it as a literal backslash.
                out.append("\\")
            else:
                # Unknown escapes are left untouched so that callers can see
                # exactly what was in the source.  This is deliberately
                # conservative: we do not guess at a meaning.
                out.append(_NAMED_ESCAPES.get(escaped, "\\" + escaped))
        else:
            numeric = match.group("numeric")
            if numeric.startswith("$"):
                value = int(numeric[1:], 16)
            elif numeric.startswith("x"):
                value = int(numeric[1:], 16)
            else:
                value = int(numeric, 10)

            if value > 0x10FFFF:
                raise ValueError(
                    "numeric escape #%s is out of Unicode range (max 0x10FFFF)" % numeric
                )
            out.append(chr(value))

        pos = match.end()

    return "".join(out)
