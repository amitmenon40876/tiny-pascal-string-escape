import unittest

from tiny_pascal_string_escape import decode_pascal_string


class DecodePascalStringTests(unittest.TestCase):
    def test_plain_string_is_returned_unchanged(self):
        self.assertEqual(decode_pascal_string("hello"), "hello")

    def test_empty_string(self):
        self.assertEqual(decode_pascal_string(""), "")

    def test_named_escapes(self):
        self.assertEqual(
            decode_pascal_string(r"a\nb\tc\\d\'e\"f"),
            "a\nb\tc\\d'e\"f",
        )

    def test_decimal_numeric_escape(self):
        self.assertEqual(decode_pascal_string("#65#66#67"), "ABC")

    def test_hex_numeric_escape_with_dollar(self):
        self.assertEqual(decode_pascal_string("#$41#$42"), "AB")

    def test_hex_numeric_escape_with_x(self):
        self.assertEqual(decode_pascal_string("#x41#x42"), "AB")

    def test_numeric_escape_unicode(self):
        self.assertEqual(decode_pascal_string("#1234"), "\u04d2")

    def test_mixed_escapes(self):
        self.assertEqual(
            decode_pascal_string(r"\t#65\n#$42"),
            "\tA\nB",
        )

    def test_unknown_escape_is_left_alone(self):
        self.assertEqual(decode_pascal_string(r"\q"), r"\q")

    def test_trailing_backslash_is_literal(self):
        self.assertEqual(decode_pascal_string("abc\\"), "abc\\")

    def test_double_backslash_produces_single_backslash(self):
        self.assertEqual(decode_pascal_string(r"\\"), "\\")

    def test_numeric_escape_at_max_unicode(self):
        self.assertEqual(decode_pascal_string("#1114111"), chr(0x10FFFF))

    def test_numeric_escape_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            decode_pascal_string("#1114112")

    def test_type_error_on_non_string(self):
        with self.assertRaises(TypeError):
            decode_pascal_string(123)  # type: ignore[arg-type]

    def test_hash_sign_not_followed_by_digits_is_literal(self):
        self.assertEqual(decode_pascal_string("#not-an-escape"), "#not-an-escape")

    def test_named_escape_after_numeric(self):
        self.assertEqual(decode_pascal_string("#65\\n"), "A\n")

    def test_escaped_question_mark(self):
        self.assertEqual(decode_pascal_string(r"\?"), "?")

    def test_escaped_single_quote(self):
        self.assertEqual(decode_pascal_string(r"\'"), "'")


if __name__ == "__main__":
    unittest.main()
