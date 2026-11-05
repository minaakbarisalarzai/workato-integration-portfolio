
# Workato Integration Engineering Portfolio

**Mina Akbari | Software Engineer — Integrations & Automation**

Workato · Ruby · Python · REST APIs · Custom Connectors · Workflow Automation

A collection of integration engineering projects showcasing my experience building Workato automations, developing custom connectors, optimizing API integrations, and designing reliable integration workflows.

## Featured Projects

### 01 — Workato Connection Failure Detection & Automated Job Recovery

**[View Project](projects/01-connection-failure-recovery/)**

Designed and used a Workato automation to streamline the investigation and recovery of failed integration jobs.

**Technical Highlights**
- Scheduled recipe discovery and connection lookup.
- Automated job-history searches and failed-job identification.
- Job rerun orchestration using Workato's RecipeOps actions.
- Error handling with Monitor and Do Not Retry.
- Recovery activity logging through Google Sheets.

**Outcome:** Consolidated previously manual recovery activities into a structured Workato workflow.

### 02 — Workato Recipe Optimization

**[View Project](projects/02-recipe-optimization/)**

Two before-and-after case studies demonstrating how to reduce Workato task consumption and simplify integration workflows.

**Case Study 1 — API Consolidation**
- Reduced configured workflow actions from **23 to 2 (91.3%)**.
- Reduced observed Workato task consumption from **5 to 2 (60%)**.
- Consolidated five REST API requests and supporting logic into Python.
- Both compared executions completed successfully.

**Case Study 2 — Native Formula Optimization**
- Replaced a Python JSON-to-Base64 encoder with `to_json.encode_base64`.
- Reduced configured Python actions from **2 to 1 (50%)**.
- Verified matching Base64 values in Workato executions.

**Outcome:** Demonstrated task efficiency, simpler recipe design, and reduced task-based resource consumption.

### 03 — GitHub Issue Explorer | Custom Workato Connector

**[View Project](projects/03-custom-connector/)**

Built a custom Workato connector in Ruby using the Workato Connector SDK and GitHub REST API.

**Technical Highlights**
- Fine-grained token authentication.
- Dynamic repository and label picklists.
- Issue retrieval, filtering, and sorting.
- Link-header pagination.
- Input validation, descriptive errors, and retry handling.
- Automated Ruby tests and live Workato demonstrations.

**Testing:** 19 unit tests and 59 assertions passing, with core functionality tested in Workato. Additional changes in the revised connector require live verification.

### 04 — Embedded Integration Architecture

**[View Project](projects/04-embedded-integration/)**

Architecture and reference implementation for embedding integration capabilities into an application.

**Technical Focus**
- Workato workspace provisioning.
- API-driven integration setup.
- Secure JWT-based embedding.
- Workspace access and permission management.
- Integration templates and automation architecture.

**Status:** Reference project; implementation and documentation scope may evolve.

---

## Technical Skills

| Area | Technologies & Capabilities |
|---|---|
| Integration Platforms | Workato, Workato Connector SDK, RecipeOps |
| Programming | Ruby, Python |
| API Development | REST APIs, HTTP, JSON, Authentication, Pagination |
| Automation | Recipe Design, Workflow Optimization, Error Handling |
| Testing | Ruby Minitest, Python Unit Tests, API Testing |
| Tools | Git, GitHub |

## Engineering Approach

I focus on building integrations that are:

- **Reliable:** Clear error handling, validation, and recovery paths.
- **Efficient:** Reduced task consumption and unnecessary actions.
- **Maintainable:** Reusable logic and appropriate use of native Workato features.
- **Secure:** Least-privilege access and careful handling of credentials.
- **Testable:** Documented behavior, reproducible examples, and meaningful validation.

## Repository Structure

```text
workato-integration-portfolio/
├── README.md
├── SECURITY.md
├── docs/
└── projects/
    ├── 01-connection-failure-recovery/
    ├── 02-recipe-optimization/
    ├── 03-custom-connector/
    └── 04-embedded-integration/
```

## About Me

I'm a software engineer specializing in **Workato integrations, custom connector development, API automation, and workflow optimization**.

My experience includes developing Ruby-based Workato connectors, building integrations with external APIs, automating operational workflows, and improving integration efficiency through Python and platform-native capabilities.

This portfolio highlights practical engineering work through implementations, testing, technical documentation, and Workato demonstrations.

---

**Developed and maintained by Mina Akbari.**

*Portfolio examples are intended for demonstration purposes.
