#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import codecs

try:
	from setuptools.core import setup, find_packages
except ImportError:
	from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand


if sys.version_info < (2, 7):
	raise SystemExit("Python 2.7 or later is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 2):
	raise SystemExit("Python 3.2 or later is required.")

exec(open(os.path.join("marrow", "mongo", "core", "release.py")).read())


class PyTest(TestCommand):
	def finalize_options(self):
		TestCommand.finalize_options(self)
		
		self.test_args = []
		self.test_suite = True
	
	def run_tests(self):
		import pytest
		sys.exit(pytest.main(self.test_args))


here = os.path.abspath(os.path.dirname(__file__))

tests_require = ['pytest', 'pytest-cov', 'pytest-spec', 'pytest-flakes']


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
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"Topic :: Utilities"
		],
	
	packages = find_packages(exclude=['test', 'example', 'benchmark']),
	include_package_data = False,
	
	# ## Dependency Declaration
	
	install_requires = [
			'pymongo>=3.2',  # We require modern API.
		],
	
	extras_require = dict(
			development = tests_require,
		),
	
	tests_require = tests_require,
	
	# ## Plugin Registration
	
	entry_points = {
				'marrow.mongo.field': [
						'Field = marrow.mongo.core.field:Field',
						'String = marrow.mongo.field.base:String',
						'Array = marrow.mongo.field.base:Array',
						'Binary = marrow.mongo.field.base:Binary',
						'ObjectId = marrow.mongo.field.base:ObjectId',
						'Boolean = marrow.mongo.field.base:Boolean',
						'Date = marrow.mongo.field.base:Date',
						'Regex = marrow.mongo.field.base:Regex',
						'JavaScript = marrow.mongo.field.base:JavaScript',
						'Timestamp = marrow.mongo.field.base:Timestamp',
						'Embed = marrow.mongo.field.complex:Embed',
						'Reference = marrow.mongo.field.complex:Reference',
						'Number = marrow.mongo.field.number:Number',
						'Double = marrow.mongo.field.number:Double',
						'Integer = marrow.mongo.field.number:Integer',
						'Long = marrow.mongo.field.number:Long',
					]
			},
	
	zip_safe = False,
	cmdclass = dict(
			test = PyTest,
		)
)
