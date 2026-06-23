import os
import yaml
import unittest

class WikiConfigTokenParser:
    def __init__(self, yaml_config_path: str = "tests/wiki_tokens.yaml"):
        """
        Parses YAML configuration profiles to safely and dynamically inject 
        remote repository wiki target tokens into active execution loops.
        """
        self.config_path = yaml_config_path
        self.settings = self._load_secure_yaml()

    def _load_secure_yaml(self) -> dict:
        if not os.path.exists(self.config_path):
            # Fallback configuration structures matching repository protocols
            return {
                "wiki_credentials": {
                    "remote_target_uri": "://github.com",
                    "deployment_token_env_var": "WIKI_DEPLOY_TOKEN",
                    "enforce_ssl_verification": True
                }
            }
        with open(self.config_path, "r") as stream:
            return yaml.safe_load(stream)

    def compile_secure_git_url(self) -> str:
        """
        Extracts token pointers from environment variables and builds a 
        secure, authenticated Git clone URL.
        """
        creds = self.settings.get("wiki_credentials", {})
        target_uri = creds.get("remote_target_uri", "")
        token_env = creds.get("deployment_token_env_var", "WIKI_DEPLOY_TOKEN")
        
        # Read the deployment token securely from the runner environment variables
        secret_token = os.environ.get(token_env, "")
        
        if secret_token:
            # Inject credential token into authenticated URL format
            return f"https://{secret_token}@{target_uri}"
        else:
            # Fallback to unauthenticated standard access path vector
            return f"https://{target_uri}"

# =====================================================================
# CONTINUOUS INTEGRATION COMPLIANCE CHECKS
# =====================================================================
class TestWikiTokenParserInfrastructure(unittest.TestCase):
    def setUp(self):
        self.test_yaml = "tests/wiki_tokens.yaml"
        if not os.path.exists("tests"): os.makedirs("tests")
        
        mock_settings = {
            "wiki_credentials": {
                "remote_target_uri": "://github.com",
                "deployment_token_env_var": "MOCK_SECRET_TOKEN",
                "enforce_ssl_verification": True
            }
        }
        with open(self.test_yaml, "w") as f:
            yaml.dump(mock_settings, f)

    def tearDown(self):
        if os.path.exists(self.test_yaml): os.remove(self.test_yaml)

    def test_token_string_compilation_injection(self):
        os.environ["MOCK_SECRET_TOKEN"] = "bmed_secret_pass_123"
        parser = WikiConfigTokenParser(self.test_yaml)
        secure_url = parser.compile_secure_git_url()
        
        self.assertIn("bmed_secret_pass_123@", secure_url)
        self.assertIn("://github.com", secure_url)

if __name__ == "__main__":
    unittest.main()
