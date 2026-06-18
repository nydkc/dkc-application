#!/bin/sh

read -p "Are you sure you want to proceed with killing the Datastore emulator process? (y/n): " -n 1 -r
echo "" # Moves to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Nothing killed. Phew."
    exit 1
fi

echo "Killing..."
pkill -f "com.google.cloud.datastore.emulator.CloudDatastore"
pkill dsadmin
