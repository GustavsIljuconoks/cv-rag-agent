import unittest

from app.services.job_sources.nva import NvaLatviaJobSource, parse_salary_range


class NvaJobSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = NvaLatviaJobSource()

    def test_parse_salary_range_handles_monthly_range(self) -> None:
        self.assertEqual(parse_salary_range("875-1080"), (875, 1080))

    def test_parse_salary_range_handles_single_amount(self) -> None:
        self.assertEqual(parse_salary_range("2000"), (2000, 2000))

    def test_parse_salary_range_treats_hourly_salary_as_unknown(self) -> None:
        self.assertEqual(parse_salary_range("5.30 Eur/stundā"), (None, None))
        self.assertEqual(parse_salary_range("12 EUR/h"), (None, None))

    def test_remote_query_matches_latvian_aliases_with_diacritics(self) -> None:
        self.assertTrue(self.source._matches_remote_query("attālināts"))
        self.assertTrue(self.source._matches_remote_query("attālināti veicams darbs"))
        self.assertTrue(self.source._matches_remote_query("remote only"))

    def test_build_search_candidates_drops_remote_only_location_token(self) -> None:
        candidates = self.source._build_search_candidates("python", "attālināts")

        self.assertEqual(candidates, ["python"])


if __name__ == "__main__":
    unittest.main()
