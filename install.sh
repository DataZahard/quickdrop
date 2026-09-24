#!/data/data/com.termux/files/usr/bin/bash

set -e

# ============================================================
# QuickDrop configuration
#
# Change these variables if you want different locations.
# ============================================================

PROGRAM_DIRECTORY="${QD_PROGRAM_DIRECTORY:-$HOME/quickdrop}"

NOTES_DIRECTORY="${QD_NOTES_DIRECTORY:-$HOME/.quickdrop}"

BACKUP_DIRECTORY="${QD_BACKUP_DIRECTORY:-$NOTES_DIRECTORY/backups}"

BASHRC_PATH="${QD_BASHRC_PATH:-$HOME/.bashrc}"

# The qd launcher requested by this setup.
QD_LAUNCHER="$HOME/projects/free/qd"


echo "================================"
echo "       QuickDrop Installer"
echo "================================"
echo

echo "Program directory : $PROGRAM_DIRECTORY"
echo "Notes directory   : $NOTES_DIRECTORY"
echo "Backup directory  : $BACKUP_DIRECTORY"
echo "Bashrc            : $BASHRC_PATH"
echo "Launcher          : $QD_LAUNCHER"
echo

# ------------------------------------------------------------
# Check Python
# ------------------------------------------------------------

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 was not found."
    echo "Install Python in Termux first with:"
    echo
    echo "pkg install python"
    exit 1
fi

# ------------------------------------------------------------
# Create directories
# ------------------------------------------------------------

mkdir -p "$PROGRAM_DIRECTORY"
mkdir -p "$NOTES_DIRECTORY"
mkdir -p "$BACKUP_DIRECTORY"
mkdir -p "$(dirname "$QD_LAUNCHER")"

# ------------------------------------------------------------
# Check that quickdrop.py exists
# ------------------------------------------------------------

if [ ! -f "$PROGRAM_DIRECTORY/quickdrop.py" ]; then
    echo
    echo "Error: quickdrop.py was not found at:"
    echo "$PROGRAM_DIRECTORY/quickdrop.py"
    echo
    echo "Put quickdrop.py there before running this installer."
    exit 1
fi

# ------------------------------------------------------------
# Create/update launcher
# ------------------------------------------------------------

if [ -f "$QD_LAUNCHER" ]; then
    echo "Updating launcher: $QD_LAUNCHER"
fi

cat > "$QD_LAUNCHER" <<EOF
#!/data/data/com.termux/files/usr/bin/bash

set -u

PROGRAM_DIRECTORY="\${QD_PROGRAM_DIRECTORY:-$PROGRAM_DIRECTORY}"

PYTHON_PROGRAM="\$PROGRAM_DIRECTORY/quickdrop.py"

if [ ! -f "\$PYTHON_PROGRAM" ]; then
    printf 'QuickDrop error: program not found:\\n%s\\n' "\$PYTHON_PROGRAM" >&2
    printf 'Set QD_PROGRAM_DIRECTORY or reinstall QuickDrop.\\n' >&2
    exit 1
fi

exec python3 "\$PYTHON_PROGRAM" "\$@"
EOF

chmod +x "$QD_LAUNCHER"

# ------------------------------------------------------------
# Initialize database
# ------------------------------------------------------------

echo "Initializing database..."

QD_NOTES_DIRECTORY="$NOTES_DIRECTORY" \
QD_BACKUP_DIRECTORY="$BACKUP_DIRECTORY" \
python3 "$PROGRAM_DIRECTORY/quickdrop.py" path >/dev/null

# ------------------------------------------------------------
# Add launcher directory to PATH
#
# We use a uniquely identifiable block so repeated installer
# runs don't add duplicate entries.
# ------------------------------------------------------------

PATH_LINE='export PATH="$HOME/projects/free:$PATH"'

if [ ! -f "$BASHRC_PATH" ]; then
    echo "Creating $BASHRC_PATH"
    touch "$BASHRC_PATH"
fi

if ! grep -Fqx "$PATH_LINE" "$BASHRC_PATH"; then
    printf '\n# QuickDrop PATH\n%s\n' "$PATH_LINE" >> "$BASHRC_PATH"
    echo "Added QuickDrop launcher directory to PATH."
else
    echo "PATH configuration already exists."
fi

# ------------------------------------------------------------
# Add automatic recent-notes display for interactive shells.
#
# This only runs for interactive Bash sessions.
# It does not run every time qd is used.
# ------------------------------------------------------------

RECENT_BLOCK_START="# QuickDrop recent notes"

if ! grep -Fqx "$RECENT_BLOCK_START" "$BASHRC_PATH"; then
    cat >> "$BASHRC_PATH" <<'EOF'

# QuickDrop recent notes
if [[ $- == *i* ]] && command -v qd >/dev/null 2>&1; then
    qd recent
fi
EOF

    echo "Added automatic recent-notes display."
else
    echo "Recent-notes configuration already exists."
fi

# ------------------------------------------------------------
# Finish
# ------------------------------------------------------------

echo
echo "================================"
echo "      Installation complete"
echo "================================"
echo
echo "Database:"
echo "  $NOTES_DIRECTORY/quickdrop.db"
echo
echo "Launcher:"
echo "  $QD_LAUNCHER"
echo
echo "Reload your Bash configuration with:"
echo
echo "  source \"$BASHRC_PATH\""
echo
echo "Then try:"
echo
echo '  qd "hello world"'
echo "  qd list"
echo "  qd search hello"
echo "  qd backup"
echo
