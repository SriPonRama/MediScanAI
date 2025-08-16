# 🚀 MediScan AI - Startup Guide

## 📋 **Quick Start Options**

### **Option 1: Double-Click Startup (Easiest)**
1. **Double-click** `start_mediscan.bat` in the project folder
2. **Wait** for the application to start
3. **Open browser** and go to: http://localhost:5000
4. **Login** with: demo@mediscan.com / demo123

### **Option 2: PowerShell Startup**
1. **Right-click** `start_mediscan.ps1` → "Run with PowerShell"
2. **Follow** the on-screen instructions
3. **Access** the application at: http://localhost:5000

### **Option 3: Manual Command Line**
```bash
# Open Command Prompt or PowerShell
cd "Documents\augment-projects\DS PROJECT"
python app.py
```

---

## 🔄 **How to Use MediScan AI**

### **Starting the Application:**
1. **Run** any of the startup methods above
2. **Wait** for "Running on http://127.0.0.1:5000" message
3. **Open browser** and navigate to: http://localhost:5000

### **Stopping the Application:**
- **Press** `Ctrl + C` in the terminal window
- **Close** the command prompt/PowerShell window

### **Accessing from Other Devices:**
- **Same Network**: Replace `localhost` with your computer's IP address
- **Example**: http://192.168.1.100:5000

---

## 🏠 **Making it Always Available**

### **Option A: Desktop Shortcut**
1. **Right-click** on `start_mediscan.bat`
2. **Select** "Create shortcut"
3. **Move shortcut** to Desktop
4. **Double-click** shortcut whenever you want to use the app

### **Option B: Windows Startup (Auto-start)**
1. **Press** `Win + R`
2. **Type** `shell:startup` and press Enter
3. **Copy** `start_mediscan.bat` to this folder
4. **App will start** automatically when Windows boots

### **Option C: Windows Service (Advanced)**
- Install as a Windows service for always-on operation
- Requires additional setup with tools like NSSM

---

## 🌐 **Deployment Options**

### **Local Network Access:**
```bash
# Modify app.py to allow network access
app.run(debug=True, host='0.0.0.0', port=5000)
```
- **Access from any device** on your network
- **Use your computer's IP**: http://192.168.1.XXX:5000

### **Cloud Deployment (Always Online):**

#### **1. Heroku (Free Tier)**
```bash
# Install Heroku CLI
# Create Procfile: web: gunicorn app:app
heroku create your-mediscan-app
git push heroku main
```

#### **2. Railway (Easy Deployment)**
1. **Connect** GitHub repository to Railway
2. **Deploy** automatically
3. **Get** permanent URL like: https://your-app.railway.app

#### **3. Render (Free Hosting)**
1. **Connect** repository to Render
2. **Set** build command: `pip install -r requirements.txt`
3. **Set** start command: `gunicorn app:app`

---

## 📱 **Mobile Access**

### **Local Network:**
1. **Start** MediScan AI on your computer
2. **Find your computer's IP** (ipconfig in cmd)
3. **Open browser** on phone/tablet
4. **Navigate** to: http://YOUR_COMPUTER_IP:5000

### **Cloud Deployment:**
- **Deploy** to cloud platform
- **Access** from anywhere with internet
- **Works** on any device with a web browser

---

## 🔧 **Troubleshooting**

### **Common Issues:**

#### **"Python not found"**
- **Install Python** 3.8+ from https://python.org
- **Check** "Add to PATH" during installation

#### **"Port already in use"**
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process
taskkill /PID <PID_NUMBER> /F
```

#### **"Module not found"**
```bash
# Install dependencies
pip install -r requirements.txt
```

#### **Database errors**
```bash
# Reinitialize database
python init_db.py
```

---

## 📊 **Performance Tips**

### **For Better Performance:**
- **Close** unnecessary applications
- **Use** Chrome or Edge browser
- **Ensure** good internet connection for translations
- **Keep** Python and dependencies updated

### **For Production Use:**
```bash
# Use production server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🎯 **Recommended Setup**

### **For Personal Use:**
1. **Create desktop shortcut** to `start_mediscan.bat`
2. **Bookmark** http://localhost:5000 in browser
3. **Start app** when needed, stop when done

### **For Team/Office Use:**
1. **Deploy to cloud** (Railway/Render)
2. **Share permanent URL** with team
3. **Always accessible** from anywhere

### **For Development:**
1. **Use manual command line** for testing
2. **Keep terminal open** for debugging
3. **Use debug mode** for development

---

## 📋 **Quick Reference**

### **Start Commands:**
- **Windows**: Double-click `start_mediscan.bat`
- **PowerShell**: `.\start_mediscan.ps1`
- **Command Line**: `python app.py`

### **Access URLs:**
- **Local**: http://localhost:5000
- **Network**: http://YOUR_IP:5000
- **Cloud**: https://your-app.platform.com

### **Demo Login:**
- **Email**: demo@mediscan.com
- **Password**: demo123

### **Stop Application:**
- **Press**: Ctrl + C
- **Close**: Terminal window

---

## 🎉 **You're All Set!**

**MediScan AI is now ready to use whenever you want!**

Choose the startup method that works best for you:
- **Quick use**: Double-click `start_mediscan.bat`
- **Always available**: Deploy to cloud
- **Network sharing**: Modify host settings

**Happy diagnosing with MediScan AI!** 🏥✨
