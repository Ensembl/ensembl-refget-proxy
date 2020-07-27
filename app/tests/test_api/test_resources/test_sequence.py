import unittest

from fastapi.testclient import TestClient
from loguru import logger

from main import app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.api_prefix = "api"
        self.sequence_url_prefix = "api/sequence/"
        self.metadata_url_prefix = "/metadata/"
        self.checksum = "6681ac2f62509cfc220d78751b8dc524"
        self.refget_url = "http://hx-rke-wp-webadmin-14-worker-1.caas.ebi.ac.uk:31136/"
        self.sequence_path = self.sequence_url_prefix + self.checksum
        self.sequence_not_found_path = self.sequence_url_prefix + "6681ac2f62751b8dc845"

    def test_404_error_in_none_relative_requests(self):
        response = self.client.get("api/")

        assert response.status_code == 404

    def test_api_error_404(self):
        get_response = self.client.get(self.sequence_not_found_path)
        logger.log('DEBUG', get_response)
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

    # def test_metadata_url_list(self):
    #     assert metadata_url_list(self.checksum) == [(self.refget_url,
    #                                                  self.refget_url + 'sequence/6681ac2f62509cfc220d78751b8dc524/metadata')]


if __name__ == "__main__":
    unittest.main()
