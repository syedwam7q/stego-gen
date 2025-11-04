# 🚀 Quick Start Guide - AI-Enhanced StegoGen

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

---

## ⚡ Installation (5 minutes)

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure API Key (Optional)

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
GROK_API_KEY=your_grok_api_key_here
```

**Note:** The application works WITHOUT an API key using intelligent fallback logic, but AI features will be more powerful with Grok API access.

**Get Grok API Key:** https://x.ai

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Or with yarn
yarn install
```

---

## 🎬 Running the Application

### Terminal 1 - Backend:

```bash
cd backend
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: **http://localhost:8000**

### Terminal 2 - Frontend:

```bash
cd frontend
npm start

# Or with yarn
yarn start
```

Frontend will run on: **http://localhost:3000**

---

## ✨ Testing New AI Features

### 1. AI Chat Assistant 🤖

**How to access:**
- Look for the floating 🤖 button in the bottom-right corner
- Click it to open the AI chat

**Try these questions:**
```
- "What's the difference between LSB and DCT?"
- "How can I improve security?"
- "What is PSNR and why does it matter?"
- "Which algorithm should I use for social media?"
- "How to avoid detection?"
```

**Expected result:** Instant AI-powered answers with explanations

---

### 2. AI Steganalysis (Detection) 🔍

**How to access:**
- Click "Steganalysis" in the navigation menu
- Or go to: http://localhost:3000/steganalysis

**Test procedure:**
1. Upload any image (preferably one with or without hidden data)
2. Click "🔬 Run Steganalysis"
3. Wait 2-5 seconds for analysis
4. Review comprehensive detection report

**What to expect:**
- Overall detection score (0-100)
- Color-coded results (red = suspicious, green = clean)
- 6 different detection tests:
  - LSB Pattern Analysis
  - Chi-Square Test
  - RS Steganalysis
  - Histogram Analysis
  - Visual Attack
  - Statistical Analysis
- AI-powered interpretation
- Detailed recommendations

---

### 3. Enhanced Encoding with AI

**Test procedure:**
1. Go to "Encode" page
2. Upload a carrier image
3. Enter some secret text
4. Click "🤖 AI Analyze Image"
5. Review AI recommendation
6. Click "🔐 Encode Message"

**What's new:**
- AI analyzes your image texture and complexity
- Recommends optimal algorithm and settings
- Explains why these settings are best
- Shows detection risk level

---

### 4. Generate PDF Report 📄

**Test procedure:**
1. After encoding an image (follow step 3 above)
2. Call the report generation API:

```javascript
// In browser console or via API tool like Postman
const operationData = {
  algorithm: "LSB",
  carrier_info: {...},
  image_stats: {...},
  recommendation: {...},
  encode_result: {...},
  metrics: {...},
  settings: {...}
};

fetch('http://localhost:8000/api/ai/generate-report', {
  method: 'POST',
  body: new FormData().append('operation_data', JSON.stringify(operationData))
})
.then(res => res.json())
.then(data => console.log('Report URL:', data.download_url));
```

**Or integrate into UI** (future enhancement)

---

### 5. Security Risk Analysis 🛡️

**Test via API:**

```bash
curl -X POST http://localhost:8000/api/ai/security-analysis \
  -F "metrics={\"psnr\":42.5,\"ssim\":0.98,\"mse\":0.5}" \
  -F "algorithm=LSB" \
  -F "settings={\"bits_per_channel\":2,\"encryption_key\":true}"
```

**Expected response:**
```json
{
  "success": true,
  "analysis": {
    "risk_level": "low",
    "detection_probability": "5-15%",
    "vulnerabilities": [...],
    "mitigation_steps": [...],
    "platforms_analysis": {...},
    "summary": "..."
  }
}
```

---

### 6. Algorithm Comparison 📊

**Test via AI Chat:**
1. Open AI chat (🤖 button)
2. Ask: "Compare LSB and DCT algorithms"

**Or via API:**

```bash
curl -X POST http://localhost:8000/api/ai/compare-algorithms \
  -F "algorithm1=LSB" \
  -F "algorithm2=DCT"
```

**Expected response:**
- Winner for each category (capacity, security, robustness)
- Explanations
- Use case recommendations

---

## 🧪 Test Scenarios

### Scenario 1: Complete Workflow
```
1. Go to Encode page
2. Upload: backend/test_files/test_carrier.png
3. Enter text: "This is a secret message!"
4. Click AI Analyze → Review recommendation
5. Click Encode → Check metrics (PSNR, SSIM)
6. Download stego image
7. Go to Steganalysis page
8. Upload the stego image
9. Run analysis → See detection results
10. Ask AI chat: "Is this image safe to share on Instagram?"
```

### Scenario 2: Learning Mode
```
1. Open AI chat
2. Ask: "Explain LSB steganography"
3. Ask: "What makes an image good for hiding data?"
4. Ask: "How can someone detect my hidden message?"
5. Learn from AI responses!
```

### Scenario 3: Security Assessment
```
1. Encode a message with 4 bits per channel
2. Note the PSNR value
3. Use security analysis API
4. Review risk level (probably HIGH)
5. Re-encode with 1 bit per channel
6. Compare security assessments
```

---

## 📊 Quick Feature Checklist

Test each feature and check off:

- [ ] Backend server starts without errors
- [ ] Frontend loads successfully
- [ ] Can navigate to all pages (Home, Encode, Decode, Steganalysis)
- [ ] 🤖 AI chat button appears and opens
- [ ] AI chat responds to questions
- [ ] Steganalysis page loads
- [ ] Can upload and analyze images in Steganalysis
- [ ] Detection report shows all 6 tests
- [ ] Can encode messages with AI analysis
- [ ] AI recommendation appears after analysis
- [ ] Quality metrics (PSNR, SSIM) are calculated
- [ ] Can download encoded images
- [ ] Can decode messages

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
lsof -i :8000  # Kill any process using port 8000
```

### Frontend won't start
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 14+
```

### AI features not working
- **Check:** Is GROK_API_KEY set in .env? (Optional)
- **Fallback:** AI features still work without API key, just less powerful
- **Verify:** Check browser console for errors
- **Network:** Ensure backend is running and accessible

### Steganalysis page blank
- **Check:** Route added in App.js? ✓ (Already done)
- **Check:** Component imported? ✓ (Already done)
- **Check:** Browser console for errors
- **Clear:** Browser cache and reload

---

## 📸 Screenshots Expected

After setup, you should see:

1. **Home Page:** Clean, modern design with feature cards
2. **Encode Page:** File upload, AI analysis button, algorithm selection
3. **Steganalysis Page:** Detection interface with test results
4. **AI Chat:** Floating 🤖 button, opens modal with chat interface
5. **Navigation:** Home | Encode | Decode | Steganalysis | 🌙

---

## 🎯 Quick API Testing

Use these curl commands to test backend:

```bash
# Health check
curl http://localhost:8000/api/health

# AI chat
curl -X POST http://localhost:8000/api/ai/chat \
  -F "question=What is steganography?"

# Compare algorithms
curl -X POST http://localhost:8000/api/ai/compare-algorithms \
  -F "algorithm1=LSB" \
  -F "algorithm2=DCT"
```

---

## 🚀 Production Build

### Backend:
```bash
# Use production ASGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend:
```bash
cd frontend
npm run build

# Serve with static server
npm install -g serve
serve -s build -p 3000
```

---

## 📚 Next Steps

After successful setup:

1. **Explore AI Chat** - Ask it anything about steganography
2. **Try Steganalysis** - Test with various images
3. **Read Documentation** - Check `AI_FEATURES.md` for detailed info
4. **Experiment** - Try different algorithms and settings
5. **Learn** - Use AI assistant to understand concepts

---

## 💡 Pro Tips

1. **Use PNG for encoding** - Lossless format preserves hidden data
2. **Check PSNR** - Above 40dB is usually safe
3. **Ask AI first** - Use chat to understand before experimenting
4. **Test detection** - Run steganalysis on your encoded images
5. **Use encryption** - Always encrypt sensitive payloads

---

## 🎓 Learning Resources

- **In-app AI Chat** - Your best learning tool
- **AI_FEATURES.md** - Comprehensive feature documentation
- **Code Comments** - Well-documented codebase
- **API Docs** - http://localhost:8000/docs (FastAPI auto-docs)

---

## ✅ Success Indicators

You'll know everything is working when:

- ✅ All pages load without errors
- ✅ AI chat responds to questions
- ✅ Steganalysis shows detection results
- ✅ Images can be encoded/decoded
- ✅ Metrics are calculated correctly
- ✅ No console errors in browser
- ✅ Backend logs show successful requests

---

## 🎉 You're Ready!

If you can do all the test scenarios above, **you're all set!**

The platform is now a powerful, AI-enhanced steganography tool with professional-grade capabilities.

**Enjoy exploring the features! 🚀**

---

## 📧 Need Help?

1. **AI Chat** - Ask the built-in assistant first!
2. **Documentation** - Check `AI_FEATURES.md`
3. **Console Logs** - Check browser and backend logs
4. **Issues** - Verify all dependencies are installed

---

**Quick Start Complete! 🎊**

**Now go to:** http://localhost:3000 and start exploring!