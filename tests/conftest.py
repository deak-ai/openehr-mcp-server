import os
import sys
import pytest
import asyncio
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# We don't need to define an event_loop fixture anymore
# pytest-asyncio provides this fixture by default
# Tests should use @pytest.mark.asyncio(scope="function") to specify the scope
