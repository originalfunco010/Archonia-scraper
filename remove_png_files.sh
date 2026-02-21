#!/bin/bash

# Bepaal de map waar dit script zelf staat
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Images map in dezelfde root als het script
folder_path="$script_dir/images"

# Check of folder bestaat
if [ -d "$folder_path" ]; then
    # Verwijder alle image bestanden
    find "$folder_path" \( -iname "*.png" -o -iname "*.webp" -o -iname "*.jpg" -o -iname "*.jpeg" \) -type f -exec rm -f {} \;
    echo "$(date): Alle PNG, JPG, JPEG en WEBP bestanden verwijderd uit $folder_path"
else
    echo "$(date): Map $folder_path bestaat niet"
fi