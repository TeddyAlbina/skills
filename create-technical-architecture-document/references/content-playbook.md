# Technical Architecture Document Content Playbook

## Contents

1. [Document philosophy](#document-philosophy)
2. [Evidence and certainty](#evidence-and-certainty)
3. [Document spine](#document-spine)
4. [Stakeholders and concerns](#stakeholders-and-concerns)
5. [Constraints, requirements, and solutions](#constraints-requirements-and-solutions)
6. [Non-functional requirement format](#non-functional-requirement-format)
7. [Five architecture views](#five-architecture-views)
8. [Cross-cutting traceability](#cross-cutting-traceability)
9. [Ubiquitous Language](#ubiquitous-language)
10. [Diagrams](#diagrams)
11. [ADRs, risks, and unresolved points](#adrs-risks-and-unresolved-points)
12. [Review rubric](#review-rubric)

## Document philosophy

Treat the TAD as a concise, version-controlled explanation of the architecture for one application or coherent group of modules. Optimize it for decisions, onboarding, review, operations, change impact, and risk management.

Keep it alive:

- Store source next to the system or in a governed architecture repository.
- Prefer text-based formats and diagrams that can be reviewed in diffs.
- Record owner, status, last verification date, source revision, and review cadence.
- Link common organization standards rather than copying them.
- Separate stable architecture from volatile inventories and runbook procedures.
- Use `N/A — reason` for considered but irrelevant topics.
- Use `TBD — owner — due date` for missing facts and `WIP` only for active work.

Avoid turning the TAD into detailed design, a class catalog, an environment inventory, a credentials store, a product requirements document, a complete enterprise architecture repository, or a chronological decision log.

## Evidence and certainty

Build an evidence ledger before drafting material claims.

| Field | Meaning |
|---|---|
| Claim | What the document intends to assert |
| Source | Repository path/line, manifest render, ADR, requirement, interview, dashboard, or authoritative URL |
| Status | `observed`, `stated`, `assumed`, or `proposed` |
| Owner | Person or role accountable for validation |
| Verified | Date or source revision |
| Confidence | High, medium, or low with reason when useful |

Apply these rules:

- Prefer rendered/runtime truth over stale summaries.
- Distinguish current-state observations from target-state proposals.
- Cite exact configuration for ports, replicas, policies, limits, protocols, or topology.
- Verify version-sensitive external facts against current primary documentation.
- Record contradictions; do not silently choose one source.
- Convert unresolved contradictions into owned actions.

## Document spine

Use this order unless stakeholders require another:

1. Document control and status
2. Executive summary
3. Purpose, audience, scope, and system boundary
4. Stakeholders and concerns
5. Business/technical drivers and architecture principles
6. Current state and target-state summary
7. Constraints, assumptions, dependencies, and unresolved points
8. Quality attributes and measurable NFRs
9. Application view
10. Development view
11. Infrastructure view
12. Security view
13. Sizing view
14. Cross-view traceability
15. Decisions/ADRs, risks, transition, and decommissioning
16. Glossary/Ubiquitous Language
17. References and appendices

Use a lean document when a service is small, the lifecycle is early, or the change is narrow. Preserve the same reasoning chain even when sections are merged.

## Stakeholders and concerns

Identify stakeholders by role rather than name when possible. Record the questions the document must answer.

| Stakeholder | Typical concerns |
|---|---|
| Product/business owner | Capabilities, boundaries, dependencies, cost, roadmap, business continuity |
| Domain expert | Correct concepts, rules, terminology, exceptions, lifecycle |
| Solution/application architect | Modularity, integration, data ownership, evolution, decisions |
| Developer/tester | Code structure, contracts, patterns, environments, testability, failure behavior |
| Platform/operations/SRE | Deployment, observability, capacity, recovery, maintenance, ownership |
| Security/privacy | Data classification, trust, identity, access, threats, audit, retention |
| Governance/compliance | Standards, evidence, traceability, exceptions, review status |
| Support | Diagnostics, degraded modes, escalation, operational boundaries |

Use the stakeholder matrix to decide which views and diagrams deserve depth. Do not give every section equal weight.

## Constraints, requirements, and solutions

Preserve three distinct concepts:

- **Constraint:** A hard boundary the project cannot choose away, such as law, budget, deadline, mandated platform, contractual integration, or organization standard.
- **Requirement:** A capability or quality the architecture must achieve within those constraints.
- **Solution:** The selected structure and mechanisms that satisfy the requirement.

For each major topic, record:

| ID | Constraint/driver | Requirement | Decision/solution | Verification | Status |
|---|---|---|---|---|---|
| TR-01 | `<hard boundary>` | `NFR-xx` | `ADR-xx / solution element` | `<test, dashboard, exercise>` | Met/gap/risk |

Reject weak chains such as “must be scalable → use Kubernetes.” State the measurable workload, scaling target, trigger, limit, state-management behavior, and test evidence.

## Non-functional requirement format

Write quality attributes as testable scenarios. Include:

- ID and quality attribute
- business rationale and priority
- source/owner
- stimulus and source of stimulus
- operating environment or failure condition
- affected artifact or operation
- expected response
- quantitative response measure
- verification method and evidence location
- linked decision/solution

Example:

| Field | Value |
|---|---|
| ID | NFR-AV-01 |
| Attribute | Availability |
| Scenario | During normal production operation, loss of one application instance shall not interrupt accepted API requests beyond automatic retries. |
| Measure | Monthly service availability >= 99.9%; no more than 1 failed accepted request per failover exercise. |
| Verification | Quarterly game-day plus SLO dashboard. |
| Linked solution | Minimum two instances across failure domains; readiness gates; idempotency key; retry policy. |

Cover only relevant quality attributes, but explicitly consider:

- availability, resilience, degraded modes, RTO, and RPO;
- latency, throughput, concurrency, capacity, and growth;
- security, privacy, auditability, integrity, and non-repudiation;
- interoperability, compatibility, portability, and versioning;
- maintainability, modifiability, testability, deployability, and operability;
- usability, accessibility, localization, and offline behavior;
- cost, sustainability/ecodesign, and resource efficiency;
- retention, archival, purge, and legal preservation.

## Five architecture views

### Application view

Answer what the system is, what it owns, and how it participates in the wider landscape.

Include as relevant:

- objectives, scope, actors, capabilities, and business context;
- current-state pain points and target state;
- system context and external dependencies;
- modules/services/jobs/user interfaces and ownership;
- information domains, master data, classification, retention, and data ownership;
- APIs, events, files, batches, protocols, semantic contracts, and failure semantics;
- critical end-to-end flows and degraded behavior;
- integration inventory or matrix at a stable level;
- transition states, migrations, coexistence, archival, purge, and decommissioning.

Avoid low-level class or sequence details unless they illustrate a system-specific architectural pattern.

### Development view

Answer how the architecture is realized, evolved, tested, and delivered.

Include as relevant:

- repository and deployable-unit boundaries;
- languages, runtimes, frameworks, and major dependencies with versions/reasons;
- layering, modularity, ports/adapters, event handling, and consistency patterns;
- configuration, secrets injection, feature flags, migrations, and compatibility;
- API/event schema governance and versioning;
- error handling, retries, idempotency, concurrency, sessions, time, and encoding;
- logging conventions, trace propagation, metrics, and diagnostic context;
- build/test/release pipeline, quality gates, artifact provenance, and rollback;
- testing strategy, contract tests, performance tests, resilience tests, and security tests;
- branching/release/versioning policy and dependency lifecycle;
- developer environment differences only where architecturally material.

### Infrastructure view

Answer where and how the system runs and is operated.

Include as relevant:

- production environment topology and failure domains;
- compute/orchestration, network zones, ingress/egress, DNS, certificates, and load balancing;
- databases, caches, queues, object/file storage, service discovery, and external infrastructure services;
- deployable units mapped to runtime units;
- deployment strategy, upgrade sequencing, rollback, and maintenance mode;
- availability mechanisms and dependency ceilings;
- backup scope, retention, restore procedure, RPO/RTO, and restore testing;
- observability stack, golden signals, business monitoring, alerts, and ownership;
- scheduled operations, startup/shutdown ordering, support boundaries, and decommissioning;
- cost and energy/resource optimization.

Do not include credentials, public exploit paths, private addresses, or volatile host inventories.

### Security view

Answer what is protected, from whom, at which boundaries, and with what evidence.

Include as relevant:

- assets, data classification, privacy categories, retention, residency, and legal basis;
- trust boundaries and threat actors;
- identity sources and lifecycle;
- user/service authentication, authorization model, least privilege, and segregation of duties;
- service accounts/workload identities and secret/key/certificate lifecycle;
- encryption in transit/at rest and key ownership;
- input validation, integrity, anti-replay/idempotency, and non-repudiation;
- audit events, access to audit data, retention, tamper resistance, and time synchronization;
- supply-chain controls, dependency/image scanning, signing, and provenance;
- prevention, detection, response, and recovery controls;
- privacy operations, deletion/export, masking, and non-production data handling;
- abuse cases, threat mitigations, accepted residual risks, and validation evidence.

Link to a full threat model rather than reproducing it when one exists.

### Sizing view

Answer the workload envelope, resource model, limits, and scaling evidence.

Include as relevant:

- baseline, peak, burst, seasonal, and growth workloads;
- transaction/event sizes and frequency;
- user concurrency and request mix;
- latency/throughput targets by critical operation;
- storage volume, growth, retention, indexes, replicas, backups, and compression;
- compute, memory, connection, thread, queue, and network budgets;
- dependency quotas and rate limits;
- horizontal/vertical scaling behavior, triggers, minimums, maximums, and cooldowns;
- stateful bottlenecks and the capacity ceiling;
- load-test method, dataset, environment fidelity, results, headroom, and next test date;
- cost/capacity trade-offs and forecast uncertainty.

Show calculations and units. Label estimates and confidence. Do not present untested vendor defaults as proven capacity.

## Cross-cutting traceability

Create a compact traceability matrix for material concerns:

| Driver/constraint | NFR | Decision/ADR | Components/views | Verification | Gap/risk |
|---|---|---|---|---|---|

Use stable IDs such as `CON-`, `NFR-`, `ADR-`, `RISK-`, and `TBD-`. Keep IDs meaningful only enough for navigation; do not encode volatile hierarchy into them.

Perform cross-view consistency checks:

- Every deployed unit maps to an application/development component.
- Every external interface appears in security/trust analysis and capacity limits when material.
- Every data store has ownership, classification, backup/retention, and sizing.
- Every availability claim accounts for dependency availability and state.
- Every scaling rule has load evidence and hard ceilings.
- Every target-state component has a transition/decommissioning implication.

## Ubiquitous Language

Follow the core idea summarized by Martin Fowler from Eric Evans: build a common, rigorous language between domain experts and developers; base it on the domain model; use it pervasively in conversation; test it with domain experts; and evolve it with understanding.

Use this glossary schema:

| Term | Precise meaning | Context | Allowed aliases | Avoid | Example | Owner/status |
|---|---|---|---|---|---|---|

Apply these tests:

1. Ask a domain expert and developer to explain a critical flow using the glossary.
2. Note terms that feel awkward, ambiguous, overloaded, or absent.
3. Compare prose with API names, events, schemas, UI labels, and code concepts.
4. Split meanings by bounded context when one word legitimately means different things.
5. Promote unresolved terms to “under discussion,” with owner and resolution date.
6. Update the document and model together after resolution.

Prefer a precise domain term over vague words such as `service`, `object`, `record`, `process`, or `status` without a qualifier.

## Diagrams

Give every diagram:

- a question/purpose;
- title, scope, and current/target-state label;
- legend and notation;
- named boundaries and owners;
- labeled interactions/protocols;
- short prose explaining the important reading;
- source in version control.

Recommended mapping:

| Question | Diagram |
|---|---|
| Who uses the system and what surrounds it? | System context |
| What are the major deployable or logical parts? | Container/module/capability |
| Where do parts run and fail? | Deployment/runtime |
| How does a critical outcome happen? | Data/control-flow or sequence |
| Where does trust change? | Trust-boundary/data-flow |
| How will current state become target state? | Transition roadmap/state diagram |

Avoid unlabeled arrows, mixed abstraction levels, unexplained colors, screenshots of editable diagrams, and diagrams that contradict text.

## ADRs, risks, and unresolved points

Use ADRs for decisions with alternatives and consequences. In the TAD, link the ADR and summarize only the selected outcome, architectural impact, and status.

Use a risk register:

| ID | Risk | Cause | Impact | Likelihood | Mitigation | Trigger/indicator | Owner | Status |
|---|---|---|---|---|---|---|---|---|

Use an unresolved-point register:

| ID | Question/assumption | Why it matters | Evidence needed | Owner | Due | Blocking? |
|---|---|---|---|---|---|---|

Keep unresolved points exceptional. If most architecture is unresolved, label the document as an exploration or draft rather than presenting it as an approved target architecture.

## Review rubric

Score each category from 0 to 2 (`0` absent/incorrect, `1` partial, `2` complete/evidenced):

| Category | 0–2 review question |
|---|---|
| Scope and audience | Can a reader identify system boundary, lifecycle state, owners, and intended decisions? |
| Evidence | Are material claims sourced and current/target/assumed states distinguished? |
| Language | Are domain terms precise, consistent, owned, and tested? |
| Drivers and constraints | Are the forces shaping the architecture explicit? |
| NFRs | Are important qualities measurable and verifiable? |
| Application | Are actors, modules, data, dependencies, and flows coherent? |
| Development | Are realization, delivery, testing, and evolution clear? |
| Infrastructure | Are runtime, failure, operations, recovery, and ownership clear? |
| Security | Are assets, boundaries, identities, controls, evidence, and residual risk clear? |
| Sizing | Are workload, calculations, limits, scaling, and validation evidence credible? |
| Decisions and traceability | Can drivers be traced to decisions, solution elements, and tests? |
| Diagrams | Do diagrams answer questions and agree with the prose? |
| Maintainability | Is the document concise, linked, versioned, and free of volatile/sensitive detail? |

Treat a score below 18/26 as a draft requiring material work. Require no zero in security, scope, evidence, or NFRs before approval for a production-critical system.
