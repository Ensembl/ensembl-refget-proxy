import unittest

from starlette.datastructures import CommaSeparatedStrings

from app.core import config


class ConfigTestCase(unittest.TestCase):
    def test_environment_variables(self):
        assert type(config.ALLOWED_HOSTS) == CommaSeparatedStrings
        assert type(config.REFGET_SERVER_URL_LIST) == list
        assert len(config.REFGET_SERVER_URL_LIST) > 0


if __name__ == "__main__":
    unittest.main()
