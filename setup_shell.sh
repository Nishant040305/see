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
    # List of subcommands and flags that just show information (don't need eval)
    local info_cmds=" list search show delete stats install help -h --help interactive tags import"
    
    # Check if the first argument is empty or one of these info commands/flags
    if [[ \$# -eq 0 ]] || [[ " \$info_cmds " =~ " \$1 " ]]; then
        # Just run normally
        command $SEE_SCRIPT "\$@"
    else
        # It's 'run' or the 'add' syntax (which implies execution)
        # We capture the output and eval it
        local cmd_output=\$(command $SEE_SCRIPT "\$@")
        if [[ -n "\$cmd_output" ]]; then
            eval "\$cmd_output"
        fi
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
