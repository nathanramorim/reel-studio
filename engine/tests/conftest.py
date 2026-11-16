import json
from pathlib import Path

import pytest


@pytest.fixture
def transcript() -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / "transcript.json").read_text())
