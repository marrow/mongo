============
marrow.mongo
============

    © 2016 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/mongo

..

    |latestversion| |ghtag| |downloads| |masterstatus| |mastercover| |masterreq| |ghwatch| |ghstar|



Introduction
============

Marrow Mongo is a collection of small, focused utilities written to enhance use of the `PyMongo native MongoDB driver
<http://api.mongodb.com/python/current/>`__ without the overhead, glacial update cycle, complexity, and head-space
requirements of a full active record object document mapper. Additionally, it provides a very light-weight database
connection plugin for the `WebCore web framework <https://github.com/marrow/WebCore>`__ and Python standard logging
adapter to emit logs to MongoDB.


Installation
============

Installing ``marrow.mongo`` is easy, just execute the following in a terminal::

    pip install marrow.mongo

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`__, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`__.

If you add ``marrow.mongo`` to the ``install_requires`` argument of the call to ``setup()`` in your application's
``setup.py`` file, marrow.mongo will be automatically installed and made available when your own application or
library is installed.  We recommend using "less than" version numbers to ensure there are no unintentional
side-effects when updating.  Use ``marrow.mongo<1.1`` to get all bugfixes for the current release, and
``marrow.mongo<2.0`` to get bugfixes and feature updates while ensuring that large breaking changes are not installed.

This package has only one hard dependency, a modern (>3.2) version of the ``pymongo`` package.  Installing
``marrow.mongo`` will also install this package.


Development Version
-------------------

    |developstatus| |developcover| |ghsince| |issuecount| |ghfork|

Development takes place on `GitHub <https://github.com/>`__ in the
`marrow.mongo <https://github.com/marrow/mongo/>`__ project.  Issue tracking, documentation, and downloads
are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`__, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/mongo.git
    (cd mongo; python setup.py develop)

You can then upgrade to the latest version at any time::

    (cd mongo; git pull; python setup.py develop)

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`__.


Documents
=========

This package utilizes the `Marrow Schema <https://github.com/marrow/schema>`__ declarative schema toolkit and extends
it to encompass MongoDB data storage concerns. You define data models by importing classes describing the various
components of a collection, such as ``Document``, ``ObjectId``, or ``String``, then compose them into a declarative
class model. For example, if you wanted to define a simple user account model, you would begin by importing::

    from marrow.mongo import Index, Document
    from marrow.mongo.field import ObjectId, String, Number, Array

One must always import ``Document`` from ``marrow.mongo.core`` prior to any import of registered fields from
``marrow.mongo``. As a note, due to the magical nature of this plugin import registry, it may change in future feature
releases. The old interface will be deprecated with a warning for one feature version first, however; pin your
dependencies.


Defining Documents
------------------

Now we can define our own ``Document`` subclass::

    class Account(Document):
        username = String(required=True)
        name = String()
        locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
        age = Number()
        
        id = ObjectId('_id', assign=True)
        tag = Array(String(), default=lambda: [], assign=True)
        
        _username = Index('username', unique=True)

Broken down::

    class Account(Document):

No surprises here, we subclass the Document class. This is required to utilize the metaclass that makes the
declarative naming and order-presrving sequence generation work. We begin to define fields::

    username = String(required=True)
    name = String()
    locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)

Introduced here is ``required``, indicating that when generating the *validation document* for this document to
ensure this field always has a value. This validation is not currently performed application-side. Also notable is the
use of ``assign`` on a string field; this will assign the default value during instantiation. Then we have a different
type of field::

    age = Number()

This allows storage of any numeric value, either integer or floating point. Now there is the record identifier::

    id = ObjectId('_id', assign=True)

Marrow Mongo does not assume your documents contain IDs; there is no separation internally between top-level documents
and "embedded documents", leaving the declaration of an ID up to you. You might not always wish to use an ObjectID,
either; please see MongoDB's documentation for discussion of general modelling practices. The first positional
parameter for most non-complex fields is the name of the MongoDB-side field. Underscores imply an attribute is
"protected" in Python, so we remap it by assigning it to just ``id``.  The ``assign`` argument here ensures whenever a
new ``Account`` is instantiated an ObjectID will be immediately generated and assigned.

Finally there is an array of tags::

    tag = Array(String(), default=lambda: [], assign=True)

This combines what we've been using so far into one field. An ``Array`` is a *complex field* (a container) and as such
the types of values allowed to be contained therein may be defined positionally. (If you want to override the field's
database-side name, pass in a ``name`` as a keyword argument.) A default is defined as an anonymous callback function
which constructs a new list on each request. The default will be executed and the result assigned automatically during
initialization as per ``id`` or ``locale``.

Lastly we define a unique index on the username to speed up any queries involving that field::

    _username = Index('username', unique=True)


Instantiating Documents
-----------------------

With a document schema defined we can now begin populating data::

    alice = Account('amcgregor', "Alice Bevan-McGregor", age=27)
    print(alice.id)  # Already has an ID.
    print(alice.id.generation_time)  # This even includes the creation time.

As can be seen above construction accepts positional and keyword parameters. Fields will be filled, positionally, in
the order they were defined, unless otherwise adjusted using the ``adjust_attribute_sequence`` decorator.

Assuming a ``pymongo`` collection is accessible by the variable name ``collection`` we can construct our index::

    Account._username.create_index(collection)

There is no need to run this command more than once unless the collection is dropped.

Let's insert our record::

    result = collection.insert_one(alice)
    assert result.acknowledged and result.inserted_id == alice.id

Yup, that's it. Instances of ``Document`` are directly usable in place of a dictionary argument to ``pymongo``
methods. We then validate that the document we wanted inserted was, in fact, inserted. Using an assert in this way,
this validation will not be run in production code run with the ``-O`` option passed (or ``PYTHONOPTIMIZE``
environment variable set) in the invocation to Python.


Querying Documents
------------------

Now that we have a document stored in the database, let's retrieve it back out and get the result as an ``Account``
instance::

    record = collection.find_one(Account.username == 'amcgregor')
    record = Account.from_mongo(record)
    print(record.name)  # Alice Bevan-McGregor

Several things are going on here. First it's important to note that Marrow Mongo isn't making the query happen for
you, and does not automatically cast dictionaries to ``Document`` subclasses when querying. The first line
demonstrates the native approach to building *filter documents*, the first argument to ``find`` or ``find_one``.

You can use standard Python comparison operators, bitwise operators, and several additional querying methods through
class-level access to the defined fields. The result of one of these operations or method calls is a dictionary-like
object that is the query. They may be combined through bitwise and (``&``) and bitwise or (``|``) operations, however
due to Python's order of operations, individual field comparisons must be wrapped in parenthesis if combining.

Combining produces a new ``Ops`` instance, so it is possible to use these to pre-construct parts of queries prior to
use. As a tip, it can save time (and visual clutter) to assign the document class to a short, single-character
variable name to make repeated reference easier.


Version History
===============

Version 1.0
-----------

* Initial release.


License
=======

marrow.mongo has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2016 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/mongo.svg?style=social&label=Watch
    :target: https://github.com/marrow/mongo/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/mongo.svg?style=social&label=Star
    :target: https://github.com/marrow/mongo/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/mongo.svg?style=social&label=Fork
    :target: https://github.com/marrow/mongo/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/mongo/master.svg?style=flat
    :target: https://travis-ci.org/marrow/mongo/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/mongo/master.svg?style=flat
    :target: https://codecov.io/github/marrow/mongo?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/mongo.svg
    :target: https://requires.io/github/marrow/mongo/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/mongo/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/mongo/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/mongo/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/mongo?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/mongo.svg
    :target: https://requires.io/github/marrow/mongo/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/mongo.svg?style=flat
    :target: https://github.com/marrow/mongo/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/mongo/1.0.0.svg
    :target: https://github.com/marrow/mongo/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/mongo.svg
    :target: https://github.com/marrow/mongo/tree/1.0.0
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/marrow.mongo.svg?style=flat
    :target: https://pypi.python.org/pypi/marrow.mongo
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/marrow.mongo.svg?style=flat
    :target: https://pypi.python.org/pypi/marrow.mongo
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat
