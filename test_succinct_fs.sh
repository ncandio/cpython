#!/bin/bash

echo "=== Succinct Filesystem Test Script ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Build the module
echo "1. Building succinct filesystem module..."
make -f Makefile.succinct clean
make -f Makefile.succinct all

if [ $? -ne 0 ]; then
    echo "Failed to build module"
    exit 1
fi

echo "2. Loading succinct filesystem module..."
insmod succinct_fs.ko

if [ $? -ne 0 ]; then
    echo "Failed to load module"
    exit 1
fi

echo "3. Creating mount point..."
mkdir -p /mnt/succinct_test

echo "4. Mounting succinct filesystem..."
mount -t succinct none /mnt/succinct_test

if [ $? -ne 0 ]; then
    echo "Failed to mount filesystem"
    rmmod succinct_fs
    exit 1
fi

echo "5. Testing basic operations..."
cd /mnt/succinct_test

echo "Creating test files and directories..."
mkdir testdir
echo "Hello from succinct filesystem" > testfile.txt
mkdir testdir/subdir
echo "Nested file content" > testdir/nested.txt

echo "6. Listing filesystem contents..."
echo "Root directory:"
ls -la
echo
echo "Test directory:"
ls -la testdir/
echo

echo "7. Reading file contents..."
echo "Content of testfile.txt:"
cat testfile.txt
echo
echo "Content of testdir/nested.txt:"
cat testdir/nested.txt
echo

echo "8. Testing filesystem stats..."
df -h /mnt/succinct_test
echo

echo "9. Kernel log messages (last 10 lines):"
dmesg | tail -10 | grep succinct

echo
echo "=== Test completed successfully ==="
echo "To cleanup: sudo umount /mnt/succinct_test && sudo rmmod succinct_fs"