# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code Tracker - Knowledge management for Claude Code conversations. Extracts decisions, tracks progress, generates reports.

Forked from [claude-conversation-extractor](https://github.com/ZeroSumQuant/claude-conversation-extractor).

## Common Commands

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest
pytest tests/test_extractor.py -v  # Single file

# Format & lint
black .
isort .
flake8 . --max-line-length=100

# Run the app
claude-code-tracker  # or: cct
```

## Architecture

### Source Files (src/)

- **extract_claude_logs.py** - Core extractor: finds JSONL in `~/.claude/projects/`, parses, exports to MD/JSON/HTML
- **interactive_ui.py** - Terminal UI with menus and real-time search
- **search_conversations.py** - Search engine with smart/exact/regex/semantic modes
- **realtime_search.py** - Live search with cross-platform keyboard handling
- **search_cli.py** - CLI wrapper for search

### Entry Points

- `claude-code-tracker` / `cct` → `extract_claude_logs:launch_interactive`

### Key Data Flow

1. `ClaudeConversationExtractor.find_sessions()` - finds `*.jsonl` in `~/.claude/projects/`
2. `extract_conversation()` - parses JSONL, extracts user/assistant messages
3. `save_as_markdown/json/html()` - outputs conversation

## Code Style

- Black formatter, 100 char line length
- isort for imports
- Type hints encouraged
