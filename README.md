# 🚀 Form Auto-Filler - Complete Web Application

**Full-Stack Form Automation Solution with Frontend + Backend Integration**

---

## 📦 Package Contents

```
form-auto-filler/
│
├── form_filler_app.html          # Frontend (Web Interface)
├── backend_server.py              # Backend (Flask Server)
├── auto_contact_form_complete.py  # Automation Engine
├── requirements.txt               # Python Dependencies
└── SETUP_GUIDE.md                 # This file
```

---

## 🎯 How It Works

```
┌─────────────┐      HTTP       ┌─────────────┐      Python      ┌─────────────┐
│             │   Requests      │             │    Subprocess    │             │
│  Frontend   │ ──────────────> │   Flask     │ ───────────────> │  Playwright │
│   (HTML)    │                 │  Backend    │                  │  Automation │
│             │ <────────────── │   (API)     │ <─────────────── │   Engine    │
└─────────────┘    Response     └─────────────┘     Logs         └─────────────┘
```

1. **Frontend**: User enters Google Sheet URL
2. **Backend**: Flask server receives request and starts Python script
3. **Automation**: Playwright fills forms on websites from CSV data
4. **Real-time Updates**: Logs stream back to frontend

---

## 🛠️ Installation

### Step 1: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 2: Verify Installation

```bash
# Check Python
python --version  # Should be 3.8+

# Check Flask
flask --version

# Check Playwright
playwright --version
```

---

## 🚀 Usage

### Method 1: Using Web Interface (Recommended)

**Step 1: Start Backend Server**
```bash
python backend_server.py
```

You should see:
```
🚀 FORM AUTO-FILLER - BACKEND SERVER
======================================================================
✅ Server starting on http://localhost:5000
📱 Open your browser and go to: http://localhost:5000
```

**Step 2: Open Browser**
- Go to: `http://localhost:5000`
- You'll see the web interface

**Step 3: Start Automation**
1. Paste your Google Sheet URL
2. Click "▶️ Start Automation"
3. Watch real-time progress in console
4. View statistics dashboard

**Step 4: Monitor Progress**
- Live console shows each step
- Statistics update in real-time
- Browser window opens showing form filling

**Step 5: Stop (Optional)**
- Click "⏹️ Stop" to halt automation
- Or let it complete automatically

### Method 2: Direct Python Script

```bash
# Run with command-line argument
python auto_contact_form_complete.py "YOUR_CSV_URL"

# Or set environment variable
export FORM_FILLER_CSV_URL="YOUR_CSV_URL"
python auto_contact_form_complete.py
```

---

## 📊 Google Sheet Format

### Required Format

Your Google Sheet should have these columns:

| website | name | email | phone | message |
|---------|------|-------|-------|---------|
| https://example1.com | John Doe | john@example.com | 9876543210 | Interested in services |
| https://example2.com | Jane Smith | jane@example.com | 9876543211 | Need information |

### Column Details

**Required:**
- `website` - Full website URL (must start with http:// or https://)

**Optional (will use defaults if empty):**
- `name` - Full name (splits into first/last automatically)
- `email` - Email address
- `phone` - Phone number
- `message` - Message/inquiry text
- `company` - Company name
- `job` - Job title
- `country`, `city`, `state` - Location information

### Making Sheet Publicly Accessible

1. Open your Google Sheet
2. Click "Share" button
3. Change to "Anyone with the link can view"
4. Copy the share link
5. Paste in the web interface

### URL Format

The app automatically converts any Google Sheets URL to CSV format:

**Input:**
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
```

**Auto-converted to:**
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0
```

---

## 🎨 Features

### Frontend Features
- ✅ Clean, modern interface
- ✅ Real-time console output
- ✅ Live statistics dashboard
- ✅ Auto URL conversion
- ✅ Error handling & validation
- ✅ Mobile responsive

### Backend Features
- ✅ RESTful API (Flask)
- ✅ Real-time log streaming
- ✅ Process management
- ✅ CORS enabled
- ✅ Error handling

### Automation Features
- ✅ Smart field detection (15+ types)
- ✅ Dropdown filling (5 strategies)
- ✅ Name splitting (first/last)
- ✅ Radio buttons & checkboxes
- ✅ CAPTCHA handling
- ✅ Chatbot removal (15+ types)
- ✅ Retry mechanism (2 attempts)
- ✅ Comprehensive logging
- ✅ JSON/CSV reports

---

## 🔧 Configuration

### Backend Server (`backend_server.py`)

```python
# Change server port (default: 5000)
app.run(port=5000)

# Change host (default: localhost)
app.run(host='0.0.0.0')  # Allow external connections
```

### Automation Engine (`auto_contact_form_complete.py`)

```python
class Config:
    # Animation speed
    ANIMATION_DELAY = 0.1  # Seconds between field fills
    
    # CAPTCHA timeout
    CAPTCHA_WAIT_TIME = 10  # Seconds to wait
    
    # Page load timeout
    PAGE_LOAD_TIMEOUT = 25000  # Milliseconds
    
    # Retry settings
    MAX_RETRIES = 2  # Number of retry attempts
    RETRY_DELAY = 2  # Seconds between retries
    
    # Browser settings
    HEADLESS = False  # Show browser window
    SLOW_MO = 50  # Slow down automation (ms)
```

---

## 🌐 API Endpoints

### Start Automation
```
POST /api/start
Body: { "csv_url": "YOUR_CSV_URL" }
Response: { "success": true, "message": "..." }
```

### Stop Automation
```
POST /api/stop
Response: { "success": true, "message": "Automation stopped" }
```

### Get Status
```
GET /api/status
Response: {
    "success": true,
    "data": {
        "running": true,
        "logs": [...],
        "stats": {
            "total": 10,
            "successful": 8,
            "failed": 2,
            "current": 5
        }
    }
}
```

### Get Logs
```
GET /api/logs
Response: {
    "success": true,
    "logs": [...]
}
```

---

## 🐛 Troubleshooting

### Issue 1: Backend Not Starting

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue 2: Can't Access http://localhost:5000

**Error:** `Connection refused`

**Solution:**
1. Make sure backend is running
2. Check terminal for errors
3. Try different port: `app.run(port=5001)`

### Issue 3: Frontend Shows "Backend Not Running"

**Solution:**
1. Start backend first: `python backend_server.py`
2. Wait for "Server starting" message
3. Refresh frontend page

### Issue 4: CSV Load Error

**Error:** `CSV load error: HTTP Error 403`

**Solution:**
1. Make sheet publicly accessible
2. Use "Anyone with link can view"
3. Check URL is correct

### Issue 5: Browser Not Opening

**Error:** `playwright._impl._api_types.Error`

**Solution:**
```bash
playwright install chromium
```

### Issue 6: Forms Not Filling

**Possible Causes:**
1. Website blocks automation (use CAPTCHA or bot detection)
2. Form structure is unusual
3. Fields are hidden/disabled

**Solution:**
- Check console logs for errors
- Try increasing timeouts in Config
- Some sites may not be compatible

### Issue 7: CAPTCHA Blocking

**Solution:**
- Script pauses for 10 seconds when CAPTCHA detected
- Solve CAPTCHA manually during pause
- Script continues after solving

---

## 📝 Best Practices

### 1. Testing
- Start with 1-2 websites first
- Verify CSV format is correct
- Check sheet is publicly accessible

### 2. Rate Limiting
- Don't spam forms
- Use reasonable delays
- Respect website terms of service

### 3. Data Quality
- Use real, accurate data
- Don't submit fake information
- Follow ethical guidelines

### 4. Monitoring
- Watch console output
- Check success/failure rates
- Review generated reports

### 5. Error Handling
- Script automatically retries failed submissions
- Logs are saved for review
- Reports generated at end

---

## 📈 Performance Tips

### Speed Optimization
```python
# Faster form filling
ANIMATION_DELAY = 0.05  # Reduce delay

# Headless mode (faster)
HEADLESS = True

# Reduce slow-mo
SLOW_MO = 20
```

### Memory Optimization
```python
# Process in batches
# Split large CSV into smaller files
# Run multiple times instead of one large run
```

---

## 🔒 Security Notes

1. **API Security**: Currently no authentication - don't expose to public internet
2. **Data Privacy**: CSV data visible to backend - use secure connection
3. **CORS**: Enabled for localhost only - adjust for production
4. **Input Validation**: Basic validation - add more for production use

### Production Recommendations
```python
# Add authentication
from flask_httpauth import HTTPBasicAuth

# Use HTTPS
app.run(ssl_context='adhoc')

# Rate limiting
from flask_limiter import Limiter

# Environment variables
import os
SECRET_KEY = os.getenv('SECRET_KEY')
```

---

## 📊 Generated Reports

After automation completes:

### JSON Report
```json
{
  "summary": {
    "total_websites": 10,
    "successful": 8,
    "failed": 2,
    "success_rate": "80.0%",
    "total_fields_filled": 75
  },
  "submissions": [...],
  "field_logs": [...]
}
```

### Files Created
- `report_YYYYMMDD_HHMMSS.json` - Detailed report
- `execution_logs.json` - Console logs

---

## 🎓 Example Workflow

```bash
# 1. Start backend
python backend_server.py

# 2. Open browser
# Go to http://localhost:5000

# 3. Prepare your Google Sheet
# Format: website, name, email, phone, message
# Make publicly accessible

# 4. Get sheet URL
# Share → Anyone with link can view → Copy link

# 5. Start automation
# Paste URL in web interface
# Click "Start Automation"

# 6. Monitor progress
# Watch console output
# View statistics
# Browser shows form filling

# 7. Review results
# Check success rate
# Review logs
# Download reports
```

---

## 🆘 Support

### Common Questions

**Q: Can I use my own CSV file?**
A: Yes, upload to Google Sheets and share publicly

**Q: Does it work on all websites?**
A: Most standard forms work. Some sites block automation.

**Q: Is it legal to use?**
A: Only use on legitimate forms with proper permissions

**Q: Can I run multiple instances?**
A: Yes, but use different ports for each backend

**Q: How fast does it run?**
A: ~10-30 seconds per website depending on complexity

---

## 🎉 Quick Start Summary

```bash
# 1. Install
pip install -r requirements.txt
playwright install chromium

# 2. Start Backend
python backend_server.py

# 3. Open Browser
http://localhost:5000

# 4. Enter Google Sheet URL

# 5. Click Start

# Done! ✅
```

---

## 📄 License

MIT License - Use responsibly and ethically

---

## 🤝 Contributing

Feel free to improve:
- Add new features
- Fix bugs
- Improve documentation
- Share feedback

---

**Version**: 3.0.0  
**Last Updated**: January 19, 2025  
**Author**: AI Development Team

---

### 🎊 Happy Automating!

Remember: Use this tool responsibly. Only submit forms you have permission to fill. Respect website terms of service and rate limits.