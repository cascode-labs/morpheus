# Set the inactivity timeout in seconds
timeout_duration=3  # 5 minutes
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Function to reset the timeout
reset_timeout() {
    last_activity=$(date +%s)
}

# Function to handle inactivity
handle_inactivity() {
    current_time=$(date +%s)
    elapsed_time=$((current_time - last_activity))

    if [ $elapsed_time -ge $timeout_duration ]; then
        echo "Inactivity timeout reached. Exiting..."
        exit 0
    fi
}

conda activate morpheus # set Python to venv

clsAdminTool -are .  # clear lock files

python_path=$(which python) # get python
python_dir=$(dirname $(dirname "$python_path")) # go two dirs above

echo "Python is installed at: $python_path"
echo "Morpheus Directory above Python interpreter: $python_dir"
log_file="virtuoso_output.log"

(virtuoso -nograph <<EOF >>"$log_file" 2>&1 &
load("$python_dir/lib/python3.11/site-packages/skillbridge/server/python_server.il")
pyStartServer(?id "test")
load("$SCRIPT_DIR/killcadence.il")
EOF
)</dev/null >/dev/null 2>&1 &

# Get the process ID of the virtuoso command
virtuoso_pid=$!

# Main loop to handle inactivity
while true; do
    reset_timeout
    handle_inactivity

    # Check if virtuoso process is still running
    if ! ps -p $virtuoso_pid > /dev/null; then
        echo "Virtuoso process has exited. Exiting..."
        exit 0
    fi

    sleep 1  # Adjust as needed
done
: '
'