import unittest

from scripts.probe_foundry import QUERY, evaluation_schema, inline_source, settings


class ProbeContractsTests(unittest.TestCase):
    def setUp(self):
        self.environ = {
            "AZURE_AI_PROJECT_ENDPOINT": (
                "https://example.services.ai.azure.com/api/projects/example/"
            ),
            "AZURE_TENANT_ID": "00000000-0000-0000-0000-000000000001",
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": "example-model",
        }

    def test_valid_configuration_normalizes_endpoint(self):
        endpoint, tenant, model = settings(self.environ)
        self.assertFalse(endpoint.endswith("/"))
        self.assertEqual(tenant, self.environ["AZURE_TENANT_ID"])
        self.assertEqual(model, "example-model")

    def test_rejects_invalid_endpoints(self):
        endpoints = (
            "http://example.services.ai.azure.com/api/projects/example",
            "https://example.com/api/projects/example",
            "https://example.services.ai.azure.com.evil.example/api/projects/example",
            "https://user:password@example.services.ai.azure.com/api/projects/example",
            "https://example.services.ai.azure.com:8443/api/projects/example",
            "https://example.services.ai.azure.com/api/projects/",
            "https://example.services.ai.azure.com/api/projects/example?token=example",
            "https://example.services.ai.azure.com/api/projects/example#fragment",
            "https://example.services.ai.azure.com/api/projects/example/extra",
        )
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    settings({**self.environ, "AZURE_AI_PROJECT_ENDPOINT": endpoint})

    def test_requires_tenant_and_model(self):
        for field in ("AZURE_TENANT_ID", "AZURE_AI_MODEL_DEPLOYMENT_NAME"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    settings({**self.environ, field: ""})

    def test_inline_data_matches_schema(self):
        data = inline_source("Freeze the card and contact bank support.")
        self.assertEqual(data["type"], "jsonl")
        self.assertEqual(data["source"]["type"], "file_content")
        self.assertEqual(len(data["source"]["content"]), 1)
        item = data["source"]["content"][0]["item"]
        self.assertEqual(item["query"], QUERY)
        self.assertEqual(set(item), set(evaluation_schema()["item_schema"]["required"]))

    def test_rejects_empty_answer(self):
        for answer in ("", "  "):
            with self.subTest(answer=answer):
                with self.assertRaises(ValueError):
                    inline_source(answer)


if __name__ == "__main__":
    unittest.main()
