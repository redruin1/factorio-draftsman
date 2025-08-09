# version.py

import draftsman


class TestVersion:
    def test_versions(self):
        assert draftsman.__version__ == "3.0.0"
        assert draftsman.__version_info__ == (3, 0, 0)
