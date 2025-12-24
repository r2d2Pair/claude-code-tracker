# Claude Code Tracker

Knowledge management for Claude Code - extract decisions, track progress, generate reports from conversations.

> Forked from [claude-conversation-extractor](https://github.com/ZeroSumQuant/claude-conversation-extractor)

## Features

### Current (from upstream)
- Extract conversations from `~/.claude/projects/` JSONL files
- Export to Markdown, JSON, HTML
- Search with smart/exact/regex/semantic modes
- Interactive terminal UI

### Planned
- **Decision Capture** - Auto-extract technical decisions with code linking
- **Knowledge Base** - Facts, conventions, gotchas in grep-friendly format
- **Progress Reports** - Activity metrics, topic analysis, milestones
- **Work Logs** - Timesheet-style reports, deliverable tracking

## Installation

```bash
pip install claude-code-tracker
```

Or install from source:

```bash
git clone https://github.com/r2d2Pair/claude-code-tracker.git
cd claude-code-tracker
pip install -e ".[dev]"
```

## Usage

```bash
# Interactive mode
claude-code-tracker
# or
cct

# List conversations
cct list

# Search
cct search "authentication"
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Lint
flake8 .
```

## License

MIT - See [LICENSE](LICENSE)

## Attribution

This project is forked from [claude-conversation-extractor](https://github.com/ZeroSumQuant/claude-conversation-extractor) by Dustin Kirby.
