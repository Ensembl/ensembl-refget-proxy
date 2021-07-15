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

from fastapi.testclient import TestClient

from core.redis import get_cached_url
from main import app


class RedisTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.api_prefix = "api"
        self.sequence_url_prefix = "api/sequence/"
        self.metadata_url_prefix = "/metadata/"
        self.checksum = "6681ac2f62509cfc220d78751b8dc524"
        self.refget_url = "http://test.service.refget.review.ensembl.org/"
        self.sequence_path = self.sequence_url_prefix + self.checksum
        self.sequence_not_found_path = self.sequence_url_prefix + "6681ac2f62751b8dc845"

    async def test_get_cached_url(self):
        result = await get_cached_url(self.checksum)
        assert type(result) == dict
        assert len(result) == 1
        assert result == {
            "refget_server_url": self.refget_url,
            "checksum": self.checksum,
            "metadata_url": self.refget_url + "sequence/" + self.checksum + "/metadata",
        }

    # async def test_get_cached_metadata(self):
    #     result = await get_cached_url(self.checksum)
    #     assert type(result) == dict
    #     assert len(result) == 1
    #     assert result == {
    #         "refget_server_url": self.refget_url,
    #         "checksum": self.checksum,
    #         "metadata_url": self.refget_url + "sequence/" + self.checksum + "/metadata",
    #     }


if __name__ == "__main__":
    # Add condition to check if the redis exists
    unittest.main()
