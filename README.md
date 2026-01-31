# SEE - CLI Command Helper

A simple, powerful tool to save, search, and manage your frequently used CLI commands.(support Linux currently)

## Features

- 💾 **Save commands** with descriptions and tags
- 🔍 **Search** through your command history
- 🏷️ **Tag-based organization**
- 🔖 **Aliases** - Assign memorable names to commands (e.g., `see myls`)
- 📊 **Usage statistics**
- 🐚 **Shell integration** - Commands like `export` affect your current shell!
- ⚡ **Quick execution** - Run saved commands by ID or Alias

## Installation

### RPM Package (Recommended for Fedora/RHEL)

The easiest way to install is using the RPM package, which automatically handles dependencies and shell integration.

1. Download the latest `.rpm` from the [Releases page](https://github.com/Nishant040305/see/releases).
2. Install it:
```bash
sudo dnf install see-0.1.0-1.fc43.noarch.rpm
```
3. Open a new terminal. The `see` command (and its shell integration like `cd/export`) will work immediately!

### Manual Installation (Development)

If you are developing or cannot use the RPM:

1. Make the script executable:
```bash
chmod +x see
```

2. (Optional) Create a symlink to use it as `see`:
```bash
sudo ln -s $(pwd)/see /usr/local/bin/see
```

### Shell Integration (Recommended)

Shell integration allows commands like `export`, `cd`, and other shell built-ins to affect your current shell session.

**Auto-install:**
```bash
# Auto-detect your shell and show installation instructions
./see.py install

# Or specify your shell
./see.py install bash
./see.py install zsh
./see.py install fish
```

**Manual installation:**

For **bash**, add to `~/.bashrc`:
```bash
see() {
    # List of subcommands that just show information (don't need eval)
    local info_cmds=" list search show delete stats install "
    
    # Check if the first argument is one of these info commands
    if [[ " $info_cmds " =~ " $1 " ]]; then
        # Just run normally
        command see "$@"
    else
        # It's 'run', or the 'add' syntax (which implies execution)
        # We capture the output and eval it
        local cmd_output=$(command see "$@")
        if [[ -n "$cmd_output" ]]; then
            eval "$cmd_output"
        fi
    fi
}
```

For **zsh**, add to `~/.zshrc` (same as bash).

For **fish**, add to `~/.config/fish/config.fish`:
```fish
function see
    # List of subcommands that just show information
    set -l info_cmds list search show delete stats install
    
    if contains -- $argv[1] $info_cmds
        # Just run normally
        command see $argv
    else
        # Capture output and eval
        set -l cmd_output (command see $argv)
        if test -n "$cmd_output"
            eval $cmd_output
        end
    end
end
```

Then reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc or ~/.config/fish/config.fish
```

## Usage

### Adding Commands

**Basic syntax:**
```bash
see -d "description" -t tag1 tag2 [-a alias] -c <command>
```

**Examples:**
```bash
# Save and execute a command
see -d "List all files" -t files ls -c ls -lah

# Save a proxy configuration
see -d "Set HTTP proxy" -t proxy network -c export https_proxy=http://proxy:3128

# Save without executing (use -s flag)
see -s -d "Dangerous command" -t system -c rm -rf /tmp/*

# Save a git command
# Save a git command with an alias
see -d "Git log pretty" -t git log -a glog -c git log --oneline --graph --all

```

### Running Saved Commands

```bash
# Run by ID
see run 1

# Run by Alias (requires shell integration)
see my_alias

# Dry run (show what would be executed)
see run 1 --dry-run
```

### Using Aliases

You can assign a short, memorable alias to any command.

```bash
# Assign alias 'myls' to command ID 5
see alias 5 -a myls

# Run the alias
see myls
```

Aliases are validated to prevent conflicts with system commands (like `ls`, `cd`, `grep`) and `see` subcommands.
```

### Searching Commands

```bash
# Search by keyword
see search proxy

# Search by tags
see search -t git

# Search by keyword and tags
see search log -t git
```

### Listing Commands

```bash
# List all commands
see list

# List by tag
see list -t docker

# Limit results
see list -n 5
```

### Other Commands

```bash
# Show a specific command
see show 3

# Show and copy to clipboard (requires pyperclip)
see show 3 -c

# Delete a command
see delete 5

# Assign an alias
see alias 5 -a mycmd

# Show statistics
see stats
```

## Architecture

The codebase is organized into modular components:

### Core Classes

- **`CommandStorage`**: Handles JSON file I/O for command persistence
- **`CommandManager`**: Manages CRUD operations on commands
- **`CommandExecutor`**: Handles command execution (subprocess or shell mode)
- **`CommandPrinter`**: Pretty-prints commands and statistics
- **`CLI`**: Orchestrates all operations and handles user interactions

### Key Features

1. **Modular Design**: Each class has a single responsibility
2. **Shell Mode**: Commands output raw text by default for shell evaluation (use `-v` for verbose output)
3. **Type Hints**: Full type annotations for better IDE support
4. **Error Handling**: Graceful handling of corrupted files and missing commands
5. **Usage Tracking**: Automatically tracks command usage frequency

## How Shell Integration Works

Without shell integration:
```bash
see run 1  # Runs: export VAR=value
echo $VAR  # Empty! (command ran in subprocess)
```

With shell integration:
```bash
see run 1  # Runs: export VAR=value
echo $VAR  # value (command ran in current shell!)
```

This also applies to **Aliases**:
```bash
see my_export_alias
echo $VAR  # Works!
```
```

The shell wrapper:
1. Detects when you're running a command
2. Calls `see` (which outputs raw command text by default)
3. Captures the command output
4. Evaluates it in your current shell using `eval`

## Configuration

Commands are stored in: `~/.config/see-helper/commands.json`

## Requirements

- Python 3.6+
- Optional: `pyperclip` OR system tools (`xclip`, `xsel`, `wl-copy`) for clipboard support

## Examples

### Setting Environment Variables
```bash
# Save proxy settings
see -d "Set corporate proxy" -t proxy -c export https_proxy=http://proxy:3128

# Later, apply the proxy settings
see run 1
echo $https_proxy  # Works with shell integration!
```

### Docker Commands
```bash
see -d "Remove all containers" -t docker cleanup -c docker rm -f $(docker ps -aq)
see -d "Remove all images" -t docker cleanup -c docker rmi -f $(docker images -q)
see -d "Docker system prune" -t docker cleanup -c docker system prune -af

# List all docker commands
see list -t docker
```

### Git Workflows
```bash
see -d "Git status short" -t git -c git status -s
see -d "Git log graph" -t git log -c git log --oneline --graph --all --decorate
see -d "Git uncommit" -t git undo -c git reset --soft HEAD~1

# Search git commands
see search -t git
```

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
