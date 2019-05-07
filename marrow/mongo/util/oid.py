"""An ObjectID implementation independent from the `bson` package bundled with PyMongo.

Within this module are implementations of all known `ObjectId` generation methods and interpretations. This is
provided primarily as a mechanism to utilize or transition older IDs on modern systems, as well as to provide an
option if you prefer the guarantees and information provided by older versions, moving forwards.

Notably, `ObjectId` was originally[1] defined (< MongoDB 3.3) as a combination of:

* 4-byte UNIX timestamp.
* 3-byte machine identifier.
* 2-byte process ID.
* 3-byte counter with random IV on process start.

The server itself never had a complex interpretation, treating the data after the timestamp as an "arbitrary node
identifier" followed by counter. The documentation and client drivers were brought more in-line with this intended
lack of structure[2] replacing the hardware and process identifiers with literal random data initialized on process
startup. As such, the modern structure is comprised of:

* 4-byte UNIX timestamp.
* 5-byte random process identifier. ("Random value" in the docs.)
* 3-byte counter with random IV on process start.

Additionally, the mechanism used to determine the hardware identifier has changed in the past. Initially it used a
substring segment of the hex encoded result of hashing the value returned by `gethostname()`. For FIPS compliance use
of MD5 was eliminated and a custom FNV implementation added. We avoid embedding yet another hashing implementation in
our own code and simply utilize the `fnv` package, if installed. (This will be automatically installed if your own
application depends upon `marrow.mongo[fips]`.)

To determine which approach is used for generation, specify the `hwid` argument to the ObjectId constructor.
Possibilities include:

* The string `legacy`: use the host name MD5 substring value and process ID. _Note if FIPS compliance is enabled, the
  md5 hash will literally be unavailable for use, resulting in the inability to utilize this choice._
* The string `fips`: use the FIPS-compliant FNV hash of the host name, and process ID.
* The string `random`: pure random bytes, the default, aliased as "modern".
* Any 5-byte bytes value: use the given HWID explicitly.

You are permitted to add additional entries to this mapping within your own application, if desired.

Unlike the PyMongo-supplied ObjectId implementation, this does not use a custom `Exception` class to represent invalid
values. TypeError will be raised if passed a value not able to be stringified, ValueError if the resulting string is
not 12 binary bytes or 24 hexadecimal digits. _**Warning:** any 12-byte `bytes` value will be accepted as-is._

Additional points of reference:

* [Implement ObjectId spec](https://jira.mongodb.org/browse/DRIVERS-499)
* [Python Driver Deprecation/Removal of MD5](https://jira.mongodb.org/browse/PYTHON-1521)
* [Java Driver "Make ObjectId conform to specification"](https://jira.mongodb.org/browse/JAVA-749)
* [ObjectID documentation should replace Process and Machine ID with 5-byte random value](https://jira.mongodb.org/browse/DOCS-11844)
* [ObjectId MachineId uses network interface names instead of mac address or something more unique](https://jira.mongodb.org/browse/JAVA-586)

[1] https://docs.mongodb.com/v3.2/reference/method/ObjectId/
[2] https://docs.mongodb.com/v3.4/reference/method/ObjectId/
"""

from binascii import hexlify, unhexlify
from datetime import datetime, timedelta
from os import getpid, urandom
from random import randint
from socket import gethostname
from struct import pack, unpack
from threading import RLock
from time import time

from bson import ObjectId as _OID
from bson.tz_util import utc

from ..core.types import Union, Optional, check_argument_types


# HWID calculation. This happens once, the first time this module is imported. Availability of choices depend on the
# ability to import the given hashing algorithm, e.g. `legacy` will be unavailable if `hashlib.md5` is unavailable.
# Feel free to expand upon these choices within your own application by updating `marrow.mongo.util.oid.HWID`.

_hostname = gethostname().encode()  # Utilized by the legacy HWID generation approaches.
HWID = {'random': urandom(5)}  # A mapping of abstract alias to hardware identification value, defaulting to random.
HWID['modern'] = HWID['random']  # Convenient alias as an antonym of "legacy".

try:  # This uses the old (<3.7) MD5 approach, which is not FIPS-safe despite having no cryptographic requirements.
	from hashlib import md5
	HWID['legacy'] = int(md5(_hostname).hexdigest()[:6], 16)
except ImportError:
	pass

try:  # A HWID variant matching MongoDB >=3.7 use of FNV-1a for FIPS compliance.
	import fnv
	_fnv = fnv.hash(_hostname, fnv.fnv_1a, bits=32)
	_fnv = (_fnv >> 24) ^ (_fnv & 0xffffff)  # XOR-fold to 24 bits.
	HWID['fips'] = pack('<I', _fnv)[:3]
except ImportError:
	pass


class _Counter:
	"""A thread-safe atomically incrementing counter.
	
	That itertools.count is thread-safe is a byproduct of the GIL on CPython, not an intentional design decision. As a
	result it can not be relied upon, thus we implement our own with proper locking.
	"""
	
	value: int
	lock: RLock
	
	def __init__(self):
		self.value = randint(0, 2**24)
		self.lock = RLock()
	
	def __iter__(self):
		return self
	
	def __next__(self):
		with self.lock:
			self.value = (self.value + 1) % 0xFFFFFF
			value = self.value
		
		return value
	
	next = __next__

_counter = _Counter()


class ObjectID:
	_type_marker = 0x07  # BSON ObjectId
	
	def __init__(self, value=None, hwid='random'):
		if value:
			self.parse(value)
		else:
			self.generate(hwid)
	
	def parse(self, value):
		self.time = int(value[:8], 16)
		self.machine = int(value[8:14], 16)
		self.process = int(value[14:18], 16)
		self.counter = int(value[18:24], 16)
	
	def generate(self, hwid='random'):
		self.time = int(time())
		self.counter = next(_counter)
		
		if hwid in ('legacy', 'fips'):
			self.machine = HWID[hwid]
			self.process = getpid() % 0xFFFF  # Can't be precomputed and included in HWID as Python may fork().
		
		elif isinstance(hwid, bytes):
			if len(hwid) != 5:
				raise ValueError("Binary hardware ID must have exact length: 5 bytes, not {}.".format(len(hwid)))
			
			self.hwid = hwid
		
		else:
			self.hwid = HWID[hwid]
	
	@property
	def hwid(self):
		return self.machine + self.process
	
	@hwid.setter
	def hwid(self, value: Union[str, bytes]):
		if isinstance(value, str):
			if len(value) != 10:
				raise ValueError("Hardware identifier must be a 5-byte binary value or 10-character hexadecimal string.")
			
			value = unhexlify(value)
		
		else:
			value = bytes(value)
		
		if len(value) != 5:
			raise ValueError("Hardware identifier must be a 5-byte binary value or 10-character hexadecimal string.")
		
		self.machine = value[:3]
		self.process = value[3:]
	
	@property
	def generation_time(self):
		"""Retrieve the generation time as a native datetime object in UTC."""
		return datetime.fromtimestamp(self.time).replace(tzinfo=utc)
	
	@generation_time.setter
	def generation_time(self, value:datetime):
		"""Assign/replace the generation time of this ObjectId."""
		assert check_argument_types()
		self.time = datetime.timestamp(value)
	
	def __bytes__(self):
		return b"{self.time:04s}{self.machine:03s}{self.process:02s}{self.counter:03s}".format(self=self)
	
	def __str__(self):
		return "{self.time:08x}{self.machine:06x}{self.process:04x}{self.counter:06x}".format(self=self)
	
	def __repr__(self):
		return "{self.__class__.__name__}('{self}', generated='{when}')".format(self=self, when=self.generation_time.isoformat())
