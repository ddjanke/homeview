# Chore Icons Setup Guide

This guide explains how to use the Google Drive-based icon system in HomeView.

## Overview

Chores now display custom icons from a Google Drive folder that are automatically downloaded to the local `/static/icons/chores/` directory. The system supports:

- **Google Drive Integration**: Icons are stored in a Google Drive folder and synced locally
- **Icon-based chores**: Use icon names that correspond to files in the Google Drive folder
- **Fallback icons**: Default Font Awesome icons when no icon is specified

## Google Drive Setup

1. **Create a Google Drive folder** for your chore icons
2. **Upload icon files** (SVG, PNG, JPG) to this folder
3. **Set the folder ID** in your environment variables:
   ```bash
   export GOOGLE_DRIVE_ICONS_FOLDER_ID="your-folder-id-here"
   ```
4. **Icons are automatically downloaded** to `/static/icons/chores/` when you sync chores

## Local Icon Directory Structure

```
app/static/icons/chores/
├── trash.svg          # Downloaded from Google Drive
├── vacuum.png         # Downloaded from Google Drive
├── laundry.svg        # Downloaded from Google Drive
├── dishes.jpg         # Downloaded from Google Drive
└── cleaning.svg       # Downloaded from Google Drive
```

## How to Use Icons

### 1. Adding Icons to Chores

When creating or syncing chores from Google Sheets, you can specify an icon name in the `icon_name` field:

**Google Sheets Format:**
| Name | Assigned To | Frequency | Day | Icon Name |
|------|-------------|-----------|-----|-----------|
| Take out trash | John | daily | M | trash |
| Vacuum living room | Jane | weekly | Sa | vacuum |
| Do laundry | John | weekly | Su | laundry |

**Note:** 
- Icon names should match the filename (without extension) in your Google Drive folder
- Icons are automatically downloaded from Google Drive when you sync chores
- Completion status is managed locally in the database and is not synced with Google Sheets

### 2. Icon Priority

The system uses the following priority order:

1. **icon_name** - If specified, loads `/static/icons/chores/{icon_name}.svg`
2. **fallback** - If no icon_name exists, shows a default Font Awesome icon

### 3. Creating Custom Icons

To add your own icons:

1. Create SVG files in `/app/static/icons/chores/`
2. Use simple, clean designs that work well at small sizes
3. Name files without the `.svg` extension (e.g., `my-chore.svg` → icon_name: `my-chore`)
4. Ensure SVGs are optimized for web use

### 4. Icon Specifications

- **Format**: SVG
- **Size**: Optimized for 60px height display
- **Color**: Use `currentColor` or `#000000` for best theme compatibility
- **Style**: Simple, recognizable icons work best

## Database Schema

The `chores` table now includes:

```sql
icon_name VARCHAR(100)  -- Name of icon file (without .svg extension)
```

## Backward Compatibility

- Chores without icons will show a default Font Awesome icon
- The system gracefully handles missing icon files
- Completion status is preserved during Google Sheets sync

## Example Usage

```python
# Creating a chore with an icon
chore = Chore(
    name="Take out trash",
    assigned_to="John",
    frequency="daily",
    day_of_week="M",
    icon_name="trash"  # This will load /static/icons/chores/trash.svg
)
```

## Troubleshooting

- **Icon not showing**: Check that the SVG file exists in `/static/icons/chores/`
- **Icon name mismatch**: Ensure the `icon_name` field matches the filename (without .svg)
- **Fallback showing**: The system will show a default icon if the specified icon file is missing
