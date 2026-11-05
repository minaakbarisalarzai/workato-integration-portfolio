
# Workato Integration Engineering Portfolio

**Mina Akbari | Software Engineer — Integrations & Automation**

**Workato · Ruby · Python · REST APIs · Custom Connectors · Workflow Automation**

A collection of integration engineering projects demonstrating my experience building Workato automations, developing custom connectors, optimizing API integrations, and designing reliable, maintainable workflows.

## Projects

### 01 — Connection Failure Detection & Automated Job Recovery

**[View Project](projects/01-connection-failure-recovery/)**

Designed, built, and used a Workato recipe to streamline the investigation and recovery of failed integration jobs.

**Technical Highlights**
- Scheduled recipe discovery and connector-based connection lookup.
- Job-history searches to identify failed executions within a specified time window.
- Automated job reruns using Workato RecipeOps actions.
- Error handling using Monitor and Do Not Retry.
- Recovery activity logging through Google Sheets.

**Outcome:** Consolidated recipe discovery, failed-job inspection, rerun initiation, and recovery logging into one Workato automation.

### 02 — Workato Recipe Optimization

**[View Project](projects/02-recipe-optimization/)**

Two before-and-after case studies demonstrating how to reduce Workato task consumption, simplify workflows, and improve maintainability.

**Case Study 1 — API Consolidation**
- Reduced configured workflow actions from **23 to 2 (91.3%)**.
- Reduced observed Workato task consumption from **5 to 2 (60%)**.
- Consolidated five REST API requests and supporting request-handling logic into Python.
- Both baseline and optimized executions completed successfully.

**Case Study 2 — Native Formula Optimization**
- Replaced a Python JSON-to-Base64 encoder with Workato's native `to_json.encode_base64` formula.
- Reduced configured Python actions from **2 to 1 (50%)**.
- Verified matching Base64 values in Workato execution results.

**Outcome:** Demonstrated measurable task reductions, simpler recipe designs, and improved task-based resource efficiency.

### 03 — GitHub Issue Explorer | Custom Workato Connector

**[View Project](projects/03-custom-connector/)**

Developed a custom Workato connector using Ruby, the Workato Connector SDK, and the GitHub REST API.

**Technical Highlights**
- Fine-grained GitHub token authentication.
- Dynamic repository and label picklists.
- Configurable issue retrieval, filtering, and sorting.
- Link-header pagination.
- Input validation and descriptive API error handling.
- Bounded retries for supported transient failures.
- Automated Ruby tests and live Workato demonstrations.

**Testing:** 19 unit tests and 59 assertions passing. Core functionality was successfully tested in Workato; additional revisions require live verification.

### 04 — Embedded Integration Architecture

**[View Project](projects/04-embedded-integration/)**

An embedded integration architecture project exploring how Workato capabilities can be incorporated into an application.

**Technical Focus**
- API-driven Workato workspace provisioning.
- Secure JWT-based embedding.
- Integration workspace and permission management.
- Automated workspace configuration.
- Reusable integration templates and architecture.

**Status:** Reference architecture and implementation documentation.

---

## Technical Skills

| Category | Technologies & Capabilities |
|---|---|
| Integration Platforms | Workato, Workato Connector SDK, RecipeOps |
| Programming Languages | Ruby, Python |
| API Integration | REST APIs, HTTP, JSON, Authentication, Pagination |
| Workflow Engineering | Recipe Design, Task Optimization, Error Handling, Logging |
| Testing | Ruby Minitest, Python Unit Tests, API Testing |
| Development Tools | Git, GitHub |

## Engineering Approach

I focus on building integrations that are:

- **Reliable:** Clear error handling, validation, and recovery workflows.
- **Efficient:** Reduced task consumption and unnecessary actions.
- **Maintainable:** Reusable logic, clear documentation, and platform-native solutions.
- **Secure:** Least-privilege authentication and careful handling of sensitive data.
- **Testable:** Reproducible examples, automated tests, and documented execution results.

## Repository Structure

```text
workato-integration-portfolio/
├── README.md
├── SECURITY.md
├── docs/
│   └── ROADMAP.md
└── projects/
    ├── 01-connection-failure-recovery/
    ├── 02-recipe-optimization/
    ├── 03-custom-connector/
    └── 04-embedded-integration/
```

## About Me

I'm a software engineer specializing in **Workato integrations, custom connector development, API automation, and workflow optimization**.

My experience includes building Ruby-based Workato connectors, developing integrations with external APIs, designing operational automations, and improving integration efficiency using Python and Workato-native functionality.

This portfolio demonstrates my technical approach through practical implementations, testing, documentation, and Workato demonstrations.

---

**Developed and maintained by Mina Akbari.**

*Portfolio materials are shared for demonstration purposes.
