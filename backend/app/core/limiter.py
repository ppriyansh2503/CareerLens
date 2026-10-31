import os
import sys
from slowapi import Limiter
from slowapi.util import get_remote_address

# Default rate limiter for CareerLens API (200 requests/minute per client IP)
# Automatically disabled during pytest execution to prevent test suite throttling
is_test_env = "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    headers_enabled=False,
    enabled=not is_test_env
)
