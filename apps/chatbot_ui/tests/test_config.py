import unittest

from chatbot_ui.core.config import config


class ConfigTests(unittest.TestCase):
    def test_config_loads_with_repo_env_file(self) -> None:
        self.assertIsNotNone(config)
        self.assertTrue(hasattr(config, "API_URL"))


if __name__ == "__main__":
    unittest.main()
