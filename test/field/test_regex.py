from common import FieldExam
from marrow.mongo.field import Regex


class RegexField(FieldExam):
	__field__ = Regex
