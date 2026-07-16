# Source, Customizer, and License Guide

## Contents

1. [Source baseline](#source-baseline)
2. [What the upstream template contributes](#what-the-upstream-template-contributes)
3. [Blank-template workflow](#blank-template-workflow)
4. [Document Template Customizer](#document-template-customizer)
5. [Create a compatible base template](#create-a-compatible-base-template)
6. [Filtering behavior](#filtering-behavior)
7. [Customizer operating procedure](#customizer-operating-procedure)
8. [License and attribution](#license-and-attribution)

## Source baseline

This skill was synthesized from the following primary sources on 2026-07-16:

- Bertrand Florat, Architecture Document Template: https://github.com/bflorat/architecture-document-template
  - inspected commit: `c1787cdf061bdb9280116fa619e64879b01cbbcf`
- Upstream blank template: https://github.com/bflorat/architecture-document-template/tree/master/blank-template
- Base-template manifest: https://github.com/bflorat/architecture-document-template/blob/master/base-template-manifest.yaml
- Document Template Customizer: https://github.com/bflorat/document-template-customizer
  - inspected commit: `f4bd042b6075c632d39f0696b1cd3ecafad20bb6`
  - hosted application: https://document-template-customizer.florat.net/
- Martin Fowler, “Ubiquitous Language”: https://martinfowler.com/bliki/UbiquitousLanguage.html

The user-provided customizer URL preloads the French `bflorat/modele-da` base. Use this English direct link when targeting `architecture-document-template`:

https://document-template-customizer.florat.net/?base_template_url=https%3A%2F%2Fraw.githubusercontent.com%2Fbflorat%2Farchitecture-document-template%2Frefs%2Fheads%2Fmaster%2F

Treat branch URLs as mutable. For an auditable architecture document, record the exact template commit used.

## What the upstream template contributes

The upstream model organizes a project/application architecture into five largely self-supporting views aligned with common stakeholder concerns:

1. Application
2. Development
3. Sizing
4. Infrastructure
5. Security

Within each subject, it distinguishes:

1. constraints that apply to the project;
2. requirements, especially NFRs, expressed within those constraints;
3. the chosen solution that responds to the requirements.

It also contributes these practices:

- Maintain the architecture as text in version control.
- Keep explanations and examples beside a blank model while authoring.
- Mark inapplicable chapters `N/A`, not silently blank.
- Mark unfinished content `TODO` or `WIP`.
- Keep assumptions and points under study explicit and exceptional.
- Move specialist detail to appendices or linked documents.
- Link ADRs rather than embedding the full decision study.
- Avoid credentials, private addressing, and sensitive physical details.
- Identify the template commit at the beginning of the document.
- Maintain a glossary supporting the Ubiquitous Language.

The comprehensive explanatory source is intentionally large. Tailor it to the project rather than filling sections mechanically.

## Blank-template workflow

The upstream repository recommends opening the explanatory template and blank template side by side. The blank template preserves the headings and prompts without the instructional prose.

Use the bundled copy at `assets/upstream-blank-asciidoc/` when an offline multi-file AsciiDoc baseline is needed. It contains:

- `README.adoc`
- `view-application.adoc`
- `view-development.adoc`
- `view-infrastructure.adoc`
- `view-security.adoc`
- `view-sizing.adoc`
- `glossary.adoc`
- `export`
- `resources/views.png`
- `ATTRIBUTION.md` and `LICENSE.md`

Run `scripts/create_tad.py --format asciidoc` to copy and initialize it. Preserve attribution when redistributing the template.

The upstream `export` helper requires a Linux-like shell and Docker. It packages AsciiDoc sources or converts them through containerized Asciidoctor, wkhtmltopdf, and Pandoc. Inspect and adapt it before CI use because it writes under `/tmp`, assumes a `diagrams` directory, and invokes external container images.

## Document Template Customizer

The customizer is a static browser application. According to its project documentation, base-template loading, filtering, and ZIP generation happen in the browser; the hosted server does not process uploaded document content. Still assess browser, network-origin, and internal-content policy before pointing it at a private base URL.

It supports:

- a base-template URL, normally a raw repository root ending in `/`;
- label selection, including multi-valued labels;
- explicit section-drop rules;
- optional anchor preservation;
- blank-only, explanatory-template-only, or both output modes;
- preview and copy;
- generated `customization-context.yaml` for repeatable filtering;
- reload of a prior customization context;
- ZIP output containing `template/` and/or `blank-template/`.

The intended governance flow is:

1. An enterprise architect maintains an organization-wide base template.
2. A senior solution architect curates a smaller template for a class of projects.
3. A project architect fills the generated blank document while consulting the filtered explanatory template.

## Create a compatible base template

Provide `README.adoc` and `base-template-manifest.yaml` at the raw base URL root. The parts must be AsciiDoc-compatible text; section headings may use AsciiDoc `=` or Markdown `#` forms.

Example manifest:

```yaml
author: Architecture Team
license: CC BY-SA 4.0
language: en
parts:
  - name: Application view
    file: view-application.adoc
  - name: Development view
    file: view-development.adoc
  - name: Infrastructure view
    file: view-infrastructure.adoc
  - name: Security view
    file: view-security.adoc
  - name: Sizing view
    file: view-sizing.adoc
multi_values_labels:
  - name: level
    available_values: [basic, intermediate, advanced]
  - name: project_size
    available_values: [small, medium, large]
  - name: detail_level
    available_values: [overview, detailed, in-depth]
files_imported_into_blank_templates:
  - src_dir: blank-template
    dest_dir: .
    files: [README.adoc, glossary.adoc, export]
files_imported_into_templates:
  - src_dir: .
    dest_dir: .
    files: [LICENSE.md]
```

Check the customizer release in use for the exact manifest property names. The inspected customizer documentation uses `files_imported_into_blank_templates` and `files_imported_into_templates`; its internal model also normalizes those imports before generation.

Annotate filterable sections with a single-line JSON comment immediately above the heading, with no intervening blank line:

```asciidoc
//🏷{"id":"nfr-availability","labels":["level::intermediate","project_size::medium","availability"],"link_to":["solution-availability"]}
== Availability requirements
```

Metadata fields:

- `id`: unique, space-free anchor identifier; use conservative ASCII.
- `labels`: simple labels or `name::value` multi-valued labels.
- `link_to`: target section ID or array of IDs; the customizer inserts localized “See also” links.

To retain explanatory content in the generated blank form, wrap it in a pre-filled block:

```asciidoc
[PRE-FILLED]
====
This organization-wide principle remains in every generated blank document.
====
```

Use pre-filled blocks sparingly for mandated principles, fixed organization context, or approved boilerplate.

## Filtering behavior

The inspected customizer documents these matching rules:

- Selecting all labels or no labels returns the full base template.
- Level-one sections are always retained.
- Dropping a parent drops all descendants.
- Keeping a parent still evaluates labeled child sections individually.
- A section is dropped when one of its labels is unselected or its parent is dropped.
- An unlabeled section is kept when its parent is kept.

Test label combinations before publishing a base template. A label taxonomy is part of the template contract; changing it can silently alter generated outputs.

## Customizer operating procedure

1. Open the hosted customizer or an approved on-premises deployment.
2. Paste the raw base-template root URL, or use a preloaded query URL.
3. Load the base and confirm its duration/status.
4. Select project size, expertise level, detail level, and concern labels.
5. Add explicit drop rules only for sections that cannot be excluded cleanly by taxonomy.
6. Preserve anchors when cross-section navigation matters.
7. Preview every retained part in blank and explanatory modes.
8. Generate both outputs for authoring: `template/` as guidance and `blank-template/` as the deliverable source.
9. Preserve `customization-context.yaml` with the document source.
10. Record base URL, exact source commit, label set, dropped sections, and generation date in document control.
11. Review the generated blank document for broken links, orphan headings, missing static resources, and inappropriate pre-filled content.

For sensitive internal templates, prefer an approved on-premises build. The customizer repository documents downloadable releases and an NGINX-based container option.

## License and attribution

The upstream architecture template is licensed under Creative Commons Attribution-ShareAlike 4.0 International. The upstream project states that a shared adapted template must retain:

- creator attribution to Bertrand Florat;
- a link to https://creativecommons.org/licenses/by-sa/4.0/;
- a disclaimer and link to https://github.com/bflorat/architecture-document-template;
- an indication of modifications where applicable;
- ShareAlike terms for the adapted template.

The bundled upstream copy includes the license and attribution notice. Do not remove them when copying or sharing the template.

The upstream project also states that architecture documents resulting from the template do not have to use CC BY-SA 4.0, although it recommends linking back to the template. This is a statement from the source project, not legal advice. Distinguish the reusable template artifact from a project-specific document produced with it, and consult the organization's legal policy when redistribution or derivative-template licensing is material.

The Document Template Customizer application itself is published under AGPLv3 according to its hosted UI/repository. That application license is separate from the content license of the base template and the project document generated from it.
