#!/bin/bash

# Script to integrate narytree module into CPython build system

echo "Integrating N-ary Tree module into CPython..."

# Check if we're in the CPython root directory
if [ ! -f "configure" ]; then
    echo "Error: This script must be run from CPython root directory"
    exit 1
fi

# Check if narytree files exist
if [ ! -f "Modules/narytreemodule.cpp" ]; then
    echo "Error: narytreemodule.cpp not found in Modules/"
    exit 1
fi

if [ ! -f "Modules/nary_tree.cpp" ]; then
    echo "Error: nary_tree.cpp not found in Modules/"
    exit 1
fi

# Check if Setup.stdlib already has narytree entry
if grep -q "narytree narytreemodule.cpp" Modules/Setup.stdlib; then
    echo "✓ N-ary tree module already configured in Setup.stdlib"
else
    echo "Adding narytree to Setup.stdlib..."
    # Add narytree module to Setup.stdlib after the spatial data structures comment
    if grep -q "# Spatial data structures" Modules/Setup.stdlib; then
        echo "✓ Spatial data structures section found"
    else
        echo "Adding spatial data structures section..."
        sed -i '/# build supports subinterpreters/,/^$/a\\n# Spatial data structures\nnarytree narytreemodule.cpp' Modules/Setup.stdlib
    fi
fi

# Build CPython with the new module
echo "Configuring CPython build..."
if ./configure --enable-optimizations; then
    echo "✓ Configuration successful"
else
    echo "✗ Configuration failed"
    exit 1
fi

echo "Building CPython..."
if make -j$(nproc); then
    echo "✓ Build successful"
else
    echo "✗ Build failed"
    exit 1
fi

echo "Testing narytree module..."
if ./python -c "import narytree; print('✓ N-ary tree module imported successfully')"; then
    echo "✓ N-ary tree module integration complete!"
else
    echo "✗ N-ary tree module import failed"
    exit 1
fi

echo ""
echo "N-ary tree is now available as a built-in module in CPython!"
echo "Usage example:"
echo "  import narytree"
echo "  tree = narytree.NaryTree('root')"
echo "  root = tree.root()"
echo "  root.add_child('child1')"