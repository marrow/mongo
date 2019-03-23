#!/usr/bin/env python3

from setuptools import setup
from sys import argv, version_info as python_version
from pathlib import Path


if python_version < (3, 5):
	raise SystemExit("Python 3.5 or later is required.")

here = Path(__file__).resolve().parent
exec((here / "marrow" / "mongo" / "release.py").read_text('utf-8'))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-isort',  # import ordering
		'misaka', 'pygments',  # Markdown field support
		'pytz', 'tzlocal>=1.4',  # timezone support, logger support
	]


setup(
	name = "marrow.mongo",
	version = version,
	
	description = description,
	long_description = (here / 'README.rst').read_text('utf-8'),
	url = url,
	
	author = author.name,
	author_email = author.email,
	
	license = 'MIT',
	keywords = ('mongodb', 'GeoJSON', 'geospatial', 'full text', 'facted', 'orm', 'odm', 'document mapper',
			'declarative', 'marrow'),
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: 3.6",
			"Programming Language :: Python :: 3.7",
			"Programming Language :: Python :: 3.8",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Topic :: Utilities"
		],
	
	packages = ('marrow.mongo', 'web.session'),
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	zip_safe = False,
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	
	install_requires = [
			'uri>=2.0.0,<3.0.0',  # Generic URI datastructure.
			'marrow.schema>=1.2.0,<2.0.0',  # Declarative schema support.
			'marrow.package>=1.1.0,<2.0.0',  # Plugin discovery and loading.
			'pymongo>=3.2',  # We require modern API.
		],
	
	extras_require = dict(
			decimal = ['pymongo>=3.4'],  # More modern version required for Decimal128 support.
			development = tests_require + ['pre-commit', 'bandit'],  # Development-time dependencies.
			logger = ['tzlocal>=1.4'],  # Timezone support to store log times in UTC like a sane person.
			markdown = ['misaka', 'pygments'],  # Markdown text storage.
			scripting = ['javascripthon<1.0'],  # Allow map/reduce functions and "stored functions" to be Python.
			tz = ['pytz', 'tzlocal>=1.4'],  # Support for timezones.
			timezone = ['pytz', 'tzlocal>=1.4'],  # Alias for the above timezone support.
		),
	
	tests_require = tests_require,
	
	entry_points = {
				# ### Marrow Mongo Lookups
				'marrow.mongo.document': [  # Document classes registered by name.
						'Document = marrow.mongo.core.document:Document',
						'GeoJSON = marrow.mongo.geo:GeoJSON',
						'GeoJSONCoord = marrow.mongo.geo:GeoJSONCoord',
						'GeometryCollection = marrow.mongo.geo:GeometryCollection',
						'LineString = marrow.mongo.geo:LineString',
						'MultiLineString = marrow.mongo.geo:MultiLineString',
						'MultiPoint = marrow.mongo.geo:MultiPoint',
						'MultiPolygon = marrow.mongo.geo:MultiPolygon',
						'Point = marrow.mongo.geo:Point',
						'Polygon = marrow.mongo.geo:Polygon',
					],
				'marrow.mongo.field': [  # Field classes registered by (optionaly namespaced) name.
						'Alias = marrow.mongo.core.field.alias:Alias',
						'Array = marrow.mongo.core.field.array:Array',
						'Binary = marrow.mongo.core.field.binary:Binary',
						'Boolean = marrow.mongo.core.field.boolean:Boolean',
						'Date = marrow.mongo.core.field.date:Date',
						'Decimal = marrow.mongo.core.field.decimal_:Decimal[decimal]',
						'Double = marrow.mongo.core.field.double:Double',
						'Embed = marrow.mongo.core.field.embed:Embed',
						'Field = marrow.mongo.core.field.base:Field',
						'Integer = marrow.mongo.core.field.integer:Integer',
						'Link = marrow.mongo.core.field.link:Link',
						'Long = marrow.mongo.core.field.long_:Long',
						'Markdown = marrow.mongo.core.field.md:Markdown[markdown]',
						'Number = marrow.mongo.core.field.number:Number',
						'ObjectId = marrow.mongo.core.field.oid:ObjectId',
						'Path = marrow.mongo.core.field.path:Path',
						'Period = marrow.mongo.core.field.period:Period',
						'PluginReference = marrow.mongo.core.field.plugin:PluginReference',
						'Reference = marrow.mongo.core.field.reference:Reference',
						'Regex = marrow.mongo.core.field.regex:Regex',
						'Set = marrow.mongo.core.field.set_:Set',
						'String = marrow.mongo.core.field.string:String',
						'TTL = marrow.mongo.core.field.ttl:TTL',
						'Timestamp = marrow.mongo.core.field.timestamp:Timestamp',
						'Translated = marrow.mongo.core.trait.localized:Translated',
						'Mapping = marrow.mongo.core.field.mapping:Mapping',
					],
				'marrow.mongo.trait': [  # Document traits for use as mix-ins.
						'Collection = marrow.mongo.core.trait.collection:Collection',
						'Derived = marrow.mongo.core.trait.derived:Derived',
						'Expires = marrow.mongo.core.trait.expires:Expires',
						'Identified = marrow.mongo.core.trait.identified:Identified',
						'Localized = marrow.mongo.core.trait.localized:Localized',
						'Published = marrow.mongo.core.trait.published:Published',
						'Queryable = marrow.mongo.core.trait.queryable:Queryable',
						'Lockable = marrow.mongo.core.trait.lockable:Lockable',
					],
				# ### WebCore Extensions
				'web.session': [  # Session Engine
						'mongo = web.session.mongo:MongoSession',
					],
			},
)
