import unittest

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

from scripts.inspect_sdk import describe


class SDKContractsTests(unittest.TestCase):
    def test_preview_evaluator_catalog_contract(self):
        with AzureCliCredential() as credential:
            with AIProjectClient(
                endpoint="https://example.services.ai.azure.com/api/projects/example",
                credential=credential,
                allow_preview=True,
            ) as client:
                contract = describe(client.beta.evaluators)
                self.assertTrue(contract["available"])
                self.assertIn("list", contract["methods"])
                self.assertIn("type:", contract["methods"]["list"])
                self.assertNotIn("list_latest_versions", contract["methods"])

    def test_missing_operation_is_explicit(self):
        self.assertEqual(describe(None), {"available": False})


if __name__ == "__main__":
    unittest.main()
