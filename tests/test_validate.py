import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate  # noqa: E402

HEADER = ",".join(validate.COLUMNS) + "\n"
GOOD = "lemonde.fr,Groupe Le Monde,TRUE,TRUE,https://example.org/a,https://example.org/src\n"


def problems(body, header=HEADER):
    return validate.check(header + body)


class ValidateTests(unittest.TestCase):
    def test_valid_row(self):
        self.assertEqual(problems(GOOD), [])

    def test_committed_data_is_valid(self):
        self.assertEqual(validate.check(validate.read_text(validate.DEFAULT_PATH)), [])

    def test_bad_header(self):
        self.assertTrue(problems(GOOD, "domain,information\n"))

    def test_domain_must_be_bare_lowercase_hostname(self):
        for bad in ["https://lemonde.fr", "LeMonde.fr", "lemonde.fr/path", "lemonde", "le monde.fr", "lemonde.fr:8080"]:
            row = GOOD.replace("lemonde.fr", bad, 1)
            self.assertTrue(any("domain" in p for p in problems(row)), bad)

    def test_duplicate_domain(self):
        self.assertTrue(any("duplicate" in p for p in problems(GOOD + GOOD)))

    def test_source_required_and_https(self):
        self.assertTrue(any("source_url" in p for p in problems("a.fr,x,TRUE,TRUE,,\n")))
        self.assertTrue(any("source_url" in p for p in problems("a.fr,x,TRUE,TRUE,,http://example.org\n")))

    def test_multiple_sources_allowed(self):
        self.assertEqual(problems("a.fr,x,TRUE,TRUE,,https://e.org/1 | https://e.org/2\n"), [])

    def test_booleans(self):
        self.assertTrue(any("active" in p for p in problems("a.fr,x,TRUE,yes,,https://e.org\n")))
        self.assertTrue(any("include_subdomains" in p for p in problems("a.fr,x,true,TRUE,,https://e.org\n")))

    def test_link_url_must_be_https_when_set(self):
        self.assertTrue(any("link_url" in p for p in problems("a.fr,x,TRUE,TRUE,ftp://e.org,https://e.org\n")))

    def test_must_be_sorted(self):
        rows = "b.fr,x,TRUE,TRUE,,https://e.org\na.fr,x,TRUE,TRUE,,https://e.org\n"
        self.assertTrue(any("canonical" in p for p in problems(rows)))
        self.assertEqual(validate.check(validate.canonical(validate.parse(HEADER + rows))), [])

    def test_wrong_column_count(self):
        self.assertTrue(any("columns" in p for p in problems("a.fr,x\n")))


if __name__ == "__main__":
    unittest.main()
