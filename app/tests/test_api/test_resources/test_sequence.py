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
from loguru import logger
from fastapi.testclient import TestClient

from api.utils import metadata_url_list
from main import app


class APISequenceTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.api_prefix = "api"
        self.sequence_url_prefix = "api/sequence/"
        self.metadata_url_prefix = "/metadata/"
        self.checksum = "6681ac2f62509cfc220d78751b8dc524"
        self.refget_url = "http://test.service.refget.review.ensembl.org/"
        self.sequence_path = self.sequence_url_prefix + self.checksum
        self.sequence_not_found_path = self.sequence_url_prefix + "6681ac2f62751b8dc845"

    def test_404_error_in_none_relative_requests(self):
        response = self.client.get("api/")

        assert response.status_code == 404

    def test_api_error_404(self):
        get_response = self.client.get(self.sequence_not_found_path)
        logger.log("DEBUG", get_response)

        assert get_response.status_code == 404

    def test_api_error_405(self):
        post_response = self.client.post(self.sequence_path)
        assert post_response.status_code == 405

        patch_response = self.client.patch(self.sequence_path)
        assert patch_response.status_code == 405

        delete_response = self.client.delete(self.sequence_path)
        assert delete_response.status_code == 405

        put_response = self.client.put(self.sequence_path)
        assert put_response.status_code == 405

    def test_sequence_api_success_200(self):
        get_response = self.client.get(self.sequence_path + "?start=0&end=10")
        assert get_response.status_code == 200
        assert len(get_response.text) == 10
        assert get_response.text == "CCACACCACA"
        assert type(get_response.text) == str

    def test_sequence_api_416_range_not_satisfied(self):
        get_response = self.client.get(self.sequence_path + "?start=12&end=10")
        assert get_response.status_code == 416

    def test_sequence_metadata_api_success_200(self):
        get_response = self.client.get(self.sequence_path + self.metadata_url_prefix)
        assert get_response.status_code == 200
        assert len(get_response.json()) == 1
        assert type(get_response.json()) == dict
        assert get_response.json() == {
            "metadata": {
                "aliases": [
                    {
                        "alias": "ga4gh:SQ.lZyxiD_ByprhOUzrR1o1bq0ezO_1gkrn",
                        "naming_authority": "ga4gh",
                    },
                    {"alias": "I", "naming_authority": "unknown"},
                ],
                "length": 230218,
                "md5": "6681ac2f62509cfc220d78751b8dc524",
                "trunc512": "959cb1883fc1ca9ae1394ceb475a356ead1ecceff5824ae7",
            }
        }

    def test_metadata_url_list(self):


        logger.log("DEBUG", metadata_url_list(self.checksum))
        assert metadata_url_list(self.checksum) == [
            {'refget_server_url': 'http://test.service.refget.review.ensembl.org/',
             'checksum': '6681ac2f62509cfc220d78751b8dc524',
             'metadata_url': 'http://test.service.refget.review.ensembl.org/sequence/6681ac2f62509cfc220d78751b8dc524/metadata',
             'is_url': True}]


if __name__ == "__main__":
    unittest.main()
