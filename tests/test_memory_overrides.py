# pyright: reportTypedDictNotRequiredAccess=false

import os
import unittest
from unittest import mock

import dj_database_url


class MemoryDatabaseOverridesTests(unittest.TestCase):
    def test_parse_honors_engine_override(self) -> None:
        config = dj_database_url.parse(
            "sqlite://:memory:", engine="custom.sqlite.backend"
        )
        self.assertEqual(
            config, {"ENGINE": "custom.sqlite.backend", "NAME": ":memory:"}
        )

    def test_parse_honors_test_options(self) -> None:
        config = dj_database_url.parse(
            "sqlite://:memory:", test_options={"NAME": "test_memory", "MIGRATE": False}
        )
        self.assertEqual(
            config,
            {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
                "TEST": {"NAME": "test_memory", "MIGRATE": False},
            },
        )

    @mock.patch.dict(os.environ, {"DJ_DB_URL_MEMORY_TEST": "sqlite://:memory:"})
    def test_config_forwards_explicit_overrides(self) -> None:
        config = dj_database_url.config(
            env="DJ_DB_URL_MEMORY_TEST",
            engine="custom.sqlite.backend",
            test_options={"MIGRATE": False},
            conn_max_age=600,
            conn_health_checks=True,
        )
        self.assertEqual(
            config,
            {
                "ENGINE": "custom.sqlite.backend",
                "NAME": ":memory:",
                "TEST": {"MIGRATE": False},
            },
        )

    def test_empty_overrides_keep_default_memory_configuration(self) -> None:
        config = dj_database_url.parse("sqlite://:memory:", engine="", test_options={})
        self.assertEqual(
            config, {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        )
