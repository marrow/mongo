# Installation

Installation is easy using the `pip` package manager.

{% method -%}
**Requirements**

* [Python](https://www.python.org) 2.7 or 3.2 and above, or compatible runtime such as [Pypy](http://pypy.org) or Pypy3.
* An accessible [MongoDB](https://www.mongodb.com/) installation; some features may require MongoDB version 3.2, decimal support requires version 3.4.

{% sample lang="bash" -%}
```bash
pip install marrow.mongo
```
{% endmethod %}

## Dependencies

> #### info::Dependency Isolation
> 
> We strongly recommend always using a container, virtualization, or sandboxing environment of some kind when developing using Python; installing things system-wide is yucky \(for a variety of reasons\) nine times out of ten.
> 
> We prefer light-weight [virtualenv](https://virtualenv.pypa.io/en/latest/virtualenv.html), others prefer solutions as robust as [Vagrant](http://www.vagrantup.com).

{% method -%}
Python dependencies will be automatically installed when `marrow.mongo` is installed:

* A modern (3.2 or newer) version of the `pymongo` package.
* The `marrow.package` plugin and canonical object loader.
* The `marrow.schema` declarative syntax toolkit.

If you add `marrow.mongo` to the `install_requires` argument of the call to `setup()` in your application's `setup.py` file, `marrow.mongo` will be automatically installed and made available when your own application or library is installed. We recommend using _less than_ version numbers to ensure there are no unintentional side-effects when updating. Use `marrow.mongo<1.2` to get all bugfixes for the current release, and `marrow.mongo<2.0` to get bugfixes and feature updates while ensuring that backwards-incompatible changes are not installed without warning.

There are a few conditional, tag-based dependencies. To utilize these optional tags add them, comma separated, beween square braces. This may require shell escaping or quoting.

{% sample lang="bash" -%}
```bash
pip install 'marrow.mongo[scripting,logger]'
```

{% common -%}
## Package Flags

* **`development`**

  Install additional utilities relating to testing and contribution, including `pytest` and various plugins, static analysis tools, debugger, and enhanced REPL shell.

* **`scripting`**

  Pulls in the [Javascripthon](https://github.com/azazel75/metapensiero.pj) Python to JavaScript _transpiler_ to enable use of native Python function transport to MongoDB. (E.g. for use in map/reduce, stored functions, etc.)

* **`logger`**

  Logging requires knowledge of the local host's timezone, so this pulls in the `tzlocal` package to retrieve this information.

{% endmethod %}


## Development Version

{% method -%}
Development takes place on [GitHub](https://github.com/) in the [marrow.mongo](https://github.com/marrow/mongo/) project. Issue tracking, documentation, and downloads are provided there.

Installing the current development version requires [Git](http://git-scm.com/), a distributed source code management system. If you have Git you can run the following to download and _link_ the development version into your Python runtime.

{% sample lang="bash" -%}
```bash
git clone https://github.com/marrow/mongo.git
(cd mongo; python setup.py develop)
```
{% endmethod %}

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes, and submit a pull request. For more information see the [Contributing](/contributing.md) section, and [GitHub's documentation](http://help.github.com/).
