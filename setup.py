#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import codecs

try:
	from setuptools.core import setup, find_packages
except ImportError:
	from setuptools import setup, find_packages


if sys.version_info < (2, 7):
	raise SystemExit("Python 2.7 or later is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 2):
	raise SystemExit("Python 3.2 or later is required.")

version = description = url = author = ''  # Actually loaded on the next line; be quiet, linter.
exec(open(os.path.join("marrow", "mongo", "core", "release.py")).read())

here = os.path.abspath(os.path.dirname(__file__))

py2 = sys.version_info < (3,)
py26 = sys.version_info < (2, 7)
py32 = sys.version_info > (3,) and sys.version_info < (3, 3)
pypy = hasattr(sys, 'pypy_version_info')

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-catchlog',  # log capture
		'pytest-isort',  # import ordering
		'misaka', 'pygments',  # Markdown field support
	]


# # Entry Point

setup(
	name = "marrow.mongo",
	version = version,
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	author = author.name,
	author_email = author.email,
	license = 'MIT',
	keywords = ['mongodb', 'GeoJSON', 'geospatial', 'full text', 'facted', 'orm', 'odm', 'document mapper',
			'declarative', 'marrow'],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.2",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Topic :: Utilities"
		],
	
	packages = find_packages(exclude=['test', 'example', 'benchmark', 'htmlcov']),
	include_package_data = True,
	package_data = {'': ['README.rst', 'LICENSE.txt']},
	namespace_packages = ['marrow', 'web', 'web.session'],
	zip_safe = False,
	
	# ## Dependency Declaration
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	
	install_requires = [
			'marrow.schema>=1.2.0,<2.0.0',  # Declarative schema support.
			'marrow.package>=1.1.0,<2.0.0',  # Plugin discovery and loading.
			'pymongo>=3.2',  # We require modern API.
			'pathlib2; python_version < "3.4"',  # Path manipulation utility.
		],
	
	extras_require = dict(
			decimal = ['pymongo>=3.4'],  # More modern version required for Decimal128 support.
			development = tests_require + ['pre-commit'],  # Development-time dependencies.
			scripting = ['javascripthon<1.0'],  # Allow map/reduce functions and "stored functions" to be Python.
			logger = ['tzlocal'],  # Timezone support to store log times in UTC like a sane person.
			markdown = ['misaka', 'pygments'],  # Markdown text storage.
		),
	
	tests_require = tests_require,
	
	# ## Plugin Registration
	
	entry_points = {
				# ### Marrow Mongo Lookups
				'marrow.mongo.document': [  # Document classes registered by name.
						'Document = marrow.mongo.core.document:Document',
						
						'GeoJSON = marrow.mongo.geo:GeoJSON',
						'GeoJSONCoord = marrow.mongo.geo:GeoJSONCoord',
						'Point = marrow.mongo.geo:Point',
						'LineString = marrow.mongo.geo:LineString',
						'Polygon = marrow.mongo.geo:Polygon',
						'MultiPoint = marrow.mongo.geo:MultiPoint',
						'MultiLineString = marrow.mongo.geo:MultiLineString',
						'MultiPolygon = marrow.mongo.geo:MultiPolygon',
						'GeometryCollection = marrow.mongo.geo:GeometryCollection',
					],
				'marrow.mongo.field': [  # Field classes registered by (optionaly namespaced) name.
						'Field = marrow.mongo.core.field:Field',
						
						'String = marrow.mongo.core.field.base:String',
						'Binary = marrow.mongo.core.field.base:Binary',
						'ObjectId = marrow.mongo.core.field.base:ObjectId',
						'Boolean = marrow.mongo.core.field.base:Boolean',
						'Date = marrow.mongo.core.field.base:Date',
						'TTL = marrow.mongo.core.field.base:TTL',
						'Period = marrow.mongo.core.field.base:Period',
						'Regex = marrow.mongo.core.field.base:Regex',
						'Timestamp = marrow.mongo.core.field.base:Timestamp',
						
						'Array = marrow.mongo.core.field.complex:Array',
						'Embed = marrow.mongo.core.field.complex:Embed',
						'Reference = marrow.mongo.core.field.complex:Reference',
						'PluginReference = marrow.mongo.core.field.complex:PluginReference',
						'Alias = marrow.mongo.core.field.complex:Alias',
						
						'Number = marrow.mongo.core.field.number:Number',
						'Double = marrow.mongo.core.field.number:Double',
						'Integer = marrow.mongo.core.field.number:Integer',
						'Long = marrow.mongo.core.field.number:Long',
						'Decimal = marrow.mongo.core.field.number:Decimal[decimal]',
						
						'Markdown = marrow.mongo.core.field.md:Markdown[markdown]',
						'Path = marrow.mongo.core.field.path:Path',
						'Translated = marrow.mongo.core.trait.localized:Translated',
					],
				'marrow.mongo.trait': [  # Document traits for use as mix-ins.
						# Active Collection Traits
						'Collection = marrow.mongo.core.trait.collection:Collection',
						'Queryable = marrow.mongo.core.trait.queryable:Queryable',
						
						# Behavioural Traits
						'Derived = marrow.mongo.core.trait.derived:Derived',
						'Expires = marrow.mongo.core.trait.expires:Expires',
						'Identified = marrow.mongo.core.trait.identified:Identified',
						'Localized = marrow.mongo.core.trait.localized:Localized',
						'Published = marrow.mongo.core.trait.published:Published',
						# 'Stateful = marrow.mongo.core.trait.stateful:Stateful',
						
						# Taxonomic Traits
						#'Heirarchical = marrow.mongo.core.trait.heir:Heirarchical',
						#'HChildren = marrow.mongo.core.trait.heir:HChildren',
						#'HParent = marrow.mongo.core.trait.heir:HParent',
						#'HAncestors = marrow.mongo.core.trait.heir:HAncestors',
						#'HPath = marrow.mongo.core.trait.heir:HPath',
						#'HNested = marrow.mongo.core.trait.heir:HNested',
						#'Taxonomy = marrow.mongo.core.trait.heir:Taxonomy',
					],
				# ### WebCore Extensions
				'web.session': [  # Session Engine
						'mongo = web.session.mongo:MongoSession',
					],
			},
)
