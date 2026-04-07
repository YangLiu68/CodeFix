# CLI Coding Agent – Development Plan

## 1. Project Goal

Build a **CLI-based AI coding agent** that can:

- Understand an existing codebase
- Retrieve relevant files
- Plan modifications
- Apply safe code edits via patches
- Execute developer tools (tests, builds, commands)

The goal is to create a **mini version of tools like Claude Code / Aider / Cursor CLI**.

------

# 2. Core Features

## Codebase Understanding

- Repository scanning
- File tree mapping
- Symbol extraction
- Fast code search

## Agent Reasoning

- Task planning
- Multi-step reasoning
- Tool usage

## Safe Code Editing

- Diff-based patch editing
- Multi-file modifications
- Human confirmation before apply

## Developer Tool Integration

- Run tests
- Execute shell commands
- Search code
- Git integration

## Interactive CLI

- Chat-like terminal interface
- Streaming responses
- Rich formatting

------

# 3. System Architecture

```
                CLI Interface
                      │
                      ▼
                Agent Controller
                      │
          ┌───────────┼───────────┐
          │           │           │
      Planner     Context      Memory
                    Builder
          │
          ▼
        Tool System
          │
   ┌──────┼──────────┬─────────┐
   │      │          │         │
read_file search   write    run_cmd
           code     patch
```

------

# 4. Technology Stack

## CLI Layer

- Python
- Typer
- Rich
- PromptToolkit

## AI / Agent

- OpenAI / Anthropic
- Tool calling
- Streaming responses

## Code Understanding

- tree-sitter (AST parsing)
- ripgrep (fast search)

## Storage

- SQLite (local memory)
- optional vector DB (FAISS)

## Dev Tools

- Git
- pytest / npm test integration

------

# 5. Repository Structure

```
cli-coding-agent/

agent/
    controller.py
    planner.py
    executor.py

context/
    indexer.py
    retriever.py
    repo_map.py

tools/
    read_file.py
    write_patch.py
    search_code.py
    run_command.py

editing/
    patch_parser.py
    patch_apply.py

cli/
    main.py
    chat_ui.py

memory/
    session_memory.py

tests/

README.md
PLAN.md
```

------

# 6. Development Phases

## Phase 1 – CLI Interface

Goal: basic interactive terminal.

Features:

- start agent
- prompt input
- streaming response

Example:

```
$ agent

Agent ready.

>
```

Deliverables:

- CLI chat loop
- LLM connection
- streaming output

------

## Phase 2 – Tool System

Goal: enable agent tool usage.

Tools:

- read_file
- search_code
- write_file
- run_command

Example tool call:

```
tool: read_file
file: server/auth.go
```

Deliverables:

- tool registry
- tool execution layer

------

## Phase 3 – Codebase Indexing

Goal: understand repository structure.

Features:

- repo tree
- file metadata
- symbol extraction

Tools:

- tree-sitter
- ripgrep

Deliverables:

- repo map
- fast file lookup

------

## Phase 4 – Context Retrieval

Goal: provide relevant code to LLM.

Pipeline:

```
user query
   ↓
code search
   ↓
relevant files
   ↓
build prompt context
```

Deliverables:

- context builder
- token-aware truncation

------

## Phase 5 – Planning Agent

Goal: multi-step reasoning before editing.

Example:

```
Plan:

1. create jwt middleware
2. modify login handler
3. update router
4. add tests
```

Deliverables:

- planning prompt
- structured plan output

------

## Phase 6 – Patch-Based Editing

Goal: safe automated code modification.

Workflow:

```
LLM produces diff patch
        ↓
validate patch
        ↓
apply patch
```

Example patch:

```
+ func JWTMiddleware() gin.HandlerFunc {
+   ...
+ }
```

Deliverables:

- diff parser
- patch applier

------

## Phase 7 – Execution Loop

Goal: full agent cycle.

Loop:

```
observe
plan
tool_call
observe
edit
verify
```

Deliverables:

- autonomous task execution
- retry on failure

------

# 7. Advanced Features

## Repo Map

Maintain structured metadata:

```
file
symbols
imports
dependencies
```

Used to improve retrieval.

------

## Autonomous Fix Mode

Command:

```
agent fix tests
```

Agent will:

```
run tests
detect failure
modify code
retry
```

------

## Git Integration

Agent can:

```
create branch
commit changes
generate PR message
```

------

## Multi-file Refactoring

Example task:

```
add authentication system
```

Agent modifies:

```
router.go
auth.go
middleware.go
```

------

# 8. Milestones

Week 1

- CLI interface
- LLM connection

Week 2

- tool system
- file operations

Week 3

- repo indexing
- code search

Week 4

- planning agent
- patch editing

Week 5

- autonomous loop
- error handling

Week 6

- git integration
- advanced context retrieval

------

# 9. Evaluation Metrics

Measure system capability by:

- multi-file edit success rate
- tool usage accuracy
- patch correctness
- test pass rate after edits

------

# 10. Stretch Goals

- local model support
- code embedding search
- language server integration
- distributed agent workers

------

# Final Goal

A **developer-grade CLI coding agent** capable of autonomously reading, editing, and improving real-world codebases.