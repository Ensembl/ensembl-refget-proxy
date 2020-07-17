import unittest

from fastapi.testclient import TestClient
from starlette.datastructures import CommaSeparatedStrings

from core import config
from main import app


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_environment_variables(self):
        assert type(config.ALLOWED_HOSTS) == CommaSeparatedStrings
        assert type(config.REFGET_SERVER_URL_LIST) == list
        assert len(config.REFGET_SERVER_URL_LIST) > 0


if __name__ == "__main__":
    unittest.main()
