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


Rationale and Goals
-------------------


Installation
============

Installing ``marrow.mongo`` is easy, just execute the following in a terminal::

    pip install marrow.mongo

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`_, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`_.

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

Development takes place on `GitHub <https://github.com/>`_ in the
`marrow.mongo <https://github.com/marrow/mongo/>`_ project.  Issue tracking, documentation, and downloads
are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/mongo.git
    (cd mongo; python setup.py develop)

You can then upgrade to the latest version at any time::

    (cd mongo; git pull; python setup.py develop)

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`_.


Getting Started
===============



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

.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/cinje.svg?style=social&label=Watch
    :target: https://github.com/marrow/cinje/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/cinje.svg?style=social&label=Star
    :target: https://github.com/marrow/cinje/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/cinje.svg?style=social&label=Fork
    :target: https://github.com/marrow/cinje/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/cinje/master.svg?style=flat
    :target: https://travis-ci.org/marrow/cinje/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/cinje/master.svg?style=flat
    :target: https://codecov.io/github/marrow/cinje?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/cinje.svg
    :target: https://requires.io/github/marrow/cinje/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/cinje/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/cinje/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/cinje/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/cinje?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/cinje.svg
    :target: https://requires.io/github/marrow/cinje/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/cinje.svg?style=flat
    :target: https://github.com/marrow/cinje/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/cinje/1.0.svg
    :target: https://github.com/marrow/cinje/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/cinje.svg
    :target: https://github.com/marrow/cinje/tree/1.0
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/cinje.svg?style=flat
    :target: https://pypi.python.org/pypi/cinje
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/cinje.svg?style=flat
    :target: https://pypi.python.org/pypi/cinje
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat
