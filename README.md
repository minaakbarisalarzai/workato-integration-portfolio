# Workato Integration Engineering Portfolio

**Automation · Custom Connectors · API Integrations · Workflow Design**

Original, independently developed examples demonstrating integration-engineering patterns with Workato, Ruby, Python, and REST APIs.

> **Status:** Repository initialized. Projects will be published incrementally as they are implemented and tested.

## Projects

| Project | Focus | Status |
| --- | --- | --- |
| [01 · Loop Control Patterns](projects/01-loop-control/) | Conditional iteration, skip-and-continue patterns, edge cases | Planned |
| [02 · Recipe Optimization](projects/02-recipe-optimization/) | Replacing unnecessary scripting steps with supported Workato formulas | Planned |
| [03 · Custom Connector](projects/03-custom-connector/) | Ruby SDK connector for a public API, authentication, actions, pagination, testing | Planned |
| [04 · Embedded Integration Architecture](projects/04-embedded-integration/) | Reference architecture for provisioning, secure embedding, and permissions | Planned |

## Engineering principles

- **Correctness first:** Document assumptions, edge cases, and reproducible tests.
- **Pragmatic design:** Use platform-native features where sufficient; write code for genuine gaps.
- **Maintainability:** Keep recipes readable and field mappings clear.
- **Resilience:** Consider authentication, pagination, retries, rate limiting, and actionable errors.
- **Security:** Use synthetic data; never commit tokens, customer information, or proprietary material.

## Technology

`Workato` · `Ruby` · `Workato Connector SDK` · `Python` · `REST APIs` · `JSON`

## How to explore

Each finished project will include a problem statement, design choices, independent code or reproducible recipe, synthetic input/output examples, setup/test instructions, limitations, and lessons learned. See [Roadmap](docs/ROADMAP.md).

## Confidentiality and attribution

All examples are independently authored demonstrations using public APIs and synthetic data. This repository does **not** contain employer or customer source code, credentials, internal configurations, or proprietary recipes. These demos are not copies of production systems.
