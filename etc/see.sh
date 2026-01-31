# SEE Command Helper - Global Shell Integration
# Installed to /etc/profile.d/see.sh

see() {
    # List of subcommands and flags that just show information (don't need eval)
    local info_cmds=" list search show delete stats install help -h --help interactive import i tags "
    
    # Check if the first argument is empty or one of these info commands/flags
    if [[ $# -eq 0 ]] || [[ " $info_cmds " =~ " $1 " ]]; then
        # Just run normally
        command /usr/share/see/see "$@"
    else
        # It's 'run' or the 'add' syntax (which implies execution)
        # We capture the output and eval it
        local cmd_output=$(command /usr/share/see/see "$@")
        if [[ -n "$cmd_output" ]]; then
            eval "$cmd_output"
        fi
    fi
}
