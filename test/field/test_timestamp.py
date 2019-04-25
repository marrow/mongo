from common import FieldExam
from marrow.mongo.field import Timestamp


class TestTimestampField(FieldExam):
	__field__ = Timestamp
