import unittest

from fastapi.testclient import TestClient

from api.resources.sequence import metadata_url_list
from main import app


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.api_prefix = 'api'
        self.sequence_url_prefix = "api/sequence/"
        self.metadata_url_prefix = "/metadata/"
        self.checksum = "6681ac2f62509cfc220d78751b8dc524"
        self.url = self.sequence_url_prefix + self.checksum

    def test_404_error_in_none_relative_requests(self):
        response = self.client.get("api/")

        assert response.status_code == 404

    def test_api_error_405_page(self):
        post_response = self.client.post(self.url)
        assert post_response.status_code == 405

        patch_response = self.client.patch(self.url)
        assert patch_response.status_code == 405

        delete_response = self.client.delete(self.url)
        assert delete_response.status_code == 405

        put_response = self.client.put(self.url)
        assert put_response.status_code == 405

    def test_metadata_url_list(self):
        assert metadata_url_list(self.checksum) == [('http://hx-rke-wp-webadmin-14-worker-1.caas.ebi.ac.uk:31136/', 'http://hx-rke-wp-webadmin-14-worker-1.caas.ebi.ac.uk:31136/sequence/6681ac2f62509cfc220d78751b8dc524/metadata')]


if __name__ == "__main__":
    unittest.main()
