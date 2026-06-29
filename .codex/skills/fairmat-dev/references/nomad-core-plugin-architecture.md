# NOMAD Core Architecture for Plugin Development

This note is a practical map of `packages/nomad-FAIR` for developing FAIRmat/NOMAD plugins such as `packages/nomad-auto-xrd`.

It is not a full package inventory. It focuses on the parts that matter when you are extending NOMAD with schemas, parsers, normalizers, apps, and actions.

## The Core Mental Model

NOMAD is built around a few layers that interact in a predictable order:

1. Plugin discovery and configuration
2. Metainfo/schema registration
3. Parsing raw files into an `EntryArchive`
4. Normalizing the archive into richer, standardized data
5. Indexing/storage/API/UI consumption
6. Optional action workflows for user-triggered compute

For plugin work, the most important thing to understand is that NOMAD is both:

- a metainfo/schema system
- a processing platform that turns files into structured archives and derived results

Actions are adjacent to this processing pipeline, but are not the same thing as parsing/normalization.

## 1. Plugin Discovery: Everything Starts from `nomad.plugin`

The new plugin mechanism is centered on Python entry points declared in a package `pyproject.toml`:

```toml
[project.entry-points.'nomad.plugin']
schema = "my_package.schema_packages:schema_entry_point"
parser = "my_package.parsers:parser_entry_point"
my_action = "my_package.actions.foo:action_entry_point"
```

The core implementation is in:

- `packages/nomad-FAIR/nomad/config/models/plugins.py`
- `packages/nomad-FAIR/nomad/config/models/config.py`

Key idea:

- NOMAD does not directly import all plugin code at config import time.
- `config.load_plugins()` discovers installed entry points, applies `nomad.yaml` overrides, instantiates the entry point objects, and stores them under `config.plugins`.
- Entry point objects are Pydantic models such as `SchemaPackageEntryPoint`, `ParserEntryPoint`, `NormalizerEntryPoint`, `AppEntryPoint`, and `ActionEntryPoint`.

Why this matters:

- Your plugin class should keep `load()` lazy.
- Import heavy or circular-prone code inside `load()`, not at module top level.
- This pattern is used correctly in `nomad-auto-xrd`.

## 2. Schema Injection: Metainfo Is the Real Extension Surface

The deepest extension point in NOMAD is the metainfo system.

Relevant modules:

- `packages/nomad-FAIR/nomad/metainfo/`
- `packages/nomad-FAIR/nomad/datamodel/`
- `packages/nomad-FAIR/nomad/datamodel/metainfo/`

Important idea:

- Schemas are Python classes built from `MSection`, `ArchiveSection`, `EntryData`, `Schema`, `Quantity`, `SubSection`, `Category`, etc.
- These definitions are collected into `Package` / `SchemaPackage` objects.
- Plugins inject additional schema packages into the global registry through `SchemaPackageEntryPoint.load()`.

In practice:

- A schema plugin typically exposes an `m_package` and returns it from `load()`.
- Example pattern:
  - `packages/nomad-auto-xrd/src/nomad_auto_xrd/schema_packages/__init__.py`
  - `packages/nomad-FAIR/examples/data/cow_tutorial/nomad-countries/src/nomad_countries/schema_packages/__init__.py`

This is “schema injection” in practice:

- install package
- register entry point
- NOMAD loads the schema package
- the package becomes part of the global metainfo environment
- archives, ELN forms, search quantities, and apps can then refer to those definitions

## 3. How the Global Schema Registry Gets Built

The main entry is:

- `packages/nomad-FAIR/nomad/datamodel/__init__.py`

`all_metainfo_packages()` does several important things:

- calls `config.load_plugins()`
- loads all `SchemaPackageEntryPoint`s
- imports parsers so parser-coupled schemas also get registered
- ensures packages with `m_package` are initialized into `Package.registry`
- builds a combined `Environment` over all loaded packages

This means the schema world is not static. It is assembled at runtime from:

- built-in NOMAD packages
- plugin-provided schema packages
- parser-triggered imports that bring in more schema definitions

Practical consequence:

- If a custom schema is not visible, the first things to check are:
  - Was the plugin installed?
  - Is the `nomad.plugin` entry point declared correctly?
  - Does `load()` actually import and return the `m_package`?
  - Was metainfo initialization triggered in the current process?

## 4. `EntryArchive` Is the Central Runtime Object

The runtime data structure for an entry is `EntryArchive`:

- `packages/nomad-FAIR/nomad/datamodel/datamodel.py`

At a high level an archive contains:

- `metadata`
- `data`
- `run`
- `measurement`
- `workflow` / `workflow2`
- `results`
- `definitions`

For plugin authors, the main parts are usually:

- `archive.data`
  - top-level custom schema/ELN content
- `archive.results`
  - normalized, search-friendly derived content
- `archive.metadata`
  - entry-level metadata used across the platform
- `archive.definitions`
  - inline/custom schema package definitions if the entry itself carries schema definitions

Practical rule:

- Parsers usually populate `archive.data`, domain-specific sections, and metadata.
- Normalizers usually derive or refine `archive.results`, topology, workflow summaries, and search-ready values.

## 5. Parsing: Raw Files Become Structured Archives

Core parser logic lives in:

- `packages/nomad-FAIR/nomad/parsing/parsers.py`
- `packages/nomad-FAIR/nomad/parsing/parser.py`

The parser system works like this:

- NOMAD loads all `ParserEntryPoint`s from plugins.
- Each parser declares matching rules such as:
  - `mainfile_name_re`
  - `mainfile_contents_re`
  - `mainfile_mime_re`
  - binary header checks
  - structured content matching via `mainfile_contents_dict`
- `match_parser()` inspects a candidate file and selects the first matching parser.
- `run_parser()` creates an `EntryArchive`, sets up a context, and calls `parser.parse(...)`.

Important practical details:

- Matching is based on file name, MIME, raw bytes, and sometimes decoded text or structured content.
- Parsers can create child entries.
- Parser plugins are loaded lazily, but their instantiated parser objects are collected into the global parser list.
- Parser names and aliases become part of NOMAD runtime lookup (`parser_dict`).

For plugin development:

- Put file-identification logic in the entry point metadata.
- Put archive-population logic in the parser class.
- Keep parser output structurally correct before worrying about downstream normalization.

## 6. Normalization Has Two Layers

This is one of the most important concepts in NOMAD.

### Layer A: Section-local `normalize()` methods

Core base classes:

- `packages/nomad-FAIR/nomad/datamodel/data.py`
- `packages/nomad-FAIR/nomad/metainfo/metainfo.py`

Many schema sections can define their own:

```python
def normalize(self, archive, logger):
    super().normalize(archive, logger)
    ...
```

This is local, schema-aware normalization. It is used to:

- fill missing derived values
- synchronize related fields
- create helper sections
- attach defaults or inferred metadata

Examples:

- `examples/archive/custom_schema.py`
- many built-in sections under `nomad/datamodel/metainfo/`
- custom sections in plugin packages such as `nomad-auto-xrd`

Key rule:

- Always call `super().normalize(...)`.
- NOMAD relies on cooperative normalization across inheritance chains.

### Layer B: Global normalizer chain

Core modules:

- `packages/nomad-FAIR/nomad/normalizing/__init__.py`
- `packages/nomad-FAIR/nomad/normalizing/normalizer.py`
- `packages/nomad-FAIR/nomad/processing/data.py`

This is the pipeline-level normalization step executed after parsing.

How it works:

- NOMAD builds a global ordered list of normalizers.
- Old-style configured normalizers and new plugin `NormalizerEntryPoint`s both feed this list.
- Each entry is normalized in `Entry.normalizing()`.
- Domain filtering can skip normalizers not relevant to the parser domain.
- After the normalizer chain, `parser.after_normalization(...)` is called.

Built-in normalizers do the heavy derived-data work such as:

- material interpretation
- method extraction
- topology
- symmetry-related summaries
- results population
- OPTIMADE-related normalization

Practical distinction:

- Section `normalize()` is best for schema-local invariants.
- Global normalizers are best for cross-cutting archive-to-results transformations.

For most plugin packages, start with section `normalize()`. Add a full custom normalizer only when you need a pipeline-wide transformation that should run independently of a specific section instance.

## 7. `EntryData` and `Schema` Are the Typical Top-Level Plugin Base Classes

From `nomad/datamodel/data.py`:

- `ArchiveSection` is the base for sections with optional normalization logic.
- `EntryData` is the usual base for top-level entry content.
- `Schema` is commonly used for schema-like top-level custom entry structures.

Useful built-in behavior:

- `EntryData.normalize()` ensures `archive.results` exists.
- It also sets fallback `entry_type` and `entry_name` in common cases.

Practical plugin pattern:

- Define a top-level `Schema` or `EntryData` subclass.
- Compose it from reusable `ArchiveSection` subclasses.
- Use `ELNAnnotation`, browser annotations, references, categories, and plot sections as needed.

This pattern is visible in `nomad-auto-xrd`, where custom schemas combine:

- ELN-oriented input sections
- references to existing NOMAD datamodel sections
- analysis/result sections
- plotting and action integration

## 8. Actions Are a Separate Compute Platform

Core modules:

- `packages/nomad-FAIR/nomad/actions/action.py`
- `packages/nomad-FAIR/nomad/actions/manager.py`
- `packages/nomad-FAIR/nomad/actions/client.py`
- `packages/nomad-FAIR/nomad/actions/shared/constant.py`
- `packages/nomad-FAIR/nomad/actions/workers/`

Actions are not parsers and not normalizers.

They are user-triggered workflows executed through Temporal, with:

- task queues such as `cpu-task-queue`, `gpu-task-queue`, `nomad-internal-workflows-task-queue`
- activities
- workflows
- Mongo persistence for action records
- streaming/logging support

Plugin action model:

- expose an `ActionEntryPoint`
- `load()` returns a `nomad.actions.Action`
- that `Action` bundles:
  - a task queue
  - a workflow class
  - activities
  - optional child workflows / extra task-queue activities

Important practical points:

- Action argument validation is inferred from the type hints of `workflow.run`.
- Temporal payloads use Pydantic conversion.
- Actions are operational workflows, not ingestion-time transformations.

This is exactly the model used in `nomad-auto-xrd` for training and analysis actions.

## 9. How `nomad-auto-xrd` Fits the Architecture

`nomad-auto-xrd` is a good real plugin example because it uses multiple extension surfaces:

- schema package entry point
- app entry point
- example upload entry point
- multiple action entry points

Its schema package shows a common NOMAD plugin pattern:

- define custom archive sections
- reuse built-in NOMAD sections (`Material`, `System`, `PlotSection`, `Analysis`, etc.)
- add ELN annotations for form generation
- use section-local normalization and helper functions to project raw domain data into NOMAD-native structures

Its actions show the separate workflow side:

- workflows/activities are registered through action entry points
- execution happens on Temporal workers, not through the parser/normalizer pipeline

What it does not currently show is a custom parser entry point, but that pattern is present in other plugins such as `nomad-measurements`, `pdi-nomad-plugin`, and tutorial/example packages.

## 10. Practical Rules for Plugin Development

### When to use a schema package

Use a `SchemaPackageEntryPoint` when you need:

- custom archive structure
- ELN forms
- custom sections/quantities/categories
- app/search integration based on your own definitions

### When to use a parser

Use a `ParserEntryPoint` when you need:

- automatic ingestion from raw files
- file matching based on names/content/MIME
- archive population from vendor or experiment output

### When to use section `normalize()`

Use section-local normalization when:

- the logic belongs to a specific schema section
- you are deriving values from neighboring fields
- you need to create/update results in a way tightly coupled to that section

### When to use a global normalizer

Use a `NormalizerEntryPoint` only when:

- the logic is pipeline-wide
- it should run after parsing regardless of where the relevant data came from
- it conceptually belongs beside built-in normalization phases rather than inside one schema section

### When to use an action

Use an `ActionEntryPoint` when:

- the user intentionally starts a workflow
- the work is long-running, asynchronous, or compute-heavy
- you need progress streams, user inputs, artifacts, task queues, or retriable workflows

Do not use actions as a substitute for parsing or normalization.

## 11. Common Failure Modes

### Plugin loads but schema is invisible

Usually one of:

- wrong `nomad.plugin` entry point path
- `load()` does not import/return `m_package`
- package not installed into the current environment
- metainfo registry not initialized in the process

### Parser matches incorrectly or not at all

Usually one of:

- too broad or too narrow `mainfile_*` matching config
- wrong regex assumptions
- unexpected encoding/compression/content structure
- parser alias/name confusion

### Custom normalization does not run

Usually one of:

- method name is wrong
- `super().normalize(...)` was omitted
- relevant section is not actually present in the archive
- logic was placed in a global normalizer when it should have lived on the schema section, or vice versa

### Action registers but cannot execute

Usually one of:

- wrong task queue
- worker not running for that queue
- workflow/activity import issue inside `load()`
- workflow input schema/type mismatch

## 12. Minimal “Correct” Plugin Pattern

For most NOMAD plugins, the safest build order is:

1. Define schema package and verify the metainfo loads.
2. Add or refine top-level `Schema` / `EntryData` sections.
3. Add section-local normalization.
4. Add a parser if the data should ingest automatically.
5. Add an app if the data needs a custom explore/search UI.
6. Add actions only if you need user-triggered compute workflows.

This order matches NOMAD’s architecture and usually avoids overengineering.

## 13. Files Worth Reading First for Future NOMAD Questions

- `packages/nomad-FAIR/nomad/config/models/plugins.py`
- `packages/nomad-FAIR/nomad/config/models/config.py`
- `packages/nomad-FAIR/nomad/datamodel/__init__.py`
- `packages/nomad-FAIR/nomad/datamodel/data.py`
- `packages/nomad-FAIR/nomad/datamodel/datamodel.py`
- `packages/nomad-FAIR/nomad/parsing/parsers.py`
- `packages/nomad-FAIR/nomad/normalizing/__init__.py`
- `packages/nomad-FAIR/nomad/normalizing/normalizer.py`
- `packages/nomad-FAIR/nomad/processing/data.py`
- `packages/nomad-FAIR/nomad/actions/action.py`
- `packages/nomad-FAIR/nomad/actions/manager.py`

## Short Summary

NOMAD’s core package is best understood as a runtime-assembled metainfo platform plus a processing pipeline.

- Schema packages inject new definitions into the global metainfo registry.
- Parsers turn raw files into `EntryArchive`s.
- Section `normalize()` methods enforce local schema semantics.
- Global normalizers derive standardized search/result content across entries.
- Actions are a separate Temporal-based workflow system for user-triggered computation.

For plugin authors, the key design question is always: does this belong in schema definition, parsing, normalization, app configuration, or action workflow?
