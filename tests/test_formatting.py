import unittest

from bot.formatting import escape_html


class EscapeHtmlTests(unittest.TestCase):
    def test_escapes_html_metacharacters(self):
        self.assertEqual(escape_html('<b>"Mafia" & friends</b>'), "&lt;b&gt;&quot;Mafia&quot; &amp; friends&lt;/b&gt;")

    def test_converts_non_string_values(self):
        self.assertEqual(escape_html(123), "123")


if __name__ == "__main__":
    unittest.main()
