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


class _Component:
	"""An object representing a component part of the larger binary ObjectID structure.
	
	This allows the definition of a range of bytes from the binary representation, with automatic extraction from the
	compound value on get, and replacement of the relevant portion of the compound value on set. Deletion will null;
	replace with zeroes.
	"""
	
	__slots__ = ('_slice', )
	
	def __getitem__(self, item):
		self._slice = item
		return self
	
	def __get__(self, instance, owner):
		return instance.binary[self._slice]
	
	def __set__(self, instance, value):
		if isinstance(value, str):
			value = unhexlify(value)
		
		start, stop, skip = self._slice.indices(12)
		l = stop - start
		
		if len(value) > l:  # Trim over-large values
			# We encode a 3-byte value as a 4-byte integer, thus need to trim it for storage.
			value = value[len(value) - l:]
		
		binary = bytearray(instance.binary)
		binary[self._slice] = value
		instance.binary = bytes(binary)
	
	def __delete__(self, instance):
		value = bytearray(instance.binary)
		value[self._slice] = '\0' * len(range(start, stop, skip))


class _Numeric(_Component):
	__slots__ = ('struct', )
	
	def __init__(self, struct='>I'):
		self.struct = struct
	
	def __get__(self, instance, owner) -> int:
		value = super().__get__(instance, owner)
		return unpack(self.struct, value)[0]
	
	def __set__(self, instance, value: int):
		assert check_argument_types()
		
		value = pack(self.struct, value)
		super().__set__(instance, value)


class _Timestamp(_Numeric):
	def __get__(self, instance, owner) -> datetime:
		value = super().__get__(instance, owner)
		return datetime.fromtimestamp(value).replace(tzinfo=utc)
	
	def __set__(self, instance, value:Union[int,datetime,timedelta]):
		assert check_argument_types()
		
		if not isinstance(value, int):
			if isinstance(value, timedelta):
				value = datetime.utcnow() + value
			
			value = datetime.timestamp(value)
		
		super().__set__(instance, value)


class ObjectID(_OID):
	__slots__ = ('binary', )
	
	_type_marker = 0x07  # BSON ObjectId
	
	time = generation_time = _Timestamp('!L')[:4]
	machine = _Component()[4:7]
	process = _Numeric('!H')[7:9]
	counter = _Numeric('!I')[9:]
	
	hwid = _Component()[4:9]  # Compound of machine + process, used esp. in later versions as random.
	
	def __init__(self, value:Optional[Union[str,bytes,_OID,datetime,timedelta]]=None, hwid='random'):
		assert check_argument_types()
		
		self.binary = b'\x00' * 12
		
		if value:
			self.parse(value)
		else:
			self.generate(hwid)
	
	@classmethod
	def from_datetime(ObjectID, when:Union[datetime,timedelta]):
		"""Construct a mock ObjectID whose only populated field is a specific generation time.
		
		This is useful for performing range queries (e.g. records constructed after X `datetime`). To enhance such use
		this reimplementation allows you to pass an explicit datetime instance, or a timedelta relative to now.
		
		All dates will be stored in UTC.
		"""
		
		assert check_argument_types()
		
		if isinstance(when, timedelta):  # If provided a relative moment, assume it's relative to now.
			when = datetime.utcnow() + when
		
		if when.utcoffset() is not None:  # Normalize to UTC.
			when = when - when.utcoffset()
		
		ts = datetime.timestamp(when)
		packed = pack('>I', ts)
		oid = b"{packed}\0\0\0\0\0\0\0\0"
		
		return ObjectID(oid)
	
	@classmethod
	def is_valid(ObjectID, oid):
		"""Identify if the given identifier will parse successfully as an ObjectID."""
		
		try:
			ObjectID(oid)
		except (TypeError, ValueError):
			return False
		
		return True
	
	def parse(self, value):
		if isinstance(value, bytes):
			value = hexlify(value).decode()
		
		value = str(value)  # Casts bson.ObjectId as well.
		
		if len(value) != 24:
			raise ValueError("ObjectID must be a 12-byte binary value or 24-character hexidecimal string.")
		
		self.binary = unhexlify(value)
	
	def generate(self, hwid='random'):
		self.time = int(time())  # 4 byte timestamp.
		
		if hwid in ('legacy', 'fips'):  # Machine + process identification.
			self.machine = HWID[hwid]
			self.process = getpid() % 0xFFFF  # Can't be precomputed and included in HWID as Python may fork().
		
		elif isinstance(hwid, bytes):  # 5-byte explicit value
			if len(hwid) != 5:
				raise ValueError("Binary hardware ID must have exact length: 5 bytes, not {}.".format(len(hwid)))
			
			self.hwid = hwid
		
		else:  # 5-byte identifier from catalog.
			self.hwid = HWID[hwid]
		
		# 3 bytes incremental counter, random IV on process start.
		self.counter = next(_counter)
	
	def __getstate__(self):
		"""Return a value suitable for picle serialization."""
		return self.binary
	
	def __setstate__(self, value):
		"""Restore state after pickle deserialization."""
		self.binary = value
	
	def __str__(self):
		return hexlify(self.binary).decode()
	
	def __bytes__(self):
		return self.binary
	
	def __repr__(self):
		return f"{self.__class__.__name__}('{self}', generated='{self.generation_time.isoformat()}')"
	
	def __eq__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary == other.binary
	
	def __ne__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary != other.binary
	
	def __lt__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary < other.binary
	
	def __le__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary <= other.binary
	
	def __gt__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary > other.binary

	def __ge__(self, other):
		try:
			other = ObjectID(other)
		except (TypeError, ValueError):
			return NotImplemented
		
		return self.binary >= other.binary
	
	def __hash__(self):
		"""Get a hash value for this :class:`ObjectId`."""
		return hash(self.binary)
