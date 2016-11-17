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

    from marrow.mongo.core import Document, Index
    from marrow.mongo.util import adjust_attribute_sequence
    from marrow.mongo import ObjectId, String, Array

One must always import ``Document`` from ``marrow.mongo.core`` prior to any import of registered fields from
``marrow.mongo``. As a note, due to the magical nature of this plugin import registry, it may change in future feature
releases. The old interface will be deprecated with a warning for one feature version first, however; pin your
dependencies.


Defining Documents
------------------

Now we can define our own ``Document`` subclass::

    @adjust_attribute_sequence(id=10000)
    class Account(Document):
        id = ObjectId('_id', assign=True)
        username = String(required=True)
        name = String()
        locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)
        
        _username = Index('username', unique=True)

Let's break that down a bit::

    @adjust_attribute_sequence(id=10000)

This changes the "sequence" for the named fields, adjusting where in the positional paramater list it shows up, and
its order in the final ordere dictionary. In this case, it's not very useful to always specify the ID positionally
frist, so we shift it to "the end".  Next::

    class Account(Document):

No surprises here, we subclass the Document class. This is required to utilize the metaclass that makes the
declarative naming and order-presrving sequence generation work. We begin to define fields::

    id = ObjectId('_id', assign=True)

Marrow Mongo does not assume your documents contain IDs; there is no separation internally between top-level documents
and "embedded documents", leaving the declaration of an ID up to you. You might not always wish to use an ObjectID,
either; please see MongoDB's documentation for discussion of general modelling practices. The first positional
parameter for most non-complex fields is the name of the MongoDB-side field. Underscores imply an attribute is
"protected" in Python, so we remap it by assigning it to just ``id``.  The ``assign`` argument here ensures whenever a
new ``Account`` is instantiated an ObjectID will be immediately generated and assigned.

The remaining fields should contain no surprises::

    username = String(required=True)
    name = String()
    locale = String(default='en-CA-u-tz-cator-cu-CAD', assign=True)

Introduced here are ``required``, indicating that when generating the *validation document* for this document to
ensure this field always has a value. This validation is not currently performed application-side. Also notable is the
use of ``assign`` on a string field; this will assign the default value during instantiation.  Lastly::

    _username = Index('username', unique=True)

We define a unique index on the username to speed up any queries involving that record.


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

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/mongo/1.0.svg
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
