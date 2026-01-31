# SEE Command Helper - Global Shell Integration
# Installed to /etc/profile.d/see.fish

function see
    # List of subcommands and flags that just show information
    set -l info_cmds list search show delete stats install help -h --help interactive import i tags alias edit
    
    if test (count $argv) -eq 0; or contains -- $argv[1] $info_cmds
        # Just run normally
        command /usr/share/see/see $argv
    else
        # Capture output and eval
        set -l cmd_output (command /usr/share/see/see $argv)
        if test -n "$cmd_output"
            eval $cmd_output
        end
    end
end
