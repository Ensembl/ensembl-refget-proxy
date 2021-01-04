#
#    See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

import unittest

from starlette.datastructures import CommaSeparatedStrings

from core import config


class ConfigTestCase(unittest.TestCase):
    def test_environment_variables(self):
        assert type(config.ALLOWED_HOSTS) == CommaSeparatedStrings
        assert type(config.REFGET_SERVER_URL_LIST) == list
        assert len(config.REFGET_SERVER_URL_LIST) > 0


if __name__ == "__main__":
    unittest.main()
