#!/usr/bin/env python3
"""
Command-line interface for Claude Code Tracker.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from claude_code_tracker.core.extractor import ClaudeConversationExtractor
except ImportError:
    from extract_claude_logs import ClaudeConversationExtractor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Tracker - Extract and manage Claude Code conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    # List all available sessions
  %(prog)s --extract 1               # Extract the most recent session
  %(prog)s --extract 1,3,5           # Extract specific sessions
  %(prog)s --recent 5                # Extract 5 most recent sessions
  %(prog)s --all                     # Extract all sessions
  %(prog)s --output ~/my-logs        # Specify output directory
  %(prog)s --search "python error"   # Search conversations
  %(prog)s --search-regex "import.*" # Search with regex
  %(prog)s --format json --all       # Export all as JSON
  %(prog)s --format html --extract 1 # Export session 1 as HTML
  %(prog)s --detailed --extract 1    # Include tool use & system messages
        """,
    )
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument(
        "--extract",
        type=str,
        help="Extract specific session(s) by number (comma-separated)",
    )
    parser.add_argument(
        "--all", "--logs", action="store_true", help="Extract all sessions"
    )
    parser.add_argument(
        "--recent", type=int, help="Extract N most recent sessions", default=0
    )
    parser.add_argument(
        "--output", type=str, help="Output directory for markdown files"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit for --list command (default: show all)",
        default=None,
    )
    parser.add_argument(
        "--interactive",
        "-i",
        "--start",
        "-s",
        action="store_true",
        help="Launch interactive UI for easy extraction",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export mode: 'logs' for interactive UI",
    )

    # Search arguments
    parser.add_argument(
        "--search", type=str, help="Search conversations for text (smart search)"
    )
    parser.add_argument(
        "--search-regex", type=str, help="Search conversations using regex pattern"
    )
    parser.add_argument(
        "--search-date-from", type=str, help="Filter search from date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--search-date-to", type=str, help="Filter search to date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--search-speaker",
        choices=["human", "assistant", "both"],
        default="both",
        help="Filter search by speaker",
    )
    parser.add_argument(
        "--case-sensitive", action="store_true", help="Make search case-sensitive"
    )

    # Export format arguments
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "html"],
        default="markdown",
        help="Output format for exported conversations (default: markdown)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Include tool use, MCP responses, and system messages in export",
    )

    args = parser.parse_args()

    # Handle interactive mode
    if args.interactive or (args.export and args.export.lower() == "logs"):
        launch_interactive()
        return

    # Initialize extractor with optional output directory
    extractor = ClaudeConversationExtractor(args.output)

    # Handle search mode
    if args.search or args.search_regex:
        _handle_search(args, extractor)
        return

    # Default action is to list sessions
    if args.list or (
        not args.extract
        and not args.all
        and not args.recent
        and not args.search
        and not args.search_regex
    ):
        sessions = extractor.list_recent_sessions(args.limit)

        if sessions and not args.list:
            print("\nTo extract conversations:")
            print("  cct --extract <number>      # Extract specific session")
            print("  cct --recent 5              # Extract 5 most recent")
            print("  cct --all                   # Extract all sessions")

    elif args.extract:
        sessions = extractor.find_sessions()

        # Parse comma-separated indices
        indices = []
        for num in args.extract.split(","):
            try:
                idx = int(num.strip()) - 1  # Convert to 0-based index
                indices.append(idx)
            except ValueError:
                print(f"❌ Invalid session number: {num}")
                continue

        if indices:
            print(f"\n📤 Extracting {len(indices)} session(s) as {args.format.upper()}...")
            if args.detailed:
                print("📋 Including detailed tool use and system messages")
            success, total = extractor.extract_multiple(
                sessions, indices, format=args.format, detailed=args.detailed
            )
            print(f"\n✅ Successfully extracted {success}/{total} sessions")

    elif args.recent:
        sessions = extractor.find_sessions()
        limit = min(args.recent, len(sessions))
        print(f"\n📤 Extracting {limit} most recent sessions as {args.format.upper()}...")
        if args.detailed:
            print("📋 Including detailed tool use and system messages")

        indices = list(range(limit))
        success, total = extractor.extract_multiple(
            sessions, indices, format=args.format, detailed=args.detailed
        )
        print(f"\n✅ Successfully extracted {success}/{total} sessions")

    elif args.all:
        sessions = extractor.find_sessions()
        print(f"\n📤 Extracting all {len(sessions)} sessions as {args.format.upper()}...")
        if args.detailed:
            print("📋 Including detailed tool use and system messages")

        indices = list(range(len(sessions)))
        success, total = extractor.extract_multiple(
            sessions, indices, format=args.format, detailed=args.detailed
        )
        print(f"\n✅ Successfully extracted {success}/{total} sessions")


def _handle_search(args, extractor):
    """Handle search mode."""
    try:
        from claude_code_tracker.search.searcher import ConversationSearcher
    except ImportError:
        from search_conversations import ConversationSearcher

    searcher = ConversationSearcher()

    # Determine search mode and query
    if args.search_regex:
        query = args.search_regex
        mode = "regex"
    else:
        query = args.search
        mode = "smart"

    # Parse date filters
    date_from = None
    date_to = None
    if args.search_date_from:
        try:
            date_from = datetime.strptime(args.search_date_from, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid date format: {args.search_date_from}")
            return

    if args.search_date_to:
        try:
            date_to = datetime.strptime(args.search_date_to, "%Y-%m-%d")
        except ValueError:
            print(f"❌ Invalid date format: {args.search_date_to}")
            return

    # Speaker filter
    speaker_filter = None if args.search_speaker == "both" else args.search_speaker

    # Perform search
    print(f"🔍 Searching for: {query}")
    results = searcher.search(
        query=query,
        mode=mode,
        date_from=date_from,
        date_to=date_to,
        speaker_filter=speaker_filter,
        case_sensitive=args.case_sensitive,
        max_results=30,
    )

    if not results:
        print("❌ No matches found.")
        return

    print(f"\n✅ Found {len(results)} matches across conversations:")

    # Group and display results
    results_by_file = {}
    for result in results:
        if result.file_path not in results_by_file:
            results_by_file[result.file_path] = []
        results_by_file[result.file_path].append(result)

    # Store file paths for potential viewing
    file_paths_list = []
    for file_path, file_results in results_by_file.items():
        file_paths_list.append(file_path)
        print(
            f"\n{len(file_paths_list)}. 📄 {file_path.parent.name} ({len(file_results)} matches)"
        )
        # Show first match preview
        first = file_results[0]
        print(f"   {first.speaker}: {first.matched_content[:100]}...")

    # Offer to view conversations
    if file_paths_list:
        print("\n" + "=" * 60)
        try:
            view_choice = input(
                f"\nView a conversation? Enter number (1-{len(file_paths_list)}) or press Enter to skip: "
            ).strip()

            if view_choice.isdigit():
                view_num = int(view_choice)
                if 1 <= view_num <= len(file_paths_list):
                    selected_path = file_paths_list[view_num - 1]
                    extractor.display_conversation(selected_path, detailed=args.detailed)

                    # Offer to extract after viewing
                    extract_choice = (
                        input("\n📤 Extract this conversation? (y/N): ").strip().lower()
                    )
                    if extract_choice == "y":
                        conversation = extractor.extract_conversation(
                            selected_path, detailed=args.detailed
                        )
                        if conversation:
                            session_id = selected_path.stem
                            output = extractor.save_conversation(
                                conversation, session_id, format=args.format
                            )
                            print(f"✅ Saved: {output.name}")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Cancelled")


def launch_interactive():
    """Launch the interactive UI directly, or handle search if specified."""
    # If no arguments provided (or just the command itself), launch interactive UI
    if len(sys.argv) <= 1:
        try:
            from claude_code_tracker.ui.interactive import main as interactive_main
        except ImportError:
            from interactive_ui import main as interactive_main
        interactive_main()
    # Check if 'search' was passed as an argument
    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        try:
            from claude_code_tracker.search.realtime import (
                RealTimeSearch,
                create_smart_searcher,
            )
            from claude_code_tracker.search.searcher import ConversationSearcher
        except ImportError:
            from realtime_search import RealTimeSearch, create_smart_searcher
            from search_conversations import ConversationSearcher

        # Initialize components
        extractor = ClaudeConversationExtractor()
        searcher = ConversationSearcher()
        smart_searcher = create_smart_searcher(searcher)

        # Run search
        rts = RealTimeSearch(smart_searcher, extractor)
        selected_file = rts.run()

        if selected_file:
            # View the selected conversation
            extractor.display_conversation(selected_file)

            # Offer to extract
            try:
                extract_choice = (
                    input("\n📤 Extract this conversation? (y/N): ").strip().lower()
                )
                if extract_choice == "y":
                    conversation = extractor.extract_conversation(selected_file)
                    if conversation:
                        session_id = selected_file.stem
                        output = extractor.save_as_markdown(conversation, session_id)
                        print(f"✅ Saved: {output.name}")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Cancelled")
    else:
        # If other arguments are provided, run the normal CLI
        main()


if __name__ == "__main__":
    main()
