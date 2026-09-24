#!/usr/bin/env python3

import os
import sys
import sqlite3
import random
from datetime import datetime
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

NOTES_DIRECTORY = Path(
    os.environ.get(
        "QD_NOTES_DIRECTORY",
        os.path.expanduser("~/.quickdrop")
    )
).expanduser()

BACKUP_DIRECTORY = Path(
    os.environ.get(
        "QD_BACKUP_DIRECTORY",
        str(NOTES_DIRECTORY / "backups")
    )
).expanduser()

DATABASE_PATH = NOTES_DIRECTORY / "quickdrop.db"


# ============================================================
# Messages
# ============================================================

SUCCESS_MESSAGES = [
    "🔥 Nice! One less thing to worry about.",
    "🚀 Done! Keep the momentum going.",
    "✓ Great work! That's another one off the list.",
    "💪 Completed! You're making progress.",
    "🔥 Nice one! Keep going.",
    "✓ Task crushed.",
    "🚀 Good job — progress is progress.",
]


# ============================================================
# Database
# ============================================================

def connect_db():
    """Open the database and automatically upgrade old schemas."""

    NOTES_DIRECTORY.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Create the original table if this is a brand-new database.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Database migration:
    #
    # Older QuickDrop versions don't have completed_at.
    # Add it automatically instead of destroying/recreating
    # the database.
    # --------------------------------------------------------

    columns = conn.execute(
        "PRAGMA table_info(notes)"
    ).fetchall()

    column_names = {
        column[1]
        for column in columns
    }

    if "completed_at" not in column_names:
        conn.execute("""
            ALTER TABLE notes
            ADD COLUMN completed_at TEXT
        """)

    conn.commit()

    return conn


# ============================================================
# Helpers
# ============================================================

def now():
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def pretty_date(timestamp):
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(timestamp)


def motivational_message():
    return random.choice(SUCCESS_MESSAGES)


def print_notes(rows):
    if not rows:
        print("No notes found.")
        return

    print("ID | Date/Time         | Note")
    print("-" * 80)

    for note_id, created_at, text in rows:
        print(
            f"{note_id} | "
            f"{pretty_date(created_at):16} | "
            f"{text}"
        )


# ============================================================
# Save
# ============================================================

def save_note(text):
    text = text.strip()

    if not text:
        print("Error: note cannot be empty.")
        return 1

    try:
        with connect_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO notes (text, created_at)
                VALUES (?, ?)
                """,
                (text, now())
            )

            note_id = cursor.lastrowid

        print(f"✓ Saved #{note_id}")
        return 0

    except sqlite3.Error as exc:
        print(f"Error saving note: {exc}", file=sys.stderr)
        return 1


# ============================================================
# List unfinished
# ============================================================

def list_notes():
    try:
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, text
                FROM notes
                WHERE completed_at IS NULL
                ORDER BY id DESC
                """
            ).fetchall()

            remaining = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NULL
                """
            ).fetchone()[0]

        if not rows:
            print("✓ No unfinished notes.")
            print("You're all caught up! 🎉")
            return 0

        print_notes(rows)
        print()
        print(f"{remaining} unfinished note(s).")

        return 0

    except sqlite3.Error as exc:
        print(f"Error reading notes: {exc}", file=sys.stderr)
        return 1


# ============================================================
# Recent
# ============================================================

def recent_notes(limit=5):
    try:
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, text
                FROM notes
                WHERE completed_at IS NULL
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()

            remaining = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NULL
                """
            ).fetchone()[0]

        print("QuickDrop — recent tasks")
        print("-" * 80)

        if not rows:
            print("✓ Nothing pending.")
            print("You're all caught up! 🎉")
            return 0

        print_notes(rows)
        print()

        if remaining > limit:
            print(f"{remaining} unfinished notes total.")

        return 0

    except sqlite3.Error as exc:
        print(
            f"Error reading recent notes: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# Search
# ============================================================

def search_notes(term):
    term = term.strip()

    if not term:
        print("Error: search term cannot be empty.")
        return 1

    try:
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, text
                FROM notes
                WHERE completed_at IS NULL
                  AND text LIKE ? COLLATE NOCASE
                ORDER BY id DESC
                """,
                (f"%{term}%",)
            ).fetchall()

        if not rows:
            print(f'No unfinished notes matching "{term}".')
            return 0

        print_notes(rows)
        return 0

    except sqlite3.Error as exc:
        print(f"Error searching notes: {exc}", file=sys.stderr)
        return 1


# ============================================================
# Done
# ============================================================

def done_note(note_id):
    try:
        note_id = int(note_id)
    except ValueError:
        print("Error: ID must be a number.")
        return 1

    try:
        with connect_db() as conn:

            row = conn.execute(
                """
                SELECT id, text, completed_at
                FROM notes
                WHERE id = ?
                """,
                (note_id,)
            ).fetchone()

            if row is None:
                print(f"Error: note #{note_id} does not exist.")
                return 1

            if row[2] is not None:
                print(f"✓ Note #{note_id} is already completed.")
                return 0

            conn.execute(
                """
                UPDATE notes
                SET completed_at = ?
                WHERE id = ?
                """,
                (now(), note_id)
            )

            remaining = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NULL
                """
            ).fetchone()[0]

        print()
        print(f"✓ COMPLETED #{note_id}")
        print(f"  {row[1]}")
        print()
        print(motivational_message())

        if remaining == 0:
            print("🎉 All tasks are complete!")
        elif remaining == 1:
            print("1 unfinished task remaining.")
        else:
            print(f"{remaining} unfinished tasks remaining.")

        return 0

    except sqlite3.Error as exc:
        print(
            f"Error completing note: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# Undo
# ============================================================

def undo_note(note_id):
    try:
        note_id = int(note_id)
    except ValueError:
        print("Error: ID must be a number.")
        return 1

    try:
        with connect_db() as conn:

            row = conn.execute(
                """
                SELECT id, text, completed_at
                FROM notes
                WHERE id = ?
                """,
                (note_id,)
            ).fetchone()

            if row is None:
                print(f"Error: note #{note_id} does not exist.")
                return 1

            if row[2] is None:
                print(f"Note #{note_id} is already unfinished.")
                return 0

            conn.execute(
                """
                UPDATE notes
                SET completed_at = NULL
                WHERE id = ?
                """,
                (note_id,)
            )

        print(f"↩ Restored #{note_id}")
        print(f"  {row[1]}")

        return 0

    except sqlite3.Error as exc:
        print(
            f"Error restoring note: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# History
# ============================================================

def history():
    try:
        with connect_db() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, text, completed_at
                FROM notes
                WHERE completed_at IS NOT NULL
                ORDER BY id DESC
                """
            ).fetchall()

        if not rows:
            print("No completed notes yet.")
            return 0

        print("QuickDrop — completed history")
        print("-" * 80)

        for note_id, created_at, text, completed_at in rows:
            print(
                f"✓ {note_id} | "
                f"{pretty_date(completed_at)} | "
                f"{text}"
            )

        return 0

    except sqlite3.Error as exc:
        print(
            f"Error reading history: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# Stats
# ============================================================

def stats():
    try:
        with connect_db() as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM notes"
            ).fetchone()[0]

            completed = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NOT NULL
                """
            ).fetchone()[0]

            remaining = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NULL
                """
            ).fetchone()[0]

            completed_today = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NOT NULL
                  AND date(completed_at) =
                      date('now', 'localtime')
                """
            ).fetchone()[0]

        print("QuickDrop Stats")
        print("-" * 30)
        print(f"Total notes     : {total}")
        print(f"Completed       : {completed}")
        print(f"Remaining       : {remaining}")
        print(f"Completed today : {completed_today}")

        if total > 0:
            percentage = (completed / total) * 100
            print(f"Completion rate : {percentage:.1f}%")

        print()

        if remaining == 0 and total > 0:
            print("🎉 Everything is complete!")
        elif completed_today > 0:
            print(
                f"🔥 You completed "
                f"{completed_today} task(s) today!"
            )
        else:
            print("Start with one small task. 🚀")

        return 0

    except sqlite3.Error as exc:
        print(f"Error reading stats: {exc}", file=sys.stderr)
        return 1


# ============================================================
# Clear completed
# ============================================================

def clear_completed():
    try:
        with connect_db() as conn:

            count = conn.execute(
                """
                SELECT COUNT(*)
                FROM notes
                WHERE completed_at IS NOT NULL
                """
            ).fetchone()[0]

            if count == 0:
                print("No completed notes to clear.")
                return 0

            print(
                f"This will permanently delete "
                f"{count} completed note(s)."
            )

            answer = input("Continue? [y/N]: ").strip().lower()

            if answer not in ("y", "yes"):
                print("Cancelled.")
                return 0

            conn.execute(
                """
                DELETE FROM notes
                WHERE completed_at IS NOT NULL
                """
            )

        print(f"✓ Deleted {count} completed note(s).")
        return 0

    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130

    except sqlite3.Error as exc:
        print(
            f"Error clearing notes: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# Backup
# ============================================================

def backup_database():
    try:
        with connect_db():
            pass

        BACKUP_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().astimezone().strftime(
            "%Y%m%d_%H%M%S"
        )

        backup_path = BACKUP_DIRECTORY / (
            f"quickdrop_{timestamp}.db"
        )

        source = sqlite3.connect(DATABASE_PATH)
        destination = sqlite3.connect(backup_path)

        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()

        print("✓ Backup created:")
        print(f"  {backup_path}")

        return 0

    except (sqlite3.Error, OSError) as exc:
        print(
            f"Error creating backup: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# Path
# ============================================================

def show_path():
    print(f"Notes directory : {NOTES_DIRECTORY}")
    print(f"Database        : {DATABASE_PATH}")
    print(f"Backup directory: {BACKUP_DIRECTORY}")
    return 0


# ============================================================
# Help
# ============================================================

def show_help():
    print("""
QuickDrop - fast local Termux notes/tasks

Usage:

  qd "note text"        Save a note/task
  qd list               List unfinished notes
  qd search WORD        Search unfinished notes
  qd done ID            Mark a note as completed
  qd undo ID            Restore a completed note
  qd recent             Show the last 5 unfinished notes
  qd history            Show completed notes
  qd stats              Show completion statistics
  qd backup             Create a database backup
  qd clear              Permanently remove completed notes
  qd path               Show storage location
  qd help               Show this help

Examples:

  qd "Remember to test the Bedrock shader"
  qd "Finish maths activity"
  qd list
  qd done 4
  qd undo 4
  qd search shader
  qd recent
  qd history
  qd stats
  qd backup
""")


# ============================================================
# Main
# ============================================================

def main():

    try:

        if len(sys.argv) == 1:
            print('Usage: qd "your note"')
            print("Run 'qd help' for all commands.")
            return 0

        command = sys.argv[1]

        if command == "help":
            show_help()
            return 0

        if command == "list":
            if len(sys.argv) != 2:
                print("Usage: qd list")
                return 1
            return list_notes()

        if command == "recent":
            if len(sys.argv) != 2:
                print("Usage: qd recent")
                return 1
            return recent_notes()

        if command == "search":
            if len(sys.argv) < 3:
                print("Usage: qd search WORD")
                return 1
            return search_notes(" ".join(sys.argv[2:]))

        if command == "done":
            if len(sys.argv) != 3:
                print("Usage: qd done ID")
                return 1
            return done_note(sys.argv[2])

        if command == "undo":
            if len(sys.argv) != 3:
                print("Usage: qd undo ID")
                return 1
            return undo_note(sys.argv[2])

        if command == "history":
            if len(sys.argv) != 2:
                print("Usage: qd history")
                return 1
            return history()

        if command == "stats":
            if len(sys.argv) != 2:
                print("Usage: qd stats")
                return 1
            return stats()

        if command == "backup":
            if len(sys.argv) != 2:
                print("Usage: qd backup")
                return 1
            return backup_database()

        if command == "clear":
            if len(sys.argv) != 2:
                print("Usage: qd clear")
                return 1
            return clear_completed()

        if command == "path":
            if len(sys.argv) != 2:
                print("Usage: qd path")
                return 1
            return show_path()

        # Everything else becomes a note.
        text = " ".join(sys.argv[1:])
        return save_note(text)

    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130

    except Exception as exc:
        print(
            f"Unexpected error: {exc}",
            file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
