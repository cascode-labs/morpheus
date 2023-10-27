
conda activate morpheus #set python to venv

clsAdminTool -ale .  #clear lock files

python_path=$(which python) #get python
python_dir=$(dirname $(dirname "$python_path")) #go two dir above

echo "Python is installed at: $python_path"
echo "Morpheus Directory above Python interpreter: $parent_dir"

virtuoso -nograph <<EOF
load("$python_dir/lib/python3.11/site-packages/skillbridge/server/python_server.il")
pyStartServer(?id "test")
EOF