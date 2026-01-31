#!/bin/bash
set -e

# Define version and paths
VERSION="0.1.0"
NAME="see"
DIR_NAME="${NAME}-${VERSION}"
TAR_NAME="${DIR_NAME}.tar.gz"

echo "Creating source tarball for ${NAME} version ${VERSION}..."

# Clean up previous attempts
rm -rf "${DIR_NAME}" "${TAR_NAME}"

# Create correct directory structure
mkdir -p "${DIR_NAME}"
cp -r see src etc LICENSE README.md setup.py "${DIR_NAME}/"

# Create tarball
tar -czf "${TAR_NAME}" "${DIR_NAME}"
echo "Created ${TAR_NAME}"

# Clean up temp dir
rm -rf "${DIR_NAME}"

# Move to RPM sources
DEST="$HOME/rpmbuild/SOURCES/${TAR_NAME}"
if [ -d "$HOME/rpmbuild/SOURCES" ]; then
    cp "${TAR_NAME}" "$DEST"
    echo "Copied to $DEST"
else
    echo "RPM sources directory not found at $HOME/rpmbuild/SOURCES"
    echo "   You may need to run: rpmdev-setuptree"
fi

echo ""
echo "Now you can run:"
echo "rpmbuild -ba ~/rpmbuild/SPECS/see.spec"
