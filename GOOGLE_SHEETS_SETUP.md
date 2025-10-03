# Google Sheets Setup for HomeView

## Overview
The HomeView app uses a **single Google Sheet** with two tabs to manage chores and todos. You can use any existing Google Sheet or create a new one.

## Required Sheet Structure

### 1. Create or Use an Existing Google Sheet
- Go to [Google Sheets](https://sheets.google.com)
- Create a new sheet or use an existing one
- Copy the **Sheet ID** from the URL (the long string between `/d/` and `/edit`)

### 2. Sheet Tabs Required

#### Tab 1: "Chores" 
**Columns (A through G):**
- **A**: Chore Name (e.g., "Take out trash")
- **B**: Assigned To (e.g., "John", "Sarah", "Kids")
- **C**: Frequency (e.g., "Daily", "Weekly", "Monthly")
- **D**: Day of Week (e.g., "Monday", "Tuesday", "Any")
- **E**: Image URL (optional, e.g., "https://example.com/trash-icon.png")
- **F**: Description (optional)
- **G**: Completed Status (TRUE/FALSE) - **This will be updated by the app**

**Example Chores Tab:**
```
A                | B      | C       | D        | E                                    | F                    | G
Take out trash   | John   | Daily   | Any      | https://example.com/trash-icon.png   | Empty all trash cans | FALSE
Vacuum living room| Sarah  | Weekly  | Saturday | https://example.com/vacuum-icon.png | Vacuum and mop       | FALSE
Clean bathroom   | Kids   | Weekly  | Sunday   | https://example.com/bathroom-icon.png| Clean toilet, sink   | FALSE
```

#### Tab 2: "Todos"
**Columns (A through G):**
- **A**: Title (e.g., "Buy groceries")
- **B**: Description (e.g., "Milk, bread, eggs")
- **C**: Priority (1-10, where 10 is highest priority)
- **D**: Category (optional, e.g., "Shopping", "Work")
- **E**: Due Date (YYYY-MM-DD format, optional)
- **F**: Assigned To (optional)
- **G**: Completed Status (TRUE/FALSE) - **This will be updated by the app**

**Example Todos Tab:**
```
A              | B                    | C | D         | E          | F    | G
Buy groceries  | Milk, bread, eggs    | 8 | Shopping  | 2024-01-15 | John | FALSE
Fix leaky faucet| Replace washer      | 6 | Home      | 2024-01-20 | John | FALSE
Call dentist   | Schedule checkup     | 4 | Health    | 2024-01-25 | Sarah| FALSE
```

## Configuration

### 1. Set the Sheet ID
Update your `config.py` file or set an environment variable:

```python
# In config.py, change this line:
GOOGLE_SHEETS_ID = "your-google-sheet-id-here"

# Or set an environment variable:
export GOOGLE_SHEETS_ID="your-actual-sheet-id"
```

### 2. Get Your Sheet ID
1. Open your Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
3. Copy the `SHEET_ID_HERE` part

## How It Works

1. **Sync from Sheets**: The app reads data from your Google Sheet and stores it locally
2. **Complete Items**: When you complete a chore or todo, the app updates both:
   - The local database (for fast display)
   - The Google Sheet (for persistence and external editing)
3. **External Editing**: You can edit the sheet directly in Google Sheets, and the app will sync the changes

## Permissions Required

The app needs these permissions for your Google account:
- **Read** your Google Calendar events
- **Read and Write** your Google Sheets

## First Time Setup

1. Create your Google Sheet with the structure above
2. Update `config.py` with your Sheet ID
3. Run the app and click "Sync from Sheets" in the Chores and Todos tabs
4. The app will populate with your data and start tracking completions

## Tips

- **Header Row**: Keep the first row as headers (the app skips it)
- **Data Types**: 
  - Priority must be a number (1-10)
  - Due dates must be in YYYY-MM-DD format
  - Completed status will be automatically managed by the app
- **Empty Cells**: The app handles missing data gracefully
- **Multiple People**: You can assign chores/todos to different people for better organization
- **Image URLs**: 
  - Use direct image URLs (ending in .jpg, .png, .gif, etc.)
  - Images will be displayed as 60px high thumbnails in chore tiles
  - If an image fails to load, it will be hidden automatically
  - Good sources: Google Drive (make public), Imgur, or your own web server
