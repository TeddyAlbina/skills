---
id: master-skill-registry-protocol
name: master-skill-registry-protocol
type: orchestrator_routing_map
version: 1.5.0
status: active
last_updated: 2026-06-24
description: Primary routing engine and boundaries for lazy-loading granular domain capabilities. Prevents context bloat by acting as an autonomous file-fetching map.
capabilities:
  - autonomous_routing
  - context_lazy_loading
  - boundary_enforcement
  - dynamic_dependency_resolution
  - skill_discovery

tags:
  - architecture
  - router
  - core-system
  - orchestrator
  - lazy-loading
  - context-boundary
  - .net
  - .net-10
  - csharp
  - modern-csharp
  - msbuild
  - nuget
  - central-package-management
  - aspire
  - blazor
  - mudblazor
  - wpf
  - winui3
  - razor-pages
  - native-aot
  - webassembly
  - benchmarkdotnet
  - microbenchmarking
  - rust
  - cargo
  - unsafe-rust
  - lsp-analysis
  - go
  - golang
  - wire
  - samber
  - viper
  - cobra
  - slog
  - pprof
  - zig
  - raylib
  - sdl3
  - clickhouse
  - chdb
  - cockroachdb
  - molt
  - postgresql
  - cloudnativepg
  - kubernetes
  - k8s
  - firecracker
  - microvm
  - jailer
  - argocd
  - gitops
  - kyverno
  - velero
  - ceph
  - nats
  - prometheus
  - alertmanager
  - victoriametrics
  - victorialogs
  - victoriatraces
  - promql
  - metricsql
  - logsql
  - opentelemetry
  - vllm
  - llm-inference
  - mcp
  - model-context-protocol
  - microsoft-foundry
  - agent-framework
  - multi-agent
  - security
  - access-control
  - encryption
  - cmek
  - tls-certificates
  - hipaa-compliance
  - gdpr-compliance
  - audit-logging
  - testing
  - xunit
  - mstest
  - tunit
  - bunit
  - testcontainers
  - integration-testing
  - performance-optimization
  - diagnostics
  - telemetry
  - static-analysis
  - knowledge-graph
  - tailwind-css
  - web-development
  - fintech
  - payment-gateways
  - inflowpay
  - kotlin
  - jpa
  - agp9
  - cocoapods
  - spm-migration
  - spm-migration
  - kotlin-tooling-java-to-kotlin
  - microsoft-docs
  - microsoft-learn
  - microsoft-learn-mcp
  - microsoft-skill-creator

---

# MASTER SKILL REGISTRY & PROTOCOL

## CONTEXT LOADING & SKILL REGISTRY PROTOCOL

You operate under a strict "Lazy-Loading" context model to minimize token bloat. You have access to a **Master Skill Registry** that indexes granular, specialized `.md` capability files.

---

## FILE SYSTEM ACCESS BOUNDARIES

You are strictly prohibited from parsing, searching, or reading individual capability files (any files ending in `*.md` inside subdirectories or located in the `/skills/` directory) during initialization or general conversation *unless* explicitly matched via the routing table below.

1. **Primary Entry Point:** You may *only* read and load this file (`SKILL.md`) into your active context during initialization.
2. **Context Laziness:** Treat all individual skill files as "cold storage." Do not pre-load them.
3. **Deterministic Routing:** Use this file purely as an autonomous routing map. Match the user's request to one or more lines in the registry table, and then immediately invoke your file-fetching/reading tool on the corresponding path. Do not ask the user for permission or input; execute the file fetch automatically.

---

## EXECUTION & DIRECT ROUTING RULES

### 1. Operational Rules

- **No Hallucination/Guessing:** If a task requires deep technical execution, syntax, or architectural constraints managed by a specific subsystem, do NOT attempt to infer or guess the details if they are missing from the current context.

- **Identify and Fetch:** Scan the incoming prompt against the Master Skill Registry table below. If a matching specialized skill file exists, you must immediately call your file-reading tool with the specified path before generating any technical response.

### 2. Tool Execution Protocol

When a matching skill is identified:

1. Locate the exact relative path in the `Reference` column.
2. Immediately call your designated file retrieval tool using that path.
3. Once the file content is retrieved, absorb its deep domain rules into your active memory loop and execute the original task seamlessly.

---

## MASTER SKILL REGISTRY

| Skill | Reference | When to Use |
|---|---|---|
| alertmanager-query | [alertmanager-query.md](references/alertmanager-query/alertmanager-query.md) | Query AlertManager via curl v2 API for listing alerts, managing silences, checking alert state |
| analyzing-dotnet-performance | [SKILL.md](references/dotnet-diag/skills/analyzing-dotnet-performance/SKILL.md) | Scan .NET code for ~50 performance anti-patterns across async, memory, strings, collections, LINQ, regex, serialization, and I/O |
| analyzing-range-distribution | [analyzing-range-distribution.md](references/analyzing-range-distribution/analyzing-range-distribution.md) | Analyze CockroachDB range distribution across tables/indexes to identify hotspots, fragmentation, or uneven data distribution |
| analyzing-schema-change-storage-risk | [analyzing-schema-change-storage-risk.md](references/analyzing-schema-change-storage-risk/analyzing-schema-change-storage-risk.md) | Estimate storage requirements for CockroachDB schema change backfills to avoid disk exhaustion |
| android-tombstone-symbolication | [SKILL.md](references/dotnet-diag/skills/android-tombstone-symbolication/SKILL.md) | Symbolicate .NET runtime frames in an Android tombstone file |
| argocd | [argocd.md](references/argocd/argocd.md) | Automate GitOps via ArgoCD API and CLI for managing Applications, ApplicationSets, Projects, Repositories, and Clusters |
| aspire-configuration | [aspire-configuration.md](references/aspire-configuration/aspire-configuration.md) | Configure Aspire AppHost to emit explicit app config via environment variables while keeping app code free of Aspire clients |
| aspire-integration-testing | [aspire-integration-testing.md](references/aspire-integration-testing/aspire-integration-testing.md) | Write integration tests using .NET Aspire's testing facilities with xUnit for distributed apps with real dependencies |
| aspire-service-defaults | [aspire-service-defaults.md](references/aspire-service-defaults/aspire-service-defaults.md) | Create a shared ServiceDefaults project for Aspire apps centralizing OpenTelemetry, health checks, resilience, and service discovery |
| auditing-cloud-cluster-security | [auditing-cloud-cluster-security.md](references/auditing-cloud-cluster-security/auditing-cloud-cluster-security.md) | Audit security posture of a CockroachDB cluster across network, auth, authorization, encryption, audit logging, and backup |
| auditing-table-statistics | [auditing-table-statistics.md](references/auditing-table-statistics/auditing-table-statistics.md) | Audit optimizer table statistics for staleness and missing coverage to diagnose poor query performance |
| benchmarking-transaction-patterns | [benchmarking-transaction-patterns.md](references/benchmarking-transaction-patterns/benchmarking-transaction-patterns.md) | Benchmark and compare explicit multi-statement vs single-statement CTE transactions in CockroachDB under contention |
| binlog-failure-analysis | [SKILL.md](references/dotnet-msbuild/skills/binlog-failure-analysis/SKILL.md) | Analyze MSBuild binary logs to diagnose build failures by replaying binlogs to searchable text logs |
| binlog-generation | [SKILL.md](references/dotnet-msbuild/skills/binlog-generation/SKILL.md) | Generate MSBuild binary logs for build diagnostics and analysis |
| build-parallelism | [SKILL.md](references/dotnet-msbuild/skills/build-parallelism/SKILL.md) | Optimize MSBuild build parallelism and multi-project scheduling |
| build-perf-baseline | [SKILL.md](references/dotnet-msbuild/skills/build-perf-baseline/SKILL.md) | Establish build performance baselines and apply systematic optimization techniques |
| build-perf-diagnostics | [SKILL.md](references/dotnet-msbuild/skills/build-perf-diagnostics/SKILL.md) | Diagnose MSBuild build performance bottlenecks using binary log analysis |
| cepth | [cepth.md](references/cepth/cepth.md) | Design, configure, debug, and integrate Ceph distributed storage clusters for Kubernetes, OpenStack, and bare-metal |
| chdb-datastore | [chdb-datastore.md](references/chdb-datastore/chdb-datastore.md) | Drop-in pandas replacement with ClickHouse performance for analyzing data with pandas-style syntax on large datasets |
| chdb-sql | [chdb-sql.md](references/chdb-sql/chdb-sql.md) | Run ClickHouse SQL queries in-process on local files, remote databases, and cloud storage without a server |
| check-bin-obj-clash | [SKILL.md](references/dotnet-msbuild/skills/check-bin-obj-clash/SKILL.md) | Detect MSBuild projects with conflicting OutputPath or IntermediateOutputPath |
| clickhouse-architecture-advisor | [clickhouse-architecture-advisor.md](references/clickhouse-architecture-advisor/clickhouse-architecture-advisor.md) | Design ClickHouse architectures and select between ingestion/modeling patterns with workload-specific decision frameworks |
| clickhouse-best-practices | [clickhouse-best-practices.md](references/clickhouse-best-practices/clickhouse-best-practices.md) | Review ClickHouse schemas, queries, or configurations against 31 rules covering schema, query, insert, and agent integration |
| clickhousectl-cloud-deploy | [clickhousectl-cloud-deploy.md](references/clickhousectl-cloud-deploy/clickhousectl-cloud-deploy.md) | Deploy ClickHouse to the cloud, go to production with ClickHouse Cloud, or migrate from local to managed ClickHouse |
| clickhousectl-local-dev | [clickhousectl-local-dev.md](references/clickhousectl-local-dev/clickhousectl-local-dev.md) | Set up a local ClickHouse development environment, install ClickHouse, create tables, and start developing |
| clr-activation-debugging | [SKILL.md](references/dotnet-diag/skills/clr-activation-debugging/SKILL.md) | Diagnose .NET Framework CLR activation issues using CLRLoad logs |
| cockroachdb-sql | [cockroachdb-sql.md](references/cockroachdb-sql/cockroachdb-sql.md) | Write, generate, or optimize SQL for CockroachDB including schema design, type mappings, and distributed database patterns |
| code-testing-agent | [SKILL.md](references/dotnet-test/skills/code-testing-agent/SKILL.md) | Generate comprehensive, workable unit tests for any programming language using a multi-agent pipeline |
| coding-guidelines | [coding-guidelines.md](references/coding-guidelines/coding-guidelines.md) | Rust code style and best practices for naming, formatting, comments, clippy, and rustfmt |
| configuring-audit-logging | [configuring-audit-logging.md](references/configuring-audit-logging/configuring-audit-logging.md) | Configure SQL audit logging on CockroachDB clusters to capture security-relevant events for compliance |
| configuring-ip-allowlists | [configuring-ip-allowlists.md](references/configuring-ip-allowlists/configuring-ip-allowlists.md) | Configure and harden IP allowlists for CockroachDB Cloud clusters to restrict network access |
| configuring-log-export | [configuring-log-export.md](references/configuring-log-export/configuring-log-export.md) | Configure log and metric export for CockroachDB Cloud clusters to external monitoring services |
| configuring-private-connectivity | [configuring-private-connectivity.md](references/configuring-private-connectivity/configuring-private-connectivity.md) | Configure private network connectivity for CockroachDB Cloud (PrivateLink, PSC, Azure Private Link, VPC peering) |
| configuring-sso-and-scim | [configuring-sso-and-scim.md](references/configuring-sso-and-scim/configuring-sso-and-scim.md) | Configure SSO authentication and SCIM 2.0 provisioning for CockroachDB across Console, DB Console, SQL, and SCIM layers |
| convert-to-cpm | [SKILL.md](references/dotnet-nuget/skills/convert-to-cpm/SKILL.md) | Convert .NET projects and solutions to NuGet Central Package Management (CPM) using Directory.Packages.props |
| crap-score | [SKILL.md](references/dotnet-test/skills/crap-score/SKILL.md) | Calculate CRAP score for .NET methods, classes, or files using code coverage and cyclomatic complexity |
| csharp-mstest | [csharp-mstest.md](references/csharp-mstest/csharp-mstest.md) | Write effective MSTest 3.x/4.x unit tests with modern assertion APIs and data-driven tests |
| csharp-scripts | [SKILL.md](references/dotnet/skills/csharp-scripts/SKILL.md) | Run single-file C# programs as scripts for quick experimentation, prototyping, and concept testing |
| csharp-tunit | [csharp-tunit.md](references/csharp-tunit/csharp-tunit.md) | Write effective TUnit unit tests including data-driven tests |
| csharp-xunit | [csharp-xunit.md](references/csharp-xunit/csharp-xunit.md) | Write effective XUnit unit tests including data-driven tests |
| designing-application-transactions | [designing-application-transactions.md](references/designing-application-transactions/designing-application-transactions.md) | Design correct and performant transaction patterns for CockroachDB apps (retries, pooling, prepared statements, follower reads) |
| designing-multi-region-applications | [designing-multi-region-applications.md](references/designing-multi-region-applications/designing-multi-region-applications.md) | Select and implement multi-region patterns for CockroachDB (REGIONAL BY ROW, GLOBAL tables, geo-partitioning) |
| directory-build-organization | [SKILL.md](references/dotnet-msbuild/skills/directory-build-organization/SKILL.md) | Guide for organizing MSBuild infrastructure with Directory.Build.props, Directory.Build.targets, and Directory.Packages.props |
| domain-cli | [domain-cli.md](references/domain-cli/domain-cli.md) | Build CLI tools with argument parsing, subcommands, TUI, progress bars, shell completion, and config layering |
| domain-cloud-native | [domain-cloud-native.md](references/domain-cloud-native/domain-cloud-native.md) | Build cloud-native apps with Kubernetes, Docker, gRPC, microservices, observability, and health checks |
| domain-embedded | [domain-embedded.md](references/domain-embedded/domain-embedded.md) | Develop embedded/no_std Rust for microcontrollers (ARM, RISC-V, HAL, PAC, RTIC, embassy) |
| domain-fintech | [domain-fintech.md](references/domain-fintech/domain-fintech.md) | Build fintech apps with decimal precision, currency handling, ledger, payments, and audit trails |
| domain-iot | [domain-iot.md](references/domain-iot/domain-iot.md) | Build IoT apps with sensors, MQTT, edge computing, telemetry, and device management |
| domain-ml | [domain-ml.md](references/domain-ml/domain-ml.md) | Build ML/AI apps in Rust with tensor ops, model inference, training, and prediction |
| domain-web | [domain-web.md](references/domain-web/domain-web.md) | Build web services with HTTP, REST, GraphQL, WebSocket, middleware, auth, and routing |
| dotnet-aot-wasm | [dotnet-aot-wasm.md](references/dotnet-aot-wasm/dotnet-aot-wasm.md) | AOT-compile Blazor/Uno WASM apps balancing download size vs runtime speed with trimming and Brotli |
| dotnet-aspire-patterns | [dotnet-aspire-patterns.md](references/dotnet-aspire-patterns/dotnet-aspire-patterns.md) | Build .NET Aspire distributed apps with AppHost orchestration, service discovery, components, and dashboard |
| dotnet-benchmarkdotnet | [dotnet-benchmarkdotnet.md](references/dotnet-benchmarkdotnet/dotnet-benchmarkdotnet.md) | Write .NET microbenchmarks with BenchmarkDotNet including memory diagnosers, baselines, and result analysis |
| dotnet-blazor-auth | [dotnet-blazor-auth.md](references/dotnet-blazor-auth/dotnet-blazor-auth.md) | Add authentication/authorization to Blazor apps with AuthorizeView, CascadingAuthenticationState, and Identity UI |
| dotnet-blazor-components | [dotnet-blazor-components.md](references/dotnet-blazor-components/dotnet-blazor-components.md) | Build Blazor components with lifecycle, state management, JS interop, EditForm validation, and QuickGrid |
| dotnet-blazor-patterns | [dotnet-blazor-patterns.md](references/dotnet-blazor-patterns/dotnet-blazor-patterns.md) | Build Blazor apps choosing hosting models, render modes, routing, streaming rendering, and prerender |
| dotnet-blazor-testing | [dotnet-blazor-testing.md](references/dotnet-blazor-testing/dotnet-blazor-testing.md) | Test Blazor components with bUnit for rendering, events, cascading params, and JS interop mocking |
| dotnet-channels | [dotnet-channels.md](references/dotnet-channels/dotnet-channels.md) | Use Channel<T> for producer/consumer queues with bounded/unbounded channels, backpressure, and drain patterns |
| dotnet-ci-benchmarking | [dotnet-ci-benchmarking.md](references/dotnet-ci-benchmarking/dotnet-ci-benchmarking.md) | Gate CI on performance regressions with automated threshold alerts, baseline tracking, and trend reports |
| dotnet-cli-architecture | [dotnet-cli-architecture.md](references/dotnet-cli-architecture/dotnet-cli-architecture.md) | Structure CLI app layers with command/handler/service separation following clig.dev principles |
| dotnet-cli-distribution | [dotnet-cli-distribution.md](references/dotnet-cli-distribution/dotnet-cli-distribution.md) | Choose CLI output format: AOT vs framework-dependent, RID matrix, single-file publish, or dotnet tool |
| dotnet-cli-packaging | [dotnet-cli-packaging.md](references/dotnet-cli-packaging/dotnet-cli-packaging.md) | Publish CLI tools to package managers: Homebrew, apt/deb, winget, Scoop, Chocolatey |
| dotnet-cli-release-pipeline | [dotnet-cli-release-pipeline.md](references/dotnet-cli-release-pipeline/dotnet-cli-release-pipeline.md) | Release CLI tools via GitHub Actions build matrix, artifact staging, GitHub Releases, and checksums |
| dotnet-containers | [dotnet-containers.md](references/dotnet-containers/dotnet-containers.md) | Containerize .NET apps with multi-stage Dockerfiles, SDK container publish (.NET 8+), rootless |
| dotnet-cryptography | [dotnet-cryptography.md](references/dotnet-cryptography/dotnet-cryptography.md) | Choose crypto algorithms, hashing, encryption, or key derivation — AES-GCM, RSA, ECDSA, PQC |
| dotnet-csharp-dependency-injection | [dotnet-csharp-dependency-injection.md](references/dotnet-csharp-dependency-injection/dotnet-csharp-dependency-injection.md) | Register or resolve services with MS DI — keyed services, scopes, decoration, hosted services |
| dotnet-csharp-modern-patterns | [dotnet-csharp-modern-patterns.md](references/dotnet-csharp-modern-patterns/dotnet-csharp-modern-patterns.md) | Use records, pattern matching, primary constructors, collection expressions — C# 12-15 by TFM |
| dotnet-csharp-nullable-reference-types | [dotnet-csharp-nullable-reference-types.md](references/dotnet-csharp-nullable-reference-types/dotnet-csharp-nullable-reference-types.md) | Enable nullable reference types — annotation strategies, attributes, common agent mistakes |
| dotnet-csharp-source-generators | [dotnet-csharp-source-generators.md](references/dotnet-csharp-source-generators/dotnet-csharp-source-generators.md) | Create source generators — IIncrementalGenerator, GeneratedRegex, LoggerMessage, STJ source-gen |
| dotnet-maui | [dotnet-maui.md](references/dotnet-maui/dotnet-maui.md) | .NET MAUI cross-platform application development |
| dotnet-maui-doctor | [dotnet-maui-doctor.md](references/dotnet-maui-doctor/dotnet-maui-doctor.md) | Diagnose and fix .NET MAUI development environment issues — validates SDK, workloads, JDK, Android SDK, Xcode, Windows SDK |
| dotnet-observability | [dotnet-observability.md](references/dotnet-observability/dotnet-observability.md) | Add observability — OpenTelemetry traces/metrics/logs, health checks, custom metrics |
| dotnet-pinvoke | [SKILL.md](references/dotnet/skills/dotnet-pinvoke/SKILL.md) | Call native (C/C++) libraries from .NET using P/Invoke and LibraryImport |
| dotnet-trace-collect | [SKILL.md](references/dotnet-diag/skills/dotnet-trace-collect/SKILL.md) | Guide developers through capturing diagnostic artifacts to diagnose production .NET performance issues |
| dotnet-winui | [dotnet-winui.md](references/dotnet-winui/dotnet-winui.md) | Build WinUI 3 apps — Windows App SDK setup, XAML patterns, MSIX/unpackaged deploy, UWP migration |
| dotnet-wpf-modern | [dotnet-wpf-modern.md](references/dotnet-wpf-modern/dotnet-wpf-modern.md) | Build WPF on .NET 8+ — Host builder, MVVM Toolkit, Fluent theme, performance, modern C# patterns |
| dump-collect | [SKILL.md](references/dotnet-diag/skills/dump-collect/SKILL.md) | Configure and collect crash dumps for modern .NET applications |
| enabling-cmek-encryption | [enabling-cmek-encryption.md](references/enabling-cmek-encryption/enabling-cmek-encryption.md) | Enable Customer-Managed Encryption Keys (CMEK) on CockroachDB Cloud clusters |
| enforcing-password-policies | [enforcing-password-policies.md](references/enforcing-password-policies/enforcing-password-policies.md) | Configure and enforce password policies on CockroachDB clusters |
| eval-performance | [SKILL.md](references/dotnet-msbuild/skills/eval-performance/SKILL.md) | Diagnose and improve MSBuild project evaluation performance |
| exp-assertion-quality | [SKILL.md](references/dotnet-experimental/skills/exp-assertion-quality/SKILL.md) | Analyze variety and depth of assertions across .NET test suites |
| exp-mock-usage-analysis | [SKILL.md](references/dotnet-experimental/skills/exp-mock-usage-analysis/SKILL.md) | Audit .NET test mock usage to find dead, unreachable, redundant, or replaceable mocks |
| exp-simd-vectorization | [SKILL.md](references/dotnet-experimental/skills/exp-simd-vectorization/SKILL.md) | Optimize hot-path scalar loops in .NET 8+ with cross-platform SIMD intrinsics |
| exp-test-boilerplate-detection | [SKILL.md](references/dotnet-experimental/skills/exp-test-boilerplate-detection/SKILL.md) | Detect duplicate boilerplate patterns across .NET test suites and identify refactoring opportunities |
| exp-test-gap-analysis | [SKILL.md](references/dotnet-experimental/skills/exp-test-gap-analysis/SKILL.md) | Perform pseudo-mutation analysis on .NET production code to find gaps in existing test suites |
| exp-test-maintainability | [SKILL.md](references/dotnet-experimental/skills/exp-test-maintainability/SKILL.md) | Assess maintainability of .NET test suites and recommend structural improvements |
| exp-test-smell-detection | [SKILL.md](references/dotnet-experimental/skills/exp-test-smell-detection/SKILL.md) | Detect test smells and anti-patterns in test code that indicate design problems |
| exp-test-tagging | [SKILL.md](references/dotnet-experimental/skills/exp-test-tagging/SKILL.md) | Analyze test suites and tag each test with standardized traits (positive, negative, critical-path, boundary, smoke) |
| find-skills | [find-skills.md](references/find-skills/find-skills.md) | Help users discover and install agent skills |
| firecracker | [firecracker.md](references/firecracker/firecracker.md) | Firecracker VMM — architecture, usage, best practices, security, jailer, and production guidance for microVMs |
| gdpr-compliant | [gdpr-compliant.md](references/gdpr-compliant/gdpr-compliant.md) | Apply GDPR-compliant engineering practices — APIs, data models, auth flows, logging, retention, encryption, breach response |
| golang-benchmark | [golang-benchmark.md](references/golang-benchmark/golang-benchmark.md) | Golang benchmarking, profiling, and performance measurement — pprof, benchstat, CI regression detection |
| golang-cli | [golang-cli.md](references/golang-cli/golang-cli.md) | Golang CLI application development — command structure, flag handling, config layering, exit codes, shell completion |
| golang-code-style | [golang-code-style.md](references/golang-code-style/golang-code-style.md) | Golang code style conventions — line length, variable declarations, control flow clarity, comment usage |
| golang-concurrency | [golang-concurrency.md](references/golang-concurrency/golang-concurrency.md) | Golang concurrency patterns — goroutines, channels, select, locks, errgroup, singleflight, worker pools |
| golang-context | [golang-context.md](references/golang-context/golang-context.md) | Idiomatic context.Context usage — propagation, cancellation, timeouts, request-scoped values |
| golang-continuous-integration | [golang-continuous-integration.md](references/golang-continuous-integration/golang-continuous-integration.md) | CI/CD pipeline configuration using GitHub Actions for Go — testing, linting, SAST, Dependabot, GoReleaser |
| golang-data-structures | [golang-data-structures.md](references/golang-data-structures/golang-data-structures.md) | Golang data structures — slices, maps, arrays, container packages, strings.Builder, generic collections |
| golang-database | [golang-database.md](references/golang-database/golang-database.md) | Go database access — parameterized queries, struct scanning, transactions, connection pools, migration tooling |
| golang-dependency-injection | [golang-dependency-injection.md](references/golang-dependency-injection/golang-dependency-injection.md) | Dependency injection in Golang — manual constructor injection and DI library comparison |
| golang-dependency-management | [golang-dependency-management.md](references/golang-dependency-management/golang-dependency-management.md) | Dependency management strategies — go.mod, Minimal Version Selection, vulnerability scanning, Dependabot/Renovate |
| golang-design-patterns | [golang-design-patterns.md](references/golang-design-patterns/golang-design-patterns.md) | Idiomatic Golang design patterns — functional options, constructors, error cascading, graceful shutdown, resilience |
| golang-documentation | [golang-documentation.md](references/golang-documentation/golang-documentation.md) | Golang documentation guide — godoc comments, README, CONTRIBUTING, CHANGELOG, Example tests, llms.txt |
| golang-error-handling | [golang-error-handling.md](references/golang-error-handling/golang-error-handling.md) | Idiomatic Golang error handling — wrapping, errors.Is/As, custom types, panic/recover, structured logging with slog |
| golang-google-wire | [golang-google-wire.md](references/golang-google-wire/golang-google-wire.md) | Compile-time DI in Golang using google/wire — wire.NewSet, wire.Build, wire.Bind, injector files, wire_gen.go |
| golang-graphql | [golang-graphql.md](references/golang-graphql/golang-graphql.md) | Implement GraphQL APIs in Golang using gqlgen or graphql-go — schemas, resolvers, subscriptions |
| golang-grpc | [golang-grpc.md](references/golang-grpc/golang-grpc.md) | gRPC usage guidelines, protobuf organization, and production-ready patterns for Golang microservices |
| golang-lint | [golang-lint.md](references/golang-lint/golang-lint.md) | Linting best practices and golangci-lint configuration — .golangci.yml, nolint directives, linter selection |
| golang-modernize | [golang-modernize.md](references/golang-modernize/golang-modernize.md) | Modernize Golang code to use recent language features, stdlib improvements, and idiomatic patterns |
| golang-naming | [golang-naming.md](references/golang-naming/golang-naming.md) | Go naming conventions — packages, constructors, structs, interfaces, constants, errors, receivers, getters/setters |
| golang-observability | [golang-observability.md](references/golang-observability/golang-observability.md) | Golang everyday observability — slog logging, Prometheus metrics, OpenTelemetry tracing, pprof profiling, alerting |
| golang-performance | [golang-performance.md](references/golang-performance/golang-performance.md) | Golang performance optimization patterns — allocation reduction, CPU efficiency, memory layout, GC tuning |
| golang-popular-libraries | [golang-popular-libraries.md](references/golang-popular-libraries/golang-popular-libraries.md) | Recommend production-ready Golang libraries and frameworks for specific tasks |
| golang-project-layout | [golang-project-layout.md](references/golang-project-layout/golang-project-layout.md) | Guide for setting up Golang project layouts and workspaces — cmd/internal/pkg conventions, monorepo, module splits |
| golang-safety | [golang-safety.md](references/golang-safety/golang-safety.md) | Defensive Golang coding — prevent nil panics, append aliasing, map concurrent access, float comparison pitfalls |
| golang-samber-do | [golang-samber-do.md](references/golang-samber-do/golang-samber-do.md) | DI in Golang using samber/do — service containers, lifecycle management, scopes, health checks, graceful shutdown |
| golang-samber-hot | [golang-samber-hot.md](references/golang-samber-hot/golang-samber-hot.md) | In-memory caching in Golang using samber/hot — eviction algorithms, TTL, cache loaders, sharding, Prometheus metrics |
| golang-samber-lo | [golang-samber-lo.md](references/golang-samber-lo/golang-samber-lo.md) | Functional programming helpers for Golang using samber/lo — 500+ type-safe generic functions |
| golang-samber-mo | [golang-samber-mo.md](references/golang-samber-mo/golang-samber-mo.md) | Monadic types for Golang using samber/mo — Option, Result, Either, Future, IO, Task, State types |
| golang-samber-oops | [golang-samber-oops.md](references/golang-samber-oops/golang-samber-oops.md) | Structured error handling in Golang with samber/oops — error builders, stack traces, error codes, context, wrapping |
| golang-samber-ro | [golang-samber-ro.md](references/golang-samber-ro/golang-samber-ro.md) | Reactive streams and event-driven programming in Golang using samber/ro — ReactiveX with 150+ operators |
| golang-samber-slog | [golang-samber-slog.md](references/golang-samber-slog/golang-samber-slog.md) | Structured logging extensions for Golang using samber/slog-* packages — multi-handler pipelines, sampling, formatting |
| golang-security | [golang-security.md](references/golang-security/golang-security.md) | Security best practices and vulnerability prevention for Golang — injection, cryptography, secrets management |
| golang-spf13-cobra | [golang-spf13-cobra.md](references/golang-spf13-cobra/golang-spf13-cobra.md) | Golang CLI command tree library using spf13/cobra — commands, hooks, validators, flags, completion, doc generation |
| golang-spf13-viper | [golang-spf13-viper.md](references/golang-spf13-viper/golang-spf13-viper.md) | Golang configuration library using spf13/viper — layered precedence, env binding, config files, hot reload |
| golang-stay-updated | [golang-stay-updated.md](references/golang-stay-updated/golang-stay-updated.md) | Resources to stay updated with Golang news, communities, and people to follow |
| golang-stretchr-testify | [golang-stretchr-testify.md](references/golang-stretchr-testify/golang-stretchr-testify.md) | Comprehensive guide to stretchr/testify for Golang testing — assert, require, mock, and suite packages |
| golang-structs-interfaces | [golang-structs-interfaces.md](references/golang-structs-interfaces/golang-structs-interfaces.md) | Golang struct and interface design patterns — composition, embedding, type assertions, interface segregation, field tags |
| golang-swagger | [golang-swagger.md](references/golang-swagger/golang-swagger.md) | Golang OpenAPI/Swagger documentation with swaggo/swag — annotation comments, code generation, framework integrations |
| golang-testing | [golang-testing.md](references/golang-testing/golang-testing.md) | Production-ready Golang tests — table-driven tests, testify, parallel tests, fuzzing, fixtures, goroutine leak detection |
| golang-troubleshooting | [golang-troubleshooting.md](references/golang-troubleshooting/golang-troubleshooting.md) | Troubleshoot Golang programs systematically — debugging methodology, common pitfalls, pprof, Delve, race detection |
| golang-uber-dig | [golang-uber-dig.md](references/golang-uber-dig/golang-uber-dig.md) | DI in Golang using uber-go/dig — reflection-based container, Provide/Invoke, parameter/result objects, value groups |
| golang-uber-fx | [golang-uber-fx.md](references/golang-uber-fx/golang-uber-fx.md) | Golang application framework using uber-go/fx — fx.New, lifecycle hooks, modules, annotations, decorators |
| hardening-user-privileges | [hardening-user-privileges.md](references/hardening-user-privileges/hardening-user-privileges.md) | Harden CockroachDB user privileges by auditing and tightening role-based access control |
| hipaa-compliance | [hipaa-compliance.md](references/hipaa-compliance/hipaa-compliance.md) | Enforceable HIPAA compliance controls when handling PHI, ePHI, or any healthcare-related data |
| including-generated-files | [SKILL.md](references/dotnet-msbuild/skills/including-generated-files/SKILL.md) | Fix MSBuild targets that generate files during the build but those files are missing from compilation |
| incremental-build | [SKILL.md](references/dotnet-msbuild/skills/incremental-build/SKILL.md) | Optimize MSBuild incremental builds — diagnose why targets re-execute unnecessarily |
| inflowpay | [inflowpay.md](references/inflowpay/inflowpay.md) | Integrate InflowPay payment infrastructure — one-time payments, subscriptions, webhooks, refunds, marketplace Connect |
| investigating-with-observability | [investigating-with-observability.md](references/investigating-with-observability/investigating-with-observability.md) | Investigate issues, debug problems, or respond to alerts in Kubernetes clusters using VictoriaMetrics/VictoriaLogs/VictoriaTraces |
| kubernetes | [kubernetes.md](references/kubernetes/kubernetes.md) | Kubernetes architecture, deployment, management, and troubleshooting |
| kubernetes-hipaa-gdpr-compliance | [hipaa-gdpr-compliance-kubernetes.md](references/hipaa-gdpr-compliance-kubernetes/hipaa-gdpr-compliance-kubernetes.md) | Kubernetes-specific constraints required for HIPAA and GDPR compliance — hard guardrail for manifests and architectures |
| kyverno | [kyverno.md](references/kyverno/kyverno.md) | Kubernetes-native policy engine for automating security, compliance, best practices, and governance |
| m01-ownership | [m01-ownership.md](references/m01-ownership/m01-ownership.md) | Rust ownership, borrow, and lifetime issues (E0382, E0597, move, clone, Copy, 'static) |
| m02-resource | [m02-resource.md](references/m02-resource/m02-resource.md) | Rust smart pointers and resource management (Box, Rc, Arc, Weak, RefCell, Cell, RAII, Drop) |
| m03-mutability | [m03-mutability.md](references/m03-mutability/m03-mutability.md) | Rust mutability issues (E0596, E0499, E0502, interior mutability, Cell, RefCell, Mutex, RwLock) |
| m04-zero-cost | [m04-zero-cost.md](references/m04-zero-cost/m04-zero-cost.md) | Rust generics, traits, and zero-cost abstraction (monomorphization, dispatch, impl Trait, trait bounds) |
| m05-type-driven | [m05-type-driven.md](references/m05-type-driven/m05-type-driven.md) | Rust type-driven design (type state, PhantomData, newtype, builder pattern, sealed trait, ZST) |
| m06-error-handling | [m06-error-handling.md](references/m06-error-handling/m06-error-handling.md) | Rust error handling (Result, Option, ?, unwrap, expect, panic, anyhow, thiserror, error propagation) |
| m07-concurrency | [m07-concurrency.md](references/m07-concurrency/m07-concurrency.md) | Rust concurrency and async (Send/Sync, threads, channels, Mutex, Atomic, async/await, tokio, deadlocks) |
| m09-domain | [m09-domain.md](references/m09-domain/m09-domain.md) | Rust domain modeling (DDD, entities, value objects, aggregates, repository pattern, business rules, invariants) |
| m10-performance | [m10-performance.md](references/m10-performance/m10-performance.md) | Rust performance optimization (benchmarking, profiling, flamegraph, criterion, allocation, cache, SIMD) |
| m11-ecosystem | [m11-ecosystem.md](references/m11-ecosystem/m11-ecosystem.md) | Rust crate integration and ecosystem (cargo, dependencies, feature flags, workspaces, PyO3, wasm, bindgen) |
| m12-lifecycle | [m12-lifecycle.md](references/m12-lifecycle/m12-lifecycle.md) | Rust resource lifecycle design (RAII, Drop, connection pools, lazy initialization, OnceCell, guard patterns) |
| m13-domain-error | [m13-domain-error.md](references/m13-domain-error/m13-domain-error.md) | Rust domain error handling design (categorization, recovery, retry, circuit breaker, graceful degradation) |
| m14-mental-model | [m14-mental-model.md](references/m14-mental-model/m14-mental-model.md) | Learning Rust concepts — mental models, analogies, understanding borrow checker, memory layout |
| m15-anti-pattern | [m15-anti-pattern.md](references/m15-anti-pattern/m15-anti-pattern.md) | Review Rust code for anti-patterns, code smells, common mistakes, and non-idiomatic patterns |
| manage-postgresql-cloudnativepg-k8s | [manage-postgresql-cloudnativepg-k8s.md](references/manage-postgresql-cloudnativepg-k8s/manage-postgresql-cloudnativepg-k8s.md) | Deploy, configure, operate, scale, backup, recover, monitor, upgrade PostgreSQL on Kubernetes using CloudNativePG |
| managing-certificates-and-encryption | [managing-certificates-and-encryption.md](references/managing-certificates-and-encryption/managing-certificates-and-encryption.md) | Manage TLS certificate and encryption key lifecycle for CockroachDB across all tiers including CMEK |
| managing-cluster-capacity | [managing-cluster-capacity.md](references/managing-cluster-capacity/managing-cluster-capacity.md) | Manage CockroachDB cluster capacity — scaling nodes up/down, decommissioning, cost management |
| managing-cluster-settings | [managing-cluster-settings.md](references/managing-cluster-settings/managing-cluster-settings.md) | Review, audit, and modify CockroachDB cluster settings and session variables |
| managing-tls-certificates | [managing-tls-certificates.md](references/managing-tls-certificates/managing-tls-certificates.md) | Manage TLS certificates for CockroachDB — CA config, client cert auth, rotation, troubleshooting SSL/TLS |
| mcp-csharp-create | [SKILL.md](references/dotnet-ai/mcp-csharp-create/SKILL.md) | Create MCP servers using the C# SDK and .NET project templates |
| mcp-csharp-debug | [SKILL.md](references/dotnet-ai/mcp-csharp-debug/SKILL.md) | Run and debug C# MCP servers locally |
| mcp-csharp-publish | [SKILL.md](references/dotnet-ai/mcp-csharp-publish/SKILL.md) | Publish and deploy C# MCP servers |
| mcp-csharp-test | [SKILL.md](references/dotnet-ai/mcp-csharp-test/SKILL.md) | Test C# MCP servers at multiple levels |
| meta-cognition-parallel | [meta-cognition-parallel.md](references/meta-cognition-parallel/meta-cognition-parallel.md) | Experimental three-layer parallel meta-cognition analysis |
| microbenchmarking | [SKILL.md](references/dotnet-diag/skills/microbenchmarking/SKILL.md) | Guide for BenchmarkDotNet microbenchmark design, configuration, and result analysis |
| microsoft-agent-framework | [microsoft-agent-framework.md](references/microsoft-agent-framework/microsoft-agent-framework.md) | Create, update, refactor, explain, or review Microsoft Agent Framework solutions in .NET and Python |
| microsoft-code-reference | [microsoft-code-reference.md](references/microsoft-code-reference/microsoft-code-reference.md) | Look up Microsoft API references, find working code samples, and verify SDK code against official docs |
| microsoft-foundry | [microsoft-foundry.md](references/microsoft-foundry/microsoft-foundry.md) | Deploy, evaluate, fine-tune, and manage Foundry agents end-to-end |
| migrate-mstest-v1v2-to-v3 | [SKILL.md](references/dotnet-test/skills/migrate-mstest-v1v2-to-v3/SKILL.md) | Migrate MSTest v1 or v2 test project to MSTest v3 |
| migrate-mstest-v3-to-v4 | [SKILL.md](references/dotnet-test/skills/migrate-mstest-v3-to-v4/SKILL.md) | Migrate an MSTest v3 test project to MSTest v4 |
| migrate-vstest-to-mtp | [SKILL.md](references/dotnet-test/skills/migrate-vstest-to-mtp/SKILL.md) | Migrate .NET test projects from VSTest to Microsoft.Testing.Platform (MTP) |
| migrate-xunit-to-xunit-v3 | [SKILL.md](references/dotnet-test/skills/migrate-xunit-to-xunit-v3/SKILL.md) | Migrate .NET test projects from xUnit.net v2 to xUnit.net v3 |
| molt-fetch | [molt-fetch.md](references/molt-fetch/molt-fetch.md) | Migrate data from PostgreSQL, MySQL, Oracle, or MSSQL to CockroachDB using molt fetch |
| molt-replicator | [molt-replicator.md](references/molt-replicator/molt-replicator.md) | Continuously replicate changes from PostgreSQL, MySQL, or Oracle to CockroachDB |
| molt-verify | [molt-verify.md](references/molt-verify/molt-verify.md) | Compare source and target databases for schema and row-level consistency after a migration |
| monitoring-background-jobs | [monitoring-background-jobs.md](references/monitoring-background-jobs/monitoring-background-jobs.md) | Monitor CockroachDB background job health by identifying failed, paused, and long-running jobs |
| msbuild-antipatterns | [SKILL.md](references/dotnet-msbuild/skills/msbuild-antipatterns/SKILL.md) | Catalog of MSBuild anti-patterns with detection rules and fix recipes |
| msbuild-modernization | [SKILL.md](references/dotnet-msbuild/skills/msbuild-modernization/SKILL.md) | Modernize and migrate MSBuild project files to SDK-style format |
| msbuild-server | [SKILL.md](references/dotnet-msbuild/skills/msbuild-server/SKILL.md) | Guide for using MSBuild Server to improve CLI build performance |
| mtp-hot-reload | [SKILL.md](references/dotnet-test/skills/mtp-hot-reload/SKILL.md) | Use MTP hot reload to iterate fixes on failing tests without rebuilding |
| mudblazor | [mudblazor.md](references/mudblazor/mudblazor.md) | Build, maintain, and optimize production-grade Blazor applications using MudBlazor components |
| nats | [nats.md](references/nats/nats.md) | Deploy and operate NATS messaging system for cloud native apps, IoT, and microservices |
| nuget-trusted-publishing | [SKILL.md](references/dotnet/skills/nuget-trusted-publishing/SKILL.md) | Set up NuGet trusted publishing (OIDC) on GitHub Actions — replaces long-lived API keys with short-lived tokens |
| openbao | [openbao.md](references/openbao/openbao.md) | Open source fork of HashiCorp Vault for secrets management (KV, PKI, Transit, dynamic secrets) |
| optimizing-ef-core-queries | [SKILL.md](references/dotnet-data/skills/optimizing-ef-core-queries/SKILL.md) | Optimize Entity Framework Core queries by fixing N+1 problems, choosing tracking modes, using compiled queries |
| performing-cluster-maintenance | [performing-cluster-maintenance.md](references/performing-cluster-maintenance/performing-cluster-maintenance.md) | Manage planned CockroachDB cluster maintenance across all tiers |
| podman | [podman.md](references/podman/podman.md) | Daemonless, rootless OCI container engine compatible with Docker CLI |
| podman-quadlet | [podman-quadlet.md](references/podman-quadlet/podman-quadlet.md) | Create, manage, or troubleshoot containers or pods as systemd services using Podman Quadlet |
| preparing-compliance-documentation | [preparing-compliance-documentation.md](references/preparing-compliance-documentation/preparing-compliance-documentation.md) | Prepare compliance documentation for CockroachDB Cloud (SOC 2, PCI DSS, ISO 27001, HIPAA, GDPR) |
| profiling-statement-fingerprints | [profiling-statement-fingerprints.md](references/profiling-statement-fingerprints/profiling-statement-fingerprints.md) | Rank and analyze SQL statement fingerprints to identify slow or error-prone query patterns |
| profiling-transaction-fingerprints | [profiling-transaction-fingerprints.md](references/profiling-transaction-fingerprints/profiling-transaction-fingerprints.md) | Analyze transaction fingerprints to identify high-retry transactions and contention patterns |
| provisioning-cluster-for-production | [provisioning-cluster-for-production.md](references/provisioning-cluster-for-production/provisioning-cluster-for-production.md) | Guide initial CockroachDB cluster provisioning and production deployment |
| rabbitmq | [rabbitmq.md](references/rabbitmq/rabbitmq.md) | Comprehensive RabbitMQ guidance for message brokering, AMQP, clustering, and Kubernetes deployment |
| razor-pages-patterns | [razor-pages-patterns.md](references/razor-pages-patterns/razor-pages-patterns.md) | Best practices for building production-grade ASP.NET Core Razor Pages applications |
| resolve-project-references | [SKILL.md](references/dotnet-msbuild/skills/resolve-project-references/SKILL.md) | Guide for interpreting ResolveProjectReferences time in MSBuild performance summaries |
| reviewing-cluster-health | [reviewing-cluster-health.md](references/reviewing-cluster-health/reviewing-cluster-health.md) | Perform comprehensive health checks of a CockroachDB cluster |
| run-tests | [SKILL.md](references/dotnet-test/skills/run-tests/SKILL.md) | Run .NET tests with dotnet test — detect platform, identify framework, apply filters, troubleshoot failures |
| rust | [rust.md](references/rust/rust.md) | Comprehensive Rust coding guidelines with 179 rules across 14 categories |
| rust-call-graph | [rust-call-graph.md](references/rust-call-graph/rust-call-graph.md) | Visualize Rust function call graphs using LSP call hierarchy |
| rust-code-navigator | [rust-code-navigator.md](references/rust-code-navigator/rust-code-navigator.md) | Navigate Rust code using LSP (go to definition, find references) |
| rust-daily | [rust-daily.md](references/rust-daily/rust-daily.md) | Generate Rust news and daily/weekly/monthly reports |
| rust-deps-visualizer | [rust-deps-visualizer.md](references/rust-deps-visualizer/rust-deps-visualizer.md) | Visualize Rust project dependencies as ASCII art |
| rust-learner | [rust-learner.md](references/rust-learner/rust-learner.md) | Look up Rust versions, crate info, and API documentation |
| rust-refactor-helper | [rust-refactor-helper.md](references/rust-refactor-helper/rust-refactor-helper.md) | Perform safe Rust refactoring with LSP analysis |
| rust-skill-creator | [rust-skill-creator.md](references/rust-skill-creator/rust-skill-creator.md) | Create skills for Rust crates or std library documentation |
| rust-symbol-analyzer | [rust-symbol-analyzer.md](references/rust-symbol-analyzer/rust-symbol-analyzer.md) | Analyze Rust project structure using LSP symbols |
| rust-trait-explorer | [rust-trait-explorer.md](references/rust-trait-explorer/rust-trait-explorer.md) | Explore Rust trait implementations using LSP |
| tailwind-css | [tailwind-css.md](references/tailwind-css/tailwind-css.md) | Style with Tailwind CSS v4, add/fix classes, use tailwind-variants, or configure Tailwind |
| template-authoring | [SKILL.md](references/dotnet-template-engine/skills/template-authoring/SKILL.md) | Guide creation and validation of custom dotnet new templates |
| template-discovery | [SKILL.md](references/dotnet-template-engine/skills/template-discovery/SKILL.md) | Find, inspect, and compare .NET project templates |
| template-instantiation | [SKILL.md](references/dotnet-template-engine/skills/template-instantiation/SKILL.md) | Create .NET projects from templates with validated parameters and smart defaults |
| template-validation | [SKILL.md](references/dotnet-template-engine/skills/template-validation/SKILL.md) | Validate custom dotnet new templates for correctness before publishing |
| technology-selection | [SKILL.md](references/dotnet-ai/technology-selection/SKILL.md) | Guide technology selection for AI/ML features in .NET 8+ applications |
| test-anti-patterns | [SKILL.md](references/dotnet-test/skills/test-anti-patterns/SKILL.md) | Detect anti-patterns and code smells in .NET test suites |
| testcontainers | [testcontainers.md](references/testcontainers/testcontainers.md) | Use Testcontainers in .NET integration tests to spin up real dependencies like databases |
| triaging-live-sql-activity | [triaging-live-sql-activity.md](references/triaging-live-sql-activity/triaging-live-sql-activity.md) | Diagnose live CockroachDB performance issues by identifying long-running queries and busy sessions |
| understand | [understand.md](references/understand/understand.md) | Analyze a codebase to produce an interactive knowledge graph |
| understand-chat | [understand-chat.md](references/understand-chat/understand-chat.md) | Ask questions about a codebase using a knowledge graph |
| understand-dashboard | [understand-dashboard.md](references/understand-dashboard/understand-dashboard.md) | Launch interactive web dashboard to visualize a codebase's knowledge graph |
| understand-diff | [understand-diff.md](references/understand-diff/understand-diff.md) | Analyze git diffs or pull requests to understand changes and risks |
| understand-domain | [understand-domain.md](references/understand-domain/understand-domain.md) | Extract business domain knowledge from a codebase and generate domain flow graphs |
| understand-explain | [understand-explain.md](references/understand-explain/understand-explain.md) | Get deep-dive explanations of specific files, functions, or modules |
| understand-knowledge | [understand-knowledge.md](references/understand-knowledge/understand-knowledge.md) | Analyze Karpathy-pattern LLM wiki knowledge bases and generate interactive knowledge graphs |
| understand-onboard | [understand-onboard.md](references/understand-onboard/understand-onboard.md) | Generate onboarding guides for new team members from project knowledge graphs |
| unit-and-integration-tests-discovery | [SKILLS.md](references/unit-and-integration-tests-discovery/SKILLS.md) | Discover unit and integration tests in a codebase |
| unsafe-checker | [unsafe-checker.md](references/unsafe-checker/unsafe-checker.md) | Review unsafe Rust code and FFI for soundness issues |
| upgrading-cluster-version | [upgrading-cluster-version.md](references/upgrading-cluster-version/upgrading-cluster-version.md) | Guide CockroachDB version upgrades with tier-appropriate procedures |
| velero | [velero.md](references/velero/velero.md) | Kubernetes backup, restore, and migration tool using CSI snapshots or filesystem backups |
| victorialogs-query | [victorialogs-query.md](references/victorialogs-query/victorialogs-query.md) | Query VictoriaLogs via curl using LogsQL for log search and analysis |
| victoriametrics | [victoriametrics.md](references/victoriametrics/victoriametrics.md) | Differences between open source (community) and Enterprise versions of VictoriaMetrics |
| victoriametrics-cardinality-analysis | [victoriametrics-cardinality-analysis.md](references/victoriametrics-cardinality-analysis/victoriametrics-cardinality-analysis.md) | Analyze VictoriaMetrics time series cardinality to find optimization opportunities |
| victoriametrics-query | [victoriametrics-query.md](references/victoriametrics-query/victoriametrics-query.md) | Query VictoriaMetrics metrics via curl using PromQL/MetricsQL |
| victoriametrics-unused-metrics-analysis | [victoriametrics-unused-metrics-analysis.md](references/victoriametrics-unused-metrics-analysis/victoriametrics-unused-metrics-analysis.md) | Find unused and rarely-queried metrics in VictoriaMetrics |
| victoriatraces-query | [victoriatraces-query.md](references/victoriatraces-query/victoriatraces-query.md) | Query VictoriaTraces via curl using the Jaeger-compatible API |
| vllm | [vllm.md](references/vllm/vllm.md) | Comprehensive knowledge of vLLM for LLM inference and serving |
| vllm-kubernetes | [vllm-kubernetes.md](references/vllm-kubernetes/vllm-kubernetes.md) | Deploy vLLM (OpenAI-compatible LLM serving) on Kubernetes |
| vm-trace-analyzer | [vm-trace-analyzer.md](references/vm-trace-analyzer/vm-trace-analyzer.md) | Analyze VictoriaMetrics query trace JSON to diagnose slow queries |
| writing-mstest-tests | [SKILL.md](references/dotnet-test/skills/writing-mstest-tests/SKILL.md) | Best practices for writing MSTest 3.x/4.x unit tests |
| zig | [zig.md](references/zig/zig.md) | Up-to-date Zig programming language patterns for version 0.15.x |
| zig-raylib | [zig-raylib.md](references/zig-raylib/zig-raylib.md) | Zig bindings for raylib 5.5 game development library |
| zig-sdl3-bindings | [zig-sdl3-bindings.md](references/zig-sdl3-bindings/zig-sdl3-bindings.md) | Zig bindings for SDL3 multimedia library for cross-platform game development |
| kotlin-backend-jpa-entity-mapping | [kotlin-backend-jpa-entity-mapping.md](references/kotlin-backend-jpa-entity-mapping/kotlin-backend-jpa-entity-mapping.md) | Create or review JPA entities in Kotlin — diagnose N+1, LazyInitializationException, indexes, data class ORM bugs |
| kotlin-tooling-agp9-migration | [kotlin-tooling-agp9-migration.md](references/kotlin-tooling-agp9-migration/kotlin-tooling-agp9-migration.md) | Upgrade Kotlin Multiplatform projects to Android Gradle Plugin 9.0+ or fix KMP+AGP build failures |
| kotlin-tooling-cocoapods-spm-migration | [kotlin-tooling-cocoapods-spm-migration.md](references/kotlin-tooling-cocoapods-spm-migration/kotlin-tooling-cocoapods-spm-migration.md) | Migrate KMP project from CocoaPods to Swift Package Manager — pod() to swiftPackage(), cocoapods to swiftPMImport |
| kotlin-tooling-java-to-kotlin | [kotlin-tooling-java-to-kotlin.md](references/kotlin-tooling-java-to-kotlin/kotlin-tooling-java-to-kotlin.md) | Convert Java source files to idiomatic Kotlin with framework-aware conversion (Spring, Lombok, Hibernate, Jackson, etc.) |
| fido2-net-lib | [fido2-net-lib.md](references/fido2-net-lib/fido2-net-lib.md) | Fido2.Net also called fido2-net-lib library for FIDO2 authentication and WebAuthn integration in .NET |
| microsoft-docs | [microsoft-docs.md](references/microsoft-docs/microsoft-docs.md) | Understand Microsoft technologies by querying official documentation, (Azure, .NET, M365, Windows, Power Platform, etc.) |
| microsoft-skill-creator | [microsoft-skill-creator.md](references/microsoft-skill-creator/microsoft-skill-creator.md) | Create agent skills for Microsoft technologies using official documentation. Use whenever the user wants to build, generate, or scaffold a skill for any Microsoft technology (Azure, .NET, M365, VS Code, Bicep, etc.) |