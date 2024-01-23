#!/bin/bash
PROJECT="morpheus"
VERSION=$(cat version)
DIST_PATH="dist/v$VERSION"
conda activate morpheus
echo "Building ${PROJECT} v$VERSION"
rm -rf "$DIST_PATH"
mkdir -p "$DIST_PATH"

# Executable
mkdir -p "$DIST_PATH/bin"
python3 -m PyInstaller morpheus/__main__.py \
  --name morpheus \
  --onefile \
  --distpath "$DIST_PATH/bin"  \
  --noconfirm \
  --paths=/morpheus
# cp -r morpheus/Test_bench_definitions $DIST_PATH/CMOSGUI/morpheus

# SKILL
cp -rf skill "$DIST_PATH/"
find "$DIST_PATH/skill" -name ".skillide.*" -delete

#Configs
echo "  copy testbench configs to $DIST_PATH"
cp -rf morpheus/Test_bench_definitions "$DIST_PATH/bin/"

# Python package
flit build
mkdir "$DIST_PATH/packages"
mv dist/morpheus-*.whl "$DIST_PATH/packages/"
mv dist/morpheus-*.tar.gz "$DIST_PATH/packages/"

# cp morpheus.cshrc "$DIST_PATH/"
# cp morpheus.bashrc "$DIST_PATH/"

chmod 775 $DIST_PATH

#symbolic link (broken?)
ln -s -f v$VERSION/bin/morpheus dist/morpheus

echo "  build saved to $DIST_PATH"
echo "  build complete!"  
