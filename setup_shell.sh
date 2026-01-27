#!/bin/bash
# SEE Helper - Shell Integration Setup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEE_SCRIPT="$SCRIPT_DIR/see"

echo "🔧 SEE Command Helper - Shell Integration Setup"
echo "================================================"
echo ""

# Detect shell
if [ -n "$BASH_VERSION" ]; then
    SHELL_TYPE="bash"
    CONFIG_FILE="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_TYPE="zsh"
    CONFIG_FILE="$HOME/.zshrc"
else
    echo "⚠️  Could not auto-detect shell type."
    echo "Please run: $SEE_SCRIPT install [bash|zsh|fish]"
    exit 1
fi

echo "Detected shell: $SHELL_TYPE"
echo "Config file: $CONFIG_FILE"
echo ""

# Check if already installed
if grep -q "# SEE Command Helper - Shell Integration" "$CONFIG_FILE" 2>/dev/null; then
    echo "✓ Shell integration already installed in $CONFIG_FILE"
    echo ""
    echo "To reinstall, remove the existing 'see()' function from $CONFIG_FILE"
    echo "and run this script again."
    exit 0
fi

echo "Installing shell integration..."
echo ""

# Add the shell function
cat >> "$CONFIG_FILE" << EOF

# SEE Command Helper - Shell Integration
# Added by setup_shell.sh on $(date)
see() {
    # Check if this is a command that needs shell evaluation
    if [[ "\$1" == "run" ]] || [[ "\$2" == "-c" ]] || [[ "\$2" == "--command" ]]; then
        # Capture both stdout and check if we're in run mode
        if [[ "\$1" == "run" ]]; then
            # Get the command to execute
            local cmd_output=\$(command $SEE_SCRIPT run "\${@:2}" --shell-mode 2>/dev/null)
            if [[ -n "\$cmd_output" ]]; then
                # Execute in current shell
                eval "\$cmd_output"
            fi
        else
            # For add commands, execute and capture
            local cmd_output=\$(command $SEE_SCRIPT "\$@" --shell-mode 2>&1)
            # The actual command will be on stdout, messages on stderr
            if [[ -n "\$cmd_output" ]]; then
                eval "\$cmd_output"
            fi
        fi
    else
        # For other subcommands, just run normally
        command $SEE_SCRIPT "\$@"
    fi
}
EOF

echo "✓ Shell integration installed successfully!"
echo ""
echo "To activate it, run:"
echo "  source $CONFIG_FILE"
echo ""
echo "Or simply open a new terminal."
echo ""
echo "Test it with:"
echo "  see run 2"
echo "  echo \$https_proxy"
echo ""
