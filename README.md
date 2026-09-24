# ⚡ QuickDrop

**QuickDrop** is a fast, local command-line note and task manager designed for **Termux on Android**.

Capture thoughts, tasks, reminders, commands, ideas, or anything else instantly:

```bash
qd "Remember to update my Minecraft mods"
```

No cloud. No account. No server. No external database.

Just **Termux + Python + SQLite**.

---

## ✨ Features

* ⚡ Instant note capture from anywhere
* 📋 Unfinished note list
* 🚀 Automatically show recent unfinished notes when starting a new Termux session
* 🔎 Search notes
* ✅ Complete notes without immediately deleting them
* ↩️ Undo completed notes
* 📜 Completion history
* 📊 Note statistics
* 💾 SQLite database backups
* 🧹 Remove completed notes when you no longer need them
* 📍 Show storage locations
* 📴 Works completely offline
* 🗄️ Uses Python's built-in SQLite support
* 📦 No third-party Python packages required

---

## 📱 Requirements

* Android
* [Termux](https://termux.dev/)
* Python 3
* Bash

Install Python in Termux:

```bash
pkg update
pkg install python
```

Git is only required if you want to clone the repository with Git.

```bash
pkg install git
```

---

# 🚀 Installation

QuickDrop **does not require a specific installation directory**.

You can clone the repository wherever you want.

For example:

```bash
cd ~/projects/free
git clone https://github.com/DataZahard/quickdrop.git
cd quickdrop
```

You can also clone or extract the repository somewhere else. Just make sure `QD_PROGRAM_DIRECTORY` points to that directory before running the installer.

### Configure installation paths

QuickDrop lets you choose where its program files, notes, backups, and Bash configuration live. Set these variables before running the installer:

```bash
export QD_PROGRAM_DIRECTORY="$PWD"
export QD_NOTES_DIRECTORY="$HOME/.quickdrop"
export QD_BACKUP_DIRECTORY="$HOME/.quickdrop/backups"
export QD_BASHRC_PATH="$HOME/.bashrc"
```

For example, if your repository is at `~/Downloads/quickdrop`:

```bash
cd ~/Downloads/quickdrop
export QD_PROGRAM_DIRECTORY="$PWD"
export QD_NOTES_DIRECTORY="$HOME/.quickdrop"
export QD_BACKUP_DIRECTORY="$HOME/.quickdrop/backups"
export QD_BASHRC_PATH="$HOME/.bashrc"
./install.sh
```

### Launcher path

The `qd` launcher is created **inside the QuickDrop program directory**.

For example:

```bash
export QD_PROGRAM_DIRECTORY="$HOME/projects/free/quickdrop"
```

The launcher will then be:

```text
$HOME/projects/free/quickdrop/qd
```

The installer adds the configured program directory to your `PATH`, so you can run `qd` from any directory.


### Run the installer

```bash
chmod +x install.sh
./install.sh
```

The installer will:

1. Use the program directory you set with `QD_PROGRAM_DIRECTORY` (or `$HOME/quickdrop` if you do not set it).
2. Create the local data directory.
3. Initialize the SQLite database.
4. Set up the `qd` command at the launcher's configured location.
5. Add the configured program directory to your `PATH`.
6. Configure automatic recent-note display for interactive Termux sessions.
7. Preserve existing `.bashrc` configuration instead of replacing it.

After installation, reload your shell:

```bash
source ~/.bashrc
```

Then test:

```bash
qd help
```

---

# 📝 Usage

## Add a note

```bash
qd "Finish maths activity"
```

Example:

```text
✓ Saved #7
```

You can run this from **any directory**.

```bash
cd ~/some/random/folder
qd "Remember this"
```

---

## List unfinished notes

```bash
qd list
```

Shows notes that haven't been completed yet.

---

## Show recent notes

```bash
qd recent
```

Shows your 5 most recent unfinished notes.

QuickDrop can also automatically run this when you open a new interactive Termux session.

---

## Search notes

```bash
qd search minecraft
```

Searches your unfinished notes for the specified term.

---

## Complete a note

```bash
qd done 7
```

The note is marked as completed rather than immediately being destroyed.

---

## Undo a completed note

```bash
qd undo 7
```

Moves the note back into your unfinished list.

---

## View completed notes

```bash
qd history
```

Shows your completed notes and their completion times.

---

## View statistics

```bash
qd stats
```

Displays information such as:

* Total notes
* Completed notes
* Unfinished notes
* Notes completed today
* Completion rate

---

## Backup your database

```bash
qd backup
```

Creates a timestamped SQLite backup.

---

## Clear completed notes

```bash
qd clear
```

QuickDrop asks for confirmation before permanently removing completed notes.

---

## Show storage paths

```bash
qd path
```

Useful for finding your database and backups.

---

## Show all commands

```bash
qd help
```

---

# 📚 Command Reference

| Command          | What it does                   |
| ---------------- | ------------------------------ |
| `qd "TEXT"`      | Create a new note              |
| `qd list`        | Show unfinished notes          |
| `qd recent`      | Show 5 recent unfinished notes |
| `qd search WORD` | Search unfinished notes        |
| `qd done ID`     | Mark a note completed          |
| `qd undo ID`     | Restore a completed note       |
| `qd history`     | Show completed notes           |
| `qd stats`       | Show statistics                |
| `qd backup`      | Create a database backup       |
| `qd clear`       | Delete completed notes         |
| `qd path`        | Show QuickDrop paths           |
| `qd help`        | Show help                      |

---

# 📂 File & Data Locations

QuickDrop keeps **application files and user data separate**.

The repository can be cloned anywhere, but the installer **does not automatically detect the clone location**. Before running the installer, set `QD_PROGRAM_DIRECTORY` to the directory containing `quickdrop.py`.

For example:

```text
~/projects/quickdrop/
```

or:

```text
~/Downloads/quickdrop/
```

or:

```text
~/my-tools/quickdrop/
```

The installer does not require a particular clone location, but you must set `QD_PROGRAM_DIRECTORY` to the clone/extracted directory.

### User data

QuickDrop stores its persistent data in:

```text
~/.quickdrop/
```

The main database is:

```text
~/.quickdrop/quickdrop.db
```

Backups are stored in:

```text
~/.quickdrop/backups/
```

This means deleting or moving the repository does not inherently mean your notes have to move with it.

---

# 🔒 Privacy & Offline Operation

QuickDrop is **local-first**.

Your notes are stored on your device using SQLite.

QuickDrop does not require:

* ☁️ Cloud storage
* 🌐 Internet access
* 🔑 An online account
* 🗄️ An external database
* 🔌 An API
* 🖥️ A server

Your data stays on your device unless you choose to copy or back it up elsewhere.

---

# 🛠️ Project Structure

The repository contains the application and installation files:

```text
quickdrop/
├── quickdrop.py
├── qd
├── install.sh
├── README.md
└── LICENSE
```

The user's data is **not stored inside the repository**. The `LICENSE` file is part of the repository; the database and backups are not.

```text
~/.quickdrop/
├── quickdrop.db
└── backups/
```

---

# 🔄 Updating QuickDrop

If you installed QuickDrop from Git, pull updates from the directory where you cloned the repository:

```bash
cd /path/to/quickdrop
git pull
```

Then run the installer again if the installation configuration has changed:

```bash
./install.sh
```

Your existing database in:

```text
~/.quickdrop/quickdrop.db
```

is preserved.

---

# 🗃️ Backups

Before major changes or upgrades, you can create a backup:

```bash
qd backup
```

You can also inspect the data location with:

```bash
qd path
```

For extra safety, keep a copy of important database backups outside the QuickDrop directory.

---

# 🧠 Philosophy

QuickDrop isn't intended to replace a full productivity suite.

It's for the moments when you need to get something **out of your head immediately**.

Instead of:

> Open an app → wait → find a notebook → create a note → type...

Just:

```bash
qd "Don't forget this"
```

**Capture first. Organize later.**

---

# 📄 License

QuickDrop is licensed under the [MIT License](LICENSE).

```text
MIT License
```

---

# 🤝 Contributing

Bug reports, feature requests, improvements, and pull requests are welcome.

If you find a problem, please include:

* Termux version
* Android version
* Python version
* QuickDrop version/commit
* The command that caused the problem
* Relevant error output

---

## ⭐ Quick Example

```bash
$ qd "Backup my important files"

✓ Saved #12

$ qd list

12 | 2026-09-20 10:32 | Backup my important files

1 unfinished note(s).

$ qd done 12

✓ COMPLETED #12
Backup my important files

🎉 Nice work!

$ qd history

12 | 2026-09-20 10:32 | Backup my important files
```

---

**QuickDrop — dump it now, deal with it later. ⚡**

**Developed by: Data Zahard**
