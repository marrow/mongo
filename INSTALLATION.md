# Installation

#### Requirements

* Python 2.7 and above, or Python 3.2 and above; or compatible, such as Pypy or Pypy3.
* An accessible MongoDB installation.

Installation is easy, just execute the following:

{% label %}Terminal{% endlabel %}
```bash
pip install marrow.mongo
```

> #### info::Installation Isolation
> 
> We _strongly_ recommend always using a container, virtualization, or sandboxing environment of some kind when developing using Python; installing things system-wide is yucky \(for a variety of reasons\) nine times out of ten.
> 
> We prefer light-weight [virtualenv](https://virtualenv.pypa.io/en/latest/virtualenv.html), others prefer solutions as robust as [Vagrant](http://www.vagrantup.com).

## Dependency Management

If you add `marrow.mongo` to the `install_requires` argument of the call to `setup()` in your application's `setup.py` file, `marrow.mongo` will be automatically installed and made available when your own application or library is installed. We recommend using "less than" version numbers to ensure there are no unintentional side-effects when updating. Use `marrow.mongo<1.2` to get all bugfixes for the current release, and `marrow.mongo<2.0` to get bugfixes and feature updates while ensuring that large breaking changes are not installed.

Python dependencies will be automatically installed when `marrow.mongo` is installed:

* A modern \(3.2 or newer\) version of the `pymongo` package.
* The `marrow.package` plugin and canonical object loader.
* The `marrow.schema` declarative syntax toolkit.

There are a few conditional, tag-based dependencies:

| Tag | Purpose |
| --- | --- |
| `development` | Install additional utilities relating to testing and contribution, including `pytest` and various plugins, static analysis tools, debugger, and enhanced REPL shell. |
| `scripting` | Pulls in the [Javascripthon](https://github.com/azazel75/metapensiero.pj) Python to JavaScript transpiler to enable use of native Python function transport to MongoDB. (E.g. for use in map/reduce, stored functions, etc.) |
| `logger` | Logging requires knowledge of the local host's timezone, so this pulls in the \`tzlocal\` package to retrieve this information. |

To utilize optional tags, add them, comma separated, beween square braces; this may require shell escaping or quoting.

{% label %}Terminal{% endlabel %}
```bash
pip install 'marrow.mongo[scripting,logger]'
```

## Development Version

Development takes place on [GitHub](https://github.com/) in the [marrow.mongo](https://github.com/marrow/mongo/) project. Issue tracking, documentation, and downloads are provided there.

Installing the current development version requires [Git](http://git-scm.com/), a distributed source code management system. If you have Git you can run the following to download and _link_ the development version into your Python runtime::

{% label %}Terminal{% endlabel %}
```bash
git clone https://github.com/marrow/mongo.git
(cd mongo; python setup.py develop)
```

You can then upgrade to the latest version at any time::

{% label %}Terminal{% endlabel %}
```bash
(cd mongo; git pull; python setup.py develop)
```

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes, and submit a pull request. For more information see the [Contributing](/CONTRIBUTING.md) section, and [GitHub's documentation](http://help.github.com/).