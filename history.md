# Version History

**Latest:** [![version](https://img.shields.io/pypi/v/marrow.mongo.svg?style=flat "Latest version.")](https://pypi.python.org/pypi/marrow.mongo)
[![tag](https://img.shields.io/github/tag/marrow/mongo.svg "Latest tag.")](https://github.com/marrow/mongo/releases/latest)  

<!-- timeline -->

## [_Refinement Release_](https://github.com/marrow/mongo/releases/tag/1.1.1) 1.1.1

** ** `2017-05-17`

__Please note that due to Pypi stupidity, version `1.1.1.1` there is actually `1.1.1`.__

New or updated in this release:

* Removal of diagnostic information and updated testing/commit configurations, improving commit performance and bumping Pypy3 versions.
* Correction of ABC participation (and missing shallow copy method) for Pypy use of query fragments.  [#32](https://github.com/marrow/mongo/issues/32)
* Corrected `$regex` generation.
* Collation support.
* Passing an existing document (with `_id` key) to an `ObjectId` field will utilize the ID provided therein.  [#20](https://github.com/marrow/mongo/issues/20)
* Enhanced `String` field capabilities to include stripping and case conversion.  [#33](https://github.com/marrow/mongo/issues/33)
* Shared `utcnow` helper function.
* Improved documentation coverage.
* Improved generalized programers' representations.
* Improved query fragment merging.
* Corrected Reference field behaviours.
* Dead code removal.
* Updated `Array` and `Embed` field default value handling to reduce boilerplate.

**Potentially backwards-incompatible changes:**

* Simplification to only support a single referenced kind in complex fields such as `Array` and `Embed`.  As multi-kind support was not fully implemented, this should not disrupt much.

New fields, including:

* `Decimal` — [#23](https://github.com/marrow/mongo/issues/23)
* `Period` — Storage of dates rounded (floor) to their nearest period.
* `Markdown` — Rich storage of Markdown textual content.  [#34](https://github.com/marrow/mongo/issues/34)
* `Path` — Store a PurePosixPath as a string.  [#35](https://github.com/marrow/mongo/issues/35)

Traits are new, see #26, including:

* `Collection` — Isolating collection management semantics from the core `Document` class.
* `Derived` — Isolating subclass management and loading from the core `Document` class.
* `Expires` — Automated inclusion of `TTL` (time-to-live) field and index definitions, including expiry check on load.
* `Identified` — Isolation of primary key management from core `Document` class.
* `Localized` — Management of contained localizable top-level document content.
* `Published` — Management of publication/retraction and dedicated creation/modification times.
* `Queryable` — Encapsulation of collection-level record management.  (**Not** an Active Record pattern.)

<!-- /timeline -->

<!-- timeline -->

## [_Feature Release_](https://github.com/marrow/mongo/releases/tag/1.1.0) 1.1.0

** ** `2016-11-27`

- Add Landscape.io integration.
- Improve overall code health. [#14](https://github.com/marrow/mongo/issues/14)
- Added missing project metadata.
- Updated installation documentation. 81e7702
- Remove dependency on `pytz`. 815a74a
- Removed our own `compat` module; schema already has a sufficient one.
- Allow for `Reference` fields to cache data they reference. [#8](https://github.com/marrow/mongo/issues/8)
- `Array` & `Embed` dereferencing + `Alias` pseudo-field support. [#12](https://github.com/marrow/mongo/issues/12)
  - Ability to dereference `Array` and `Embed` subfield values when querying through class attribute access.
  - Added `Alias` pseudo-field to allow the creation of shortcuts for value retrieval and assignment (via instance attribute access) and querying (through class attribute access).
  - `Array` and `Embed` now persist their typecasting within `__data__`, to preserve changes to nested values. (This is generally safe, however do not utilize `PluginReference` as an embeddable kind.)
- Allow for fields to be combined, not just query documents. [#11](https://github.com/marrow/mongo/issues/11)
  - Field references (`Q` instances generated through class-based attribute access of fields) may now be combined to save time in queries involving multiple fields being compared against the same value.
- Parameterized filter, sort, projection and updates. [#4](https://github.com/marrow/mongo/issues/4)
  - Addition of `~` inversion / `$not` support on `Ops`.
  - Split `Ops` types.
  - Ensure Document uses `odict`.
- GeoJSON and geographic querying support. [#6](https://github.com/marrow/mongo/issues/6)
  - Added Document types:
    - `GeoJSON`
    - `GeoJSONCoord`
    - `Point`
    - `LineString`
    - `Polygon`
    - `MultiPoint`
    - `MultiLineString`
    - `MultiPolygon`
    - `GeometryCollection`
  - Added field query operators:
    - `near`
    - `intersects`
    - `within`
  - Added parametric filter operators:
    - `near`
    - `within`
    - `within_box`
    - `within_polygon`
    - `within_center`
    - `within_sphere`
    - `intersects`
- Ability to perform certain collection-level operations. [#17](https://github.com/marrow/mongo/issues/17)
  - Added Document class methods:
    - `create_collection`
    - `get_collection`
    - `create_indexes`
  - Added the following Document class attributes to control collection settings:
    - `__collection__` - the name of the collection to use
    - `__read_preference__` - default ReadPreference
    - `__read_concern__` - default ReadConcern
    - `__write_concern__` - default WriteConcern
    - `__capped__` - the size, in bytes, to allocate as a capped collection
    - `__capped_count__` - additionally limit the number of records
    - `__engine__` - override storage engine options
    - `__validate__` - one of 'off' (the default), 'strict', or 'moderate'.


<!-- /timeline -->

<!-- timeline -->

## [_Initial Release_](https://github.com/marrow/mongo/releases/tag/1.0.0) 1.0.0

** ** `2016-11-21`

* Initial release of basic field mapping functionality.

<!-- /timeline -->
