"""Shell integration installer."""

import os
from pathlib import Path
from typing import Optional


def get_shell_wrapper(shell: str, script_path: str) -> str:
    """Get the shell wrapper function for the specified shell."""
    
    if shell == 'bash' or shell == 'zsh':
        return f'''# SEE Command Helper - Shell Integration
see() {{
    # List of subcommands and flags that just show information (don't need eval)
    local info_cmds=" list search show delete stats install help -h --help "
    
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
    set -l info_cmds list search show delete stats install help -h --help
    
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
    
    print(f"\n🔧 Installing SEE shell integration for {shell}...")
    print(f"\nAdd the following to your {config_file}:\n")
    print("=" * 60)
    print(wrapper)
    print("=" * 60)
    print(f"\nThen run: source {config_file}")
    print("\nOr, to install automatically, run:")
    print(f"  see install {shell} >> {config_file} && source {config_file}")
