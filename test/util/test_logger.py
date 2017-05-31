# encoding: utf-8

import pytest

try:
	from marrow.mongo.util.logger import JSONFormatter, MongoFormatter, MongoHandler

except ImportError:
	pytestmark = pytest.mark.skip(reason="Local timezone support library tzlocal not installed.")


def test_nothing():
	JSONFormatter, MongoFormatter, MongoHandler
