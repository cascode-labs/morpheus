#!/bin/bash
PROJECT="morpheus"
VERSION=$(cat version)
DIST_PATH="dist/v$VERSION"
echo "Building ${PROJECT} v$VERSION"
rm -rf "$DIST_PATH"
mkdir -p "$DIST_PATH"

# Executable
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
cp -rf morpheus/Test_bench_definitions "$DIST_PATH/"

# Python package
flit build
mkdir "$DIST_PATH/packages"
mv dist/morpheus-*.whl "$DIST_PATH/packages/"
mv dist/morpheus-*.tar.gz "$DIST_PATH/packages/"

# cp morpheus.cshrc "$DIST_PATH/"
# cp morpheus.bashrc "$DIST_PATH/"

chmod 775 $DIST_PATH

echo "  build saved to $DIST_PATH"
echo "  build complete!"
