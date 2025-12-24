"""
Claude Code Tracker - Knowledge management for Claude Code conversations.

Extract decisions, track progress, generate reports from Claude Code sessions.
"""

__version__ = "0.1.0"

from claude_code_tracker.core.extractor import ClaudeConversationExtractor

__all__ = ["ClaudeConversationExtractor", "__version__"]
