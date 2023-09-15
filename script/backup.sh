#!/bin/bash
# Replace '/path/to/source/file' with the actual path to your source file
source_file="/etc/wireguard/wg0.conf"

# Replace '/path/to/backup/directory' with the actual path to your backup directory
backup_dir="/mnt/wg_backup"

# Create a backup filename with the current date and time
backup_filename="wg0_$(date +'%Y-%m-%d_%H-%M-%S').conf"

# Check if a file with the same backup filename already exists
if [ -e "$backup_dir/$backup_filename" ]; then
    echo "Backup file $backup_filename already exists. Skipping backup."
else
    # Copy the source file to the backup directory with the new filename
    cp "$source_file" "$backup_dir/$backup_filename"
    echo "Backup of $source_file created as $backup_filename"
fi