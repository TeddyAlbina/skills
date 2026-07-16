---
name: create-technical-architecture-document
description: Create, update, tailor, review, and validate living Technical Architecture Documents (TADs) for applications and coherent systems. Use for architecture dossiers, solution/high-level design documents, architecture views, system context and deployment documentation, constraints and non-functional requirements, security/infrastructure/sizing views, ADR linkage, architecture glossaries and Ubiquitous Language, Markdown or AsciiDoc architecture templates, and architecture-document quality reviews.
---

# Create Technical Architecture Document

Produce an evidence-backed, maintainable architecture document that explains why the system is shaped as it is. Connect every material constraint and measurable requirement to the solution, its verification, and any unresolved risk.

## Load the right resources

- Read `references/content-playbook.md` before drafting or materially revising a document.
- Read `references/source-and-customizer-guide.md` when tailoring the upstream Florat template, using the online customizer, publishing a reusable base template, or applying the license.
- Read `references/tooling-and-evidence.md` when discovering an existing codebase, selecting diagrams, rendering AsciiDoc, or exporting PDF/DOCX.
- Inspect `assets/sample-technical-architecture-document.md` when a filled example would clarify expected depth.
- Copy `assets/technical-architecture-document.md` for a comprehensive Markdown document.
- Copy `assets/technical-architecture-document-lean.md` for a small system or an early architecture baseline.
- Copy `assets/upstream-blank-asciidoc/` for the original multi-file AsciiDoc blank template.

## Execute the workflow

### 1. Establish the document contract

Determine the system boundary, audience, lifecycle stage, required output format, depth, and destination. Use these defaults when the user does not specify them:

- Markdown as the source format.
- Comprehensive template for production systems; lean template for prototypes or narrow changes.
- One living document plus linked ADRs, not copied decision histories.
- Current and target state clearly separated.
- Unknown facts marked `TBD` with owner and due date; non-applicable topics marked `N/A` with one-line rationale.

Never invent requirements, topology, controls, capacities, or decisions. Record assumptions explicitly and distinguish observed repository truth from recommendations.

### 2. Discover evidence before writing

Read repository instructions first. Inspect architecture sources in this order:

1. Existing TADs, ADRs, requirements, threat models, runbooks, API/event schemas, deployment manifests, infrastructure-as-code, and CI/CD definitions.
2. Code graph or language-aware symbol tools for components, entry points, dependencies, calls, and runtime boundaries.
3. Configuration and literal search for ports, routes, queues, topics, data stores, identity providers, limits, timeouts, and feature flags.
4. Tests, observability configuration, performance evidence, SLOs, incident notes, and release procedures.
5. Current authoritative external documentation for version-sensitive technologies or standards.

Capture material claims in an evidence ledger with: claim, source, status (`observed`, `stated`, `assumed`, or `proposed`), owner, and verification date. Cite paths, line numbers, manifests, commands, or links in the document where useful.

### 3. Build and test the Ubiquitous Language

Create the glossary early. Derive terms from domain experts, requirements, APIs, events, data models, and user journeys. For each important term, record its precise meaning, context, aliases, forbidden ambiguous synonyms, and owner/status.

Use the same term in prose, diagrams, interfaces, events, schemas, and code-facing names where practical. Flag collisions such as one word with multiple meanings or multiple words for one concept. Treat conversations and reviews with domain experts as tests of the language. Evolve the glossary when the model changes.

### 4. Choose and scaffold the format

Run the local generator for repeatable scaffolding:

```bash
python scripts/create_tad.py --project "Project Name" --owner "Architecture Team" --output docs/technical-architecture.md
```

Use `--profile lean` for the compact Markdown template. Use `--format asciidoc --output docs/architecture` for the upstream multi-file template. The script refuses to overwrite existing output unless `--force` is provided.

For organization-wide template curation, use the Document Template Customizer workflow described in `references/source-and-customizer-guide.md`. Pin the upstream commit in the generated document.

### 5. Write from drivers to solution

Open with purpose, scope, audience, status, system boundary, and executive summary. Then document stakeholders and concerns, business and technical drivers, constraints, assumptions, measurable NFRs, and architectural principles.

For each view, preserve the reasoning chain:

```text
Constraint -> measurable requirement -> architectural decision -> solution element -> verification evidence
```

Cover the five views at a depth appropriate to the system:

- Application: context, actors, capabilities/modules, external systems, information, interfaces, flows, and transition path.
- Development: code/deployable-unit structure, stack, dependencies, patterns, delivery, testing, configuration, logs, and maintainability.
- Infrastructure: environments, compute, network, persistence, middleware, deployment, availability, backup/restore, observability, operations, and decommissioning.
- Security: data classification, trust boundaries, identity, authentication, authorization, secrets, encryption, audit, privacy, threat mitigations, and residual risk.
- Sizing: workloads, growth assumptions, latency/throughput targets, storage, compute, memory, network, capacity model, scaling triggers, and validation method.

Link decisions to ADRs. Summarize the outcome and consequences in the TAD; keep alternatives and decision chronology in the ADR. Keep detailed design, environment inventories, credentials, private addressing, and other sensitive operational data outside the TAD.

### 6. Add decision-useful diagrams

Include diagrams only when they answer a stakeholder question. Prefer text-native Mermaid or PlantUML for versionable living documentation. Label system boundaries, ownership, protocols, trust boundaries, data classification, cardinality, synchronous/asynchronous interaction, and current versus target state.

For a comprehensive document, normally include:

- system context;
- container/module or capability view;
- deployment/runtime view;
- one critical data or control flow;
- security trust boundaries when materially different from deployment boundaries.

Provide a short narrative and a legend. Do not let a diagram become the sole source of a critical fact.

### 7. Review for integrity

Check that:

- every hard constraint is addressed or accepted as a risk;
- every important NFR has a measurable target and verification method;
- every material component appears consistently across prose, diagrams, interfaces, deployment, security, and sizing;
- current state, transition state, and target state are not blended;
- terms match the glossary;
- `TBD`, `TODO`, `WIP`, assumptions, and unresolved points have owners and dates;
- `N/A` sections explain why they do not apply;
- secrets, credentials, private endpoints, and exploitable infrastructure details are absent;
- links and source revisions are valid;
- the document remains concise enough to maintain.

Run the validator:

```bash
python scripts/validate_tad.py docs/technical-architecture.md --profile standard
python scripts/validate_tad.py docs/technical-architecture.md --profile strict --fail-on-warnings
```

Use `--json` for CI integration. Fix errors; evaluate warnings against the document contract rather than deleting useful exceptions.

### 8. Render and hand off

Preview Mermaid/PlantUML and render AsciiDoc before delivery. For PDF or DOCX output, use the dedicated PDF/document capability when available and inspect the rendered pages, tables, diagrams, links, headings, and page breaks.

Report the created artifact, format/profile, evidence inspected, validation result, explicit assumptions, unresolved items, and the command needed to regenerate it.

## Preserve source and license integrity

The bundled upstream AsciiDoc blank template is from Bertrand Florat's `architecture-document-template` and is licensed CC BY-SA 4.0. Keep its `ATTRIBUTION.md` and `LICENSE.md` when copying or redistributing the template. Follow `references/source-and-customizer-guide.md` for the distinction between sharing an adapted template and publishing a project document produced from it.

## Example requests

- "Create a TAD from this repository and deployment manifests."
- "Turn these requirements and ADRs into a five-view architecture document."
- "Review our architecture.md for missing NFRs, security gaps, and inconsistent diagrams."
- "Generate a lean Markdown architecture baseline for this service."
- "Tailor the Florat AsciiDoc template for a small internal API using the customizer labels."
- "Create and normalize the domain glossary as a Ubiquitous Language."
