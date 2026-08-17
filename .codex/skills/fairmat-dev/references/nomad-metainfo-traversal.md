# NOMAD Metainfo Traversal

## Section traversal

Traverse serialized NOMAD data by metainfo section boundaries:

- `section_def.all_quantities` defines opaque leaf values
- `section_def.all_sub_sections` defines the only recursive branches

This means:

- scalar quantities stay scalar
- array quantities stay arrays
- JSON quantities stay dict/list payloads
- nested lists inside quantities are not flattened

Do not infer recursion rules from raw serialized shape alone.

## Root archive rule

For serialized exported entries:

- top-level `archive` starts from `EntryArchive.m_def`
- recurse with the subsection's declared section definition unless the serialized child carries a more specific `m_def`
- plugin-defined schema variation is expected mainly below `archive.data`

## Section-definition lookup

Prefer the loaded metainfo registry:

```python
from nomad.metainfo import Package, Section

def resolve_section_def(m_def: str) -> Section | None:
    package_name, section_name = m_def.rsplit(".", 1)
    package = Package.registry.get(package_name)
    if package is None:
        return None
    definition = package.all_definitions.get(section_name)
    return definition if isinstance(definition, Section) else None
```

Notes:

- `Package.registry` only knows packages already loaded in the current NOMAD process
- avoid forcing heavy plugin loading from lightweight utility code unless the task explicitly needs it

## DataFrame construction

Recommended pattern:

1. Build one row dict per exported entry.
2. Flatten schema-governed sections by metainfo property boundaries.
3. Preserve quantity values intact in the row dict.
4. Convert the row dicts to a DataFrame.
5. Only then adapt columns for Arrow or Parquet if required.

## Arrow and Parquet failure modes

Common failures:

- mixed Python object columns that Arrow cannot cast to one type
- empty dict columns inferred as `struct<>`
- nested types that contain an empty struct somewhere below the top-level type

Recommended handling:

- stringify object columns that Arrow cannot encode consistently
- drop columns whose non-null values are all empty dicts if that data is not useful
- recursively inspect inferred Arrow types for `struct<>` before Parquet writing

## Caching

For repeated `m_def` resolution inside one process, `functools.lru_cache` is fine.

Guidelines:

- keep it process-local in your reasoning
- do not assume reuse across Temporal child workflows or different worker processes
- use `cache_info()` during debugging to inspect hits, misses, and current size

## Design preference

Keep the flattening logic semantically correct first:

- quantities opaque
- subsections recursive

Then isolate unavoidable storage-format compromises at the output boundary instead of
polluting the traversal logic with file-format concerns.
