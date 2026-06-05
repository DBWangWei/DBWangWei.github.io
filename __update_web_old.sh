#!/bin/bash

# Set the destination directory
DEST_DIR="../dbwangwei.github.io"

# Step 1: Run mkdocs build
echo "Running mkdocs build..."
mkdocs build 2>&1 || { echo "Error running mkdocs build: $?"; exit 1; }
echo "mkdocs build completed."

# Step 2: Go to DEST_DIR directory
echo "Navigating to $DEST_DIR..."
pushd "$DEST_DIR" 2>&1 || { echo "Error navigating to $DEST_DIR: $?"; exit 1; }

# Step 3: Remove all files and directories in DEST_DIR using git rm
echo "Removing all files and directories in $DEST_DIR using git rm..."
git rm -rf . 2>&1 || { echo "Error running git rm: $?"; popd; exit 1; }

# Step 4: Copy ./site to DEST_DIR
echo "Copying ./site to $DEST_DIR..."
cp -rf ../../site/* . 2>&1 || { echo "Error copying to $DEST_DIR: $?"; popd; exit 1; }
echo "Copying completed."

# Step 5: Git add, commit, and push
echo "Pushing changes to $DEST_DIR..."
git add . 2>&1 || { echo "Error running git add: $?"; popd; exit 1; }
git commit -m "Update website" 2>&1 || { echo "Error running git commit: $?"; popd; exit 1; }
git push 2>&1 || { echo "Error running git push: $?"; popd; exit 1; }

# Step 6: Go back to the original directory
popd 2>&1 || { echo "Error navigating back to the original directory: $?"; exit 1; }

echo "All steps completed successfully."