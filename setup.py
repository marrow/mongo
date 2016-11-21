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

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-capturelog',  # log capture
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
	keywords = '',
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
	
	# ## Dependency Declaration
	
	setup_requires = [
			'pytest-runner',
		] if {'pytest', 'test', 'ptr'}.intersection(sys.argv) else [],
	
	install_requires = [
			'marrow.schema>=1.2.0,<2.0.0',  # Declarative schema support.
			'marrow.package>=1.1.0,<2.0.0',  # Plugin discovery and loading.
			'pymongo>=3.2',  # We require modern API.
			'pytz',  # Timezone support.
		],
	
	extras_require = dict(
			development = tests_require + ['pre-commit'],  # Development-time dependencies.
			scripting = ['javascripthon<1.0'],  # Allow map/reduce functions and "stored functions" to be Python.
			logger = ['tzlocal'],  # Timezone support to store log times in UTC like a sane person.
		),
	
	tests_require = tests_require,
	
	# ## Plugin Registration
	
	entry_points = {
				# ### Marrow Mongo Lookups
				'marrow.mongo.document': [  # Document classes registered by name.
						'Document = marrow.mongo.core:Document',
					],
				'marrow.mongo.field': [  # Field classes registered by (optionaly namespaced) name.
						'Field = marrow.mongo.core.field:Field',
						'String = marrow.mongo.core.field.base:String',
						'Binary = marrow.mongo.core.field.base:Binary',
						'ObjectId = marrow.mongo.core.field.base:ObjectId',
						'Boolean = marrow.mongo.core.field.base:Boolean',
						'Date = marrow.mongo.core.field.base:Date',
						'TTL = marrow.mongo.core.field.base:TTL',
						'Regex = marrow.mongo.core.field.base:Regex',
						'Timestamp = marrow.mongo.core.field.base:Timestamp',
						'Array = marrow.mongo.core.field.complex:Array',
						'Embed = marrow.mongo.core.field.complex:Embed',
						'Reference = marrow.mongo.core.field.complex:Reference',
						'PluginReference = marrow.mongo.core.field.complex:PluginReference',
						'Number = marrow.mongo.core.field.number:Number',
						'Double = marrow.mongo.core.field.number:Double',
						'Integer = marrow.mongo.core.field.number:Integer',
						'Long = marrow.mongo.core.field.number:Long',
					],
				# ### WebCore Extensions
				'web.session': [  # Session Engine
						'mongo = web.session.mongo:MongoSession',
					],
			},
)
