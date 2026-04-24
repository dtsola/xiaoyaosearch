# Claude Command: Onboard

This command acts as an expert technical mentor to help you rapidly understand a new codebase, generating a comprehensive "Survival Guide" for the project.

## Usage

To analyze the project, run:
```
/onboard
```

Or with specific focus:
```
/onboard --focus "auth flow"
```

## What This Command Does

1. **Scans Context**: Automatically reads key configuration files to determine the tech stack:
   - `package.json` / `go.mod` / `pom.xml` / `requirements.txt` (Dependencies)
   - `README.md` (Documentation)
   - `docker-compose.yml` / `Dockerfile` (Infrastructure)
   - `.gitignore` (Project structure hints)
2. **Maps Architecture**: Analyzes the directory structure (`src`, `app`, `lib`, etc.) to understand the architectural pattern (MVC, DDD, Hexagonal, etc.).
3. **Traces Core Paths**: Identifies the entry points (e.g., `index.js`, `main.go`, `App.tsx`) and traces a theoretical request from API to Database.
4. **Synthesizes Report**: Generates a structured Markdown report covering Business, Architecture, Code Navigation, and Setup.

## Output Structure: The Survival Guide

The command will generate a report with the following structure:

### 1. 🔭 The Big Picture (Business & Architecture)
- **One-Liner**: What does this project actually do?
- **Tech Stack**: Core languages, frameworks, and *why* they seem to be used.
- **Architecture Diagram**: A `mermaid` flowchart showing the high-level system design or data flow.

### 2. 🗺️ Map of the Territory (Navigation)
- **Key Directories**: The top 3-5 most important folders and what lives inside.
- **Logic Location**: Where does the business logic live? (Controllers? Services? Domain?)
- **Entry Points**: Where does the code start running?

### 3. 🕵️ Core Path Analysis
- **Trace**: A step-by-step list tracking a core feature (e.g., Login or Create Order) from the HTTP Request down to the Database Query.
- **Data Flow**: `Function A` -> `Function B` -> `Database Table`.

### 4. 🚀 Setup & Run
- **Quick Start**: Summarized commands to get it running (based on `package.json` scripts or Docker).
- **Pitfalls**: 2 predicted issues a new developer might face (e.g., missing ENV variables, version mismatches).

### 5. ⚠️ Risks & Debt
- **Code Smells**: Any obvious hardcoded values, massive functions, or lack of tests.
- **First Task**: A recommendation for a simple module to read first to get started.

## Best Practices for Onboarding

- **Run from Root**: Execute this command from the root directory of the project for the best context.
- **Verify Docs**: Compare the generated "Setup" instructions with the actual `README.md` to find discrepancies.
- **Interactive Follow-up**: After the report is generated, ask specific questions like:
  - "Explain the `authMiddleware` function in detail."
  - "Generate a sequence diagram for the payment flow."

## Command Options

- `--focus [topic]`: Instead of a general overview, deep dive into a specific domain (e.g., `/onboard --focus "payment system"`).
- `--deep`: Performs a more granular analysis of utility functions and shared libraries.

## Important Notes

- The analysis is based on the provided file context. If key files are missing, the command will infer based on standard patterns.
- The Mermaid diagrams generated are high-level representations to help mental modeling.
- This command does not execute code; it only reads and analyzes static code and configuration.