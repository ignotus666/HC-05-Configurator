#!/bin/bash
set -e

# Extract version from debian/control
VERSION=$(awk -F': ' '/^Version:/ {print $2; exit}' debian/control)
PKGDIR="hc05-configurator_${VERSION}"
PKGDEB="hc05-configurator_${VERSION}.deb"

# Clean previous build artifacts
rm -rf "$PKGDIR" "$PKGDEB"

# Create the directory structure
mkdir -p "$PKGDIR/usr/share/hc05-configurator/src"
mkdir -p "$PKGDIR/usr/bin"
mkdir -p "$PKGDIR/DEBIAN"
mkdir -p "$PKGDIR/usr/share/applications"

# Copy source files
cp -r src/* "$PKGDIR/usr/share/hc05-configurator/src/"

# Copy launcher script
cp debian/hc05-configurator.sh "$PKGDIR/usr/bin/hc05-configurator"
chmod +x "$PKGDIR/usr/bin/hc05-configurator"

# Copy desktop entry
cp debian/hc05-configurator.desktop "$PKGDIR/usr/share/applications/"

# Copy icon to the correct location for hicolor theme
mkdir -p "$PKGDIR/usr/share/icons/hicolor/48x48/apps/"
cp hc-05.png "$PKGDIR/usr/share/icons/hicolor/48x48/apps/hc-05.png"

# Copy control file
cp debian/control "$PKGDIR/DEBIAN/control"
# Copy postinst script for icon cache update
cp debian/postinst "$PKGDIR/DEBIAN/postinst"
chmod 755 "$PKGDIR/DEBIAN/postinst"

# Build the .deb package
fakeroot dpkg-deb --build "$PKGDIR"

# Clean up build directory after successful build
rm -rf "$PKGDIR"

echo "DEB package built: $PKGDEB"
