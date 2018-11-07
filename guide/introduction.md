# Introduction

Documents are the records of [MongoDB](https://www.mongodb.com/), stored in an efficient binary form called [BSON](http://bsonspec.org/), allowing record manipulation that is cosmetically similar to [JSON](http://json.org/). In Python these are typically represented as [dictionaries](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict), Python's native mapping type. Marrow Mongo provides a [`Document`](reference/document.md) mapping type that is directly compatible with and substitutable anywhere PyMongo uses dictionaries.

This package utilizes the [Marrow Schema](https://github.com/marrow/schema#readme) declarative schema toolkit and extends it to encompass MongoDB data storage concerns. Its documentation may assist you in understanding the processes involved in Marrow Mongo. At a fundamental level you define data models by importing classes describing the various components of a collection, such as `Document`, `ObjectId`, or `String`, then compose them into a declarative class model whose attributes describe the data structure, constraints, etc.

`Field` types and `Document` mix-in classes (_traits_) meant for general use are registered using Python standard [_entry points_](http://setuptools.readthedocs.io/en/latest/setuptools.html#extensible-applications-and-frameworks) and are directly importable from the `marrow.mongo.field` and `marrow.mongo.trait` package namespaces respectively.

Within this guide fields are broadly organized into three categories:

* **Simple fields** are fields that hold _scalar values_, variables that can only hold one value at a time. This covers most datatypes you use without thinking: strings, integers, floating point or decimal values, etc.

* **Complex fields** cover most of what's left: variables that can contain multiple values. This includes arrays (`list` in Python, `Array` in JavaScript), compound mappings (_embedded documents_), etc.

* **Complicated fields** are represented by fields with substantial additional logic associated with them, typically through complex typecasting, or by including wrapping objects containing additional functionality. These are separate as they represent substantial additions to core MongoDB capabilities, possibly with additional external dependencies.