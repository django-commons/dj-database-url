# pyright: reportTypedDictNotRequiredAccess=false

import unittest
from urllib.parse import urlencode

import dj_database_url


class CurrentSchemaOptionsTests(unittest.TestCase):
    def test_preserves_existing_options_for_postgres_schemes(self) -> None:
        query = urlencode(
            {
                "options": "-c statement_timeout=2000 -c lock_timeout=500",
                "currentSchema": "reporting",
            }
        )
        for scheme in (
            "postgres",
            "postgresql",
            "pgsql",
            "postgis",
            "redshift",
            "timescale",
            "timescalegis",
        ):
            with self.subTest(scheme=scheme):
                config = dj_database_url.parse(f"{scheme}://u:p@host/db?{query}")
                self.assertEqual(
                    config["OPTIONS"],
                    {
                        "options": "-c statement_timeout=2000 -c lock_timeout=500 "
                        "-c search_path=reporting"
                    },
                )

    def test_current_schema_takes_precedence_in_either_query_order(self) -> None:
        parameters = [
            ("options", "-c search_path=public -c statement_timeout=2000"),
            ("currentSchema", "reporting"),
        ]
        for pairs in (parameters, parameters[::-1]):
            with self.subTest(pairs=pairs):
                config = dj_database_url.parse(
                    f"postgres://u:p@host/db?{urlencode(pairs)}"
                )
                self.assertEqual(
                    config["OPTIONS"]["options"],
                    "-c search_path=public -c statement_timeout=2000 "
                    "-c search_path=reporting",
                )

    def test_appended_schema_is_escaped(self) -> None:
        query = urlencode(
            {
                "options": "-c statement_timeout=2000",
                "currentSchema": "reporting area\\night\tteam",
            }
        )
        config = dj_database_url.parse(f"postgres://u:p@host/db?{query}")
        self.assertEqual(
            config["OPTIONS"]["options"],
            "-c statement_timeout=2000 "
            "-c search_path=reporting\\ area\\\\night\\\tteam",
        )

    def test_current_schema_without_existing_options(self) -> None:
        config = dj_database_url.parse("postgres://u:p@host/db?currentSchema=reporting")
        self.assertEqual(config["OPTIONS"], {"options": "-c search_path=reporting"})

    def test_options_without_current_schema_are_unchanged(self) -> None:
        options = "-c statement_timeout=2000 -c search_path=public"
        query = urlencode({"options": options})
        config = dj_database_url.parse(f"postgres://u:p@host/db?{query}")
        self.assertEqual(config["OPTIONS"], {"options": options})
