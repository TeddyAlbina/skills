---
name: unit-and-integration-tests-discovery
description: |
  Analyze any codebase to discover gaps in test coverage and add high-value, meaningful unit tests and integration tests.
  Use this skill whenever the task involves:
  • Improving test coverage
  • Writing tests for new features, refactors, or bug fixes
  • Adding tests before/after code changes
  • Addressing low coverage in critical modules
  • Ensuring regression safety
  Do NOT use for general code writing unless tests are explicitly requested.
version: "1.0"
---

# Add Meaningful Unit & Integration Tests

## Overview
This skill equips the AI agent to systematically explore a project, identify high-impact areas lacking tests, and add **meaningful** unit tests (isolated logic) and integration tests (component interactions) that actually improve reliability, prevent regressions, and document behavior.

## When to Use This Skill
- User asks to "add tests", "improve coverage", "write unit/integration tests", or "add tests for this feature"
- Before or after implementing/refactoring code
- Coverage reports show < 80% in core modules
- Bug reports reveal missing test cases
- Recent git changes have no corresponding tests
- Preparing a PR or code review

**When NOT to use:**
- Pure documentation or config changes with no behavioral impact
- Trivial getters/setters (unless they contain logic)
- When the user explicitly says "no tests needed"

## Core Procedure (Follow in Order)

### 1. Project & Testing Framework Discovery
- Identify language and test framework (`pytest`, `Jest`, `JUnit`, `Go test`, `rspec`, `vitest`, `C#`, etc.)
- Locate test directories
- Read any existing `AGENTS.md`, `.github/`, or test config files for conventions
- Run the full test suite once to confirm it passes

### 2. Coverage Analysis & Gap Discovery
- Generate a coverage report using the project's native tools:
  - Python: `coverage run -m pytest && coverage report --show-missing`
  - JavaScript/TypeScript: `npm test -- --coverage`
  - Other languages: use the built-in coverage command
- Identify:
  - Files/functions with 0% or low coverage
  - Recently changed files (`git log --since="1 month" --name-only`)
  - Core business logic, public APIs, error paths, complex conditionals

### 3. Prioritize Meaningful Test Targets (High-Value First)
Prioritize in this order:
1. **Critical paths** — business logic, calculations, security, data validation
2. **Public interfaces** — APIs, exported functions, CLI commands
3. **Integration points** — DB, external services, file I/O, message queues
4. **Complex or recently changed code**
5. **Edge cases & error handling** (null/empty, invalid input, timeouts, permissions)

Avoid low-value tests (trivial one-liners).

### 4. Test Design Principles (Always Follow)
- **Unit tests**: Isolate the unit (mock dependencies)
- **Integration tests**: Test real interactions where valuable (use test DBs, in-memory services, testcontainers)
- Use the project's naming and structure conventions
- Follow **Arrange → Act → Assert** (or Given/When/Then)
- Cover:
  - Happy path
  - Edge cases & boundary values
  - Error conditions
  - Parameterized tests for multiple scenarios
- Name tests descriptively: `test_process_order_creates_invoice_when_valid()` or `it("returns 400 when title is empty")`
- Prefer **state-based** assertions over interaction-based mocks when possible
- Keep tests fast, independent, and deterministic

### 5. Implementation Steps
1. Write the test file (or add to existing) in the correct location
2. Run **only** the new tests to verify they fail first (if applicable) then pass
3. Re-run full coverage to confirm meaningful improvement
4. Run the entire test suite to ensure no regressions
5. If tests are flaky, fix immediately

### 6. Final Validation & Documentation
- Confirm coverage increased in the targeted areas
- Add a short comment or PR description explaining what behavior is now protected
- Suggest next highest-value tests if more are needed

## Tools & Commands You May Use
- Test runner + coverage tool of the project
- `git log`, `git blame`, `grep`, `rg` (ripgrep) for code search
- Language-specific static analysis if available
- Project linter/formatter on new test files

## Common Pitfalls to Avoid
- Over-mocking that makes tests brittle
- Testing implementation details instead of behavior
- Writing tests that duplicate production code logic
- Creating slow or flaky integration tests
- Adding tests for obvious getters/setters while core logic remains untested

## Example Usage Flow (for a Python project)
```bash
# 1. Discover & run coverage
coverage run -m pytest && coverage report

# 2. Identify gap → e.g. src/orders.py:process_order() has 12% coverage

# 3. Agent writes tests/test_orders.py with:
#    - test_process_order_happy_path
#    - test_process_order_rejects_invalid_amount
#    - test_process_order_handles_db_error (integration)
```

This skill pairs perfectly with TDD, refactoring, or code-review skills.

**Pro tip:** When in doubt, ask the user "Should I focus on unit tests, integration tests, or both for this module?" before writing.