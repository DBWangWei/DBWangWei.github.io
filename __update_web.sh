#!/bin/bash

# Set the source and destination directories
SRC_DIR="/Users/weiwang/Home/weiwcs.github.io"
DEST_DIR="/Users/weiwang/Home/dbwangwei.github.io"

# Step 1: Refresh generated publication artifacts

echo "Refreshing publication pages..."
python3 tools/publications/build_publications.py 2>&1 || { echo "Error generating publications: $?"; exit 1; }
echo "Publication refresh completed."

# Step 2: Run mkdocs build
echo "Running mkdocs build..."
mkdocs build 2>&1 || { echo "Error running mkdocs build: $?"; exit 1; }
echo "mkdocs build completed."

# Step 3: Create the destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating destination directory: $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

# Step 3: Remove all files and directories in DEST_DIR using git rm, if the directory is not empty
if [ "$(ls -A "$DEST_DIR")" ]; then
    echo "Removing all files and directories in $DEST_DIR using git rm..."
    cd "$DEST_DIR"
    git rm -rf . 2>&1 || { echo "Error running git rm: $?"; }
    cd "$SRC_DIR"
else
    echo "Destination directory is empty, skipping git rm."
fi

## Additional step: Must copy the CNAME (dbwangwei.github.io) back
echo "Copying ${SRC_DIR}/CNAME to $DEST_DIR ..."
cp -rf "$SRC_DIR/CNAME" "$DEST_DIR" 2>&1 || { echo "Error copying to $DEST_DIR: $?"; exit 1; }
echo "Copying completed."


# Step 4: Copy ./site to DEST_DIR
echo "Copying ${SRC_DIR}/site/ to $DEST_DIR ..."
cp -rf "$SRC_DIR/site/" "$DEST_DIR" 2>&1 || { echo "Error copying to $DEST_DIR: $?"; exit 1; }
echo "Copying completed."

# Step 5: Git add, commit, and push
echo "Pushing changes to $DEST_DIR..."
cd "$DEST_DIR"
git add . 2>&1 || { echo "Error running git add: $?"; exit 1; }
git commit -m "Update website" 2>&1 || { echo "Error running git commit: $?"; exit 1; }
git push 2>&1 || { echo "Error running git push: $?"; exit 1; }

echo "All steps completed successfully."