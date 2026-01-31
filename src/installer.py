"""Shell integration installer."""

import os
import sys
from pathlib import Path
from typing import Optional


def get_shell_wrapper(shell: str, script_path: str) -> str:
    """Get the shell wrapper function for the specified shell."""
    
    if shell == 'bash' or shell == 'zsh':
        return f'''# SEE Command Helper - Shell Integration
see() {{
    # List of subcommands and flags that just show information (don't need eval)
    local info_cmds=" list search show delete stats install help -h --help interactive import i tags alias edit "
    
    # Check if the first argument is empty or one of these info commands/flags
    if [[ $# -eq 0 ]] || [[ " $info_cmds " =~ " $1 " ]]; then
        # Just run normally
        command {script_path} "$@"
    else
        # It's 'run' or the 'add' syntax (which implies execution)
        # We capture the output and eval it
        local cmd_output=$(command {script_path} "$@")
        if [[ -n "$cmd_output" ]]; then
            eval "$cmd_output"
        fi
    fi
}}
'''
    elif shell == 'fish':
        return f'''# SEE Command Helper - Shell Integration
function see
    # List of subcommands and flags that just show information
    set -l info_cmds list search show delete stats install help -h --help interactive import i tags alias edit
    
    if test (count $argv) -eq 0; or contains -- $argv[1] $info_cmds
        # Just run normally
        command {script_path} $argv
    else
        # Capture output and eval
        set -l cmd_output (command {script_path} $argv)
        if test -n "$cmd_output"
            eval $cmd_output
        end
    end
end
'''
    
    return ""


def handle_install(shell: Optional[str] = None, script_path: Optional[str] = None):
    """Handle shell wrapper installation."""
    # Auto-detect shell if not specified
    if not shell:
        shell_env = os.environ.get('SHELL', '')
        if 'bash' in shell_env:
            shell = 'bash'
        elif 'zsh' in shell_env:
            shell = 'zsh'
        elif 'fish' in shell_env:
            shell = 'fish'
        else:
            print("Could not auto-detect shell. Please specify: see install [bash|zsh|fish]")
            return
    
    # Get the absolute path to the script
    if not script_path:
        script_path = os.path.abspath(__file__)
        # If we're in the package, point to the main script
        if 'see_helper' in script_path:
            script_path = str(Path(script_path).parent.parent / 'see')
    
    # Get the wrapper function
    wrapper = get_shell_wrapper(shell, script_path)
    
    # Determine config file
    config_files = {
        'bash': Path.home() / '.bashrc',
        'zsh': Path.home() / '.zshrc',
        'fish': Path.home() / '.config' / 'fish' / 'config.fish'
    }
    
    config_file = config_files.get(shell)
    if not config_file:
        print(f"Unsupported shell: {shell}")
        return
    
    print(f"\nInstalling SEE shell integration for {shell}...", file=sys.stderr)
    
    # Check if we can write to the file
    try:
        # Read existing content to check for duplicates
        if config_file.exists():
            content = config_file.read_text()
            if "see()" in content and "# SEE Command Helper" in content:
                print(f"Shell integration already appears to be installed in {config_file}", file=sys.stderr)
                print(f"\nTo reinstall, remove the 'see()' function and try again.", file=sys.stderr)
                return

        # Append to the config file
        with open(config_file, "a") as f:
            f.write("\n" + wrapper + "\n")
            
        print(f" Successfully added shell integration to {config_file}", file=sys.stderr)
        print(f"\nTo activate it now, run:\n  source {config_file}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error writing to {config_file}: {e}", file=sys.stderr)
        print("\nPlease add the following manually:\n", file=sys.stderr)
        print(wrapper)
