#!/bin/bash
set -e

# Clean previous build artifacts
rm -rf hc05-configurator_0.0.5 hc05-configurator_0.0.5.deb

# Create the directory structure
mkdir -p hc05-configurator_0.0.5/usr/share/hc05-configurator/src
mkdir -p hc05-configurator_0.0.5/usr/bin
mkdir -p hc05-configurator_0.0.5/DEBIAN
mkdir -p hc05-configurator_0.0.5/usr/share/applications

# Copy source files
cp -r src/* hc05-configurator_0.0.5/usr/share/hc05-configurator/src/

# Copy launcher script
cp debian/hc05-configurator.sh hc05-configurator_0.0.5/usr/bin/hc05-configurator
chmod +x hc05-configurator_0.0.5/usr/bin/hc05-configurator

# Copy desktop entry
cp debian/hc05-configurator.desktop hc05-configurator_0.0.5/usr/share/applications/

# Copy icon to the correct location for hicolor theme
mkdir -p hc05-configurator_0.0.5/usr/share/icons/hicolor/48x48/apps/
cp hc-05.png hc05-configurator_0.0.5/usr/share/icons/hicolor/48x48/apps/hc-05.png

# Copy control file
cp debian/control hc05-configurator_0.0.5/DEBIAN/control
# Copy postinst script for icon cache update
cp debian/postinst hc05-configurator_0.0.5/DEBIAN/postinst
chmod 755 hc05-configurator_0.0.5/DEBIAN/postinst

# Build the .deb package
fakeroot dpkg-deb --build hc05-configurator_0.0.5

echo "DEB package built: hc05-configurator_0.0.5.deb"
