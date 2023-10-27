
conda activate morpheus

python_path=$(which python)
python_dir=$(dirname $(dirname "$python_path"))
echo "Python is installed at: $python_path"
echo "Directory two levels above Python interpreter: $parent_dir"

virtuoso -nograph <<EOF
load("$python_dir/lib/python3.11/site-packages/skillbridge/server/python_server.il")
pyStartServer()
EOF