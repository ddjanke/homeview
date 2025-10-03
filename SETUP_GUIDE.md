# HomeView Setup Guide

## 🚀 **Complete Setup Process**

### **Step 1: Google API Setup**

#### **1.1 Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "HomeView" (or any name you prefer)
4. Click "Create"

#### **1.2 Enable Required APIs**
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for and enable these APIs:
   - **Google Calendar API**
   - **Google Sheets API**

#### **1.3 Create OAuth2 Credentials**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Add these authorized redirect URIs:
   - `http://localhost:5000/auth/callback` (for local testing)
   - `http://YOUR_PI_IP:5000/auth/callback` (replace with your Pi's IP)
5. Click "Create"
6. Download the JSON file and save it as `credentials/google_credentials.json`

### **Step 2: Google Sheets Setup**

#### **2.1 Create Your Google Sheet**
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new sheet
3. Add two tabs: "Chores" and "Todos"
4. Set up the columns as shown in `GOOGLE_SHEETS_SETUP.md`

#### **2.2 Get Your Sheet ID**
1. Open your Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
3. Copy the `SHEET_ID_HERE` part

#### **2.3 Update Configuration**
Edit `config.py` and replace:
```python
GOOGLE_SHEETS_ID = "your-google-sheet-id-here"
```
with your actual Sheet ID.

### **Step 3: Run the Application**

#### **3.1 Install Dependencies**
```bash
pyenv activate homeview
pip install -r requirements.txt
```

#### **3.2 Start the Application**
```bash
python run.py
```

#### **3.3 Access the Application**
1. Open your browser
2. Go to `http://localhost:5000` (or your Pi's IP)
3. You'll see the login page

### **Step 4: First Login and Sync**

#### **4.1 Login Process**
1. Click "Sign in with Google"
2. You'll be redirected to Google's login page
3. Sign in with your Google account
4. Grant permissions for Calendar and Sheets access
5. You'll be redirected back to the app

#### **4.2 Sync Your Data**
1. **Calendar**: Click the "Calendar" tab → "Refresh Calendar"
2. **Chores**: Click the "Chores" tab → "Sync from Sheets"
3. **Todos**: Click the "Todos" tab → "Sync from Sheets"
4. **Weather**: Click the "Weather" tab → "Refresh"

### **Step 5: Configure Your Data**

#### **5.1 Add Chores to Google Sheets**
1. Open your Google Sheet
2. In the "Chores" tab, add your chores:
   - Column A: Chore name
   - Column B: Assigned to (person)
   - Column C: Frequency (Daily, Weekly, etc.)
   - Column D: Day of week
   - Column E: Image URL (optional)
   - Column F: Description (optional)
3. Click "Sync from Sheets" in the app

#### **5.2 Add Todos to Google Sheets**
1. In the "Todos" tab, add your todos:
   - Column A: Title
   - Column B: Description
   - Column C: Priority (1-10)
   - Column D: Category (optional)
   - Column E: Due date (YYYY-MM-DD)
   - Column F: Assigned to (optional)
2. Click "Sync from Sheets" in the app

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"Login failed" Error**
- Check that `credentials/google_credentials.json` exists
- Verify the redirect URI matches your setup
- Make sure the Google APIs are enabled

#### **"No chores found" Message**
- Check that your Google Sheet ID is correct in `config.py`
- Verify the sheet has a "Chores" tab with data
- Make sure you've granted Sheets access during login

#### **Calendar not loading**
- Check that you've granted Calendar access during login
- Verify the Google Calendar API is enabled
- Try refreshing the calendar

#### **Images not showing in chores**
- Make sure image URLs are direct links (ending in .jpg, .png, etc.)
- Test the URLs in your browser first
- Check that the URLs are publicly accessible

### **File Structure Check**
Make sure you have these files:
```
homeview/
├── credentials/
│   └── google_credentials.json  ← Your OAuth2 credentials
├── config.py                    ← Updated with your Sheet ID
├── run.py
└── app/
    └── ...
```

## 🎯 **Next Steps**

1. **Customize your data** in Google Sheets
2. **Add images** to your chores for better visual recognition
3. **Set up your Raspberry Pi** for deployment
4. **Configure weather location** in `config.py` if needed

## 📱 **Using the App**

- **Hold the "Hold to Complete" button** and tap chores/todos to mark them complete
- **Sync regularly** to keep data up to date
- **Edit in Google Sheets** for changes that sync back to the app
- **Use the weather tab** for current conditions and forecast

## 🔒 **Security Notes**

- Your Google credentials are stored locally
- The app only reads your calendar and sheets (no writing to calendar)
- All data stays in your Google account
- Use HTTPS in production for better security
