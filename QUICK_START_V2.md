# 🚀 StegoGen v2.0 - Quick Start Guide

## ⚡ TL;DR - Get Started in 2 Minutes

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm start

# Visit: http://localhost:3000
```

---

## 📦 What's New in v2.0?

### 🎯 **10 Major Enhancements**

1. **📊 Dashboard** - Overview of all operations with stats
2. **📐 Capacity Calculator** - Estimate data hiding capacity
3. **⚖️ Algorithm Comparison** - Side-by-side algorithm analysis
4. **📚 History Tracking** - Automatic operation logging
5. **⭐ Presets System** - Save and reuse favorite settings
6. **📱 Mobile Navigation** - Full responsive design
7. **⚙️ Configuration Management** - Environment-based config
8. **🎨 Enhanced UI** - Better design and animations
9. **🤖 Improved AI** - Context-aware assistance
10. **🔧 Better Architecture** - Cleaner, more maintainable code

---

## 🎯 New Pages & Features

### 1. Dashboard (`/dashboard`)
Your command center for steganography operations:
- **Real-time stats**: Total operations, data hidden, avg quality
- **Recent activity**: Last 5 operations at a glance
- **Quick actions**: Fast access to all features
- **Algorithm usage**: Visual breakdown of your preferences
- **AI tips**: Personalized recommendations

**When to use**: Start here to see overview of all your activity

---

### 2. Capacity Calculator (`/capacity`)
Calculate how much data you can hide:
- **Two modes**: 
  - Manual (enter dimensions manually)
  - Upload (analyze actual file)
- **Real-time calculation**: Instant capacity estimates
- **AI recommendations**: Optimal settings for your file
- **Quality analysis**: Entropy, texture, complexity scores

**When to use**: Before encoding to ensure your payload fits

**Example**:
- 1920×1080 image
- 1 bit/channel (LSB)
- Capacity: ~777 KB (enough for ~1,500 pages of text!)

---

### 3. Algorithm Comparison (`/compare`)
Choose the best algorithm for your needs:
- **Side-by-side comparison**: Any two algorithms
- **4 categories**: Capacity, Security, Robustness, Complexity
- **Visual winners**: Clear indication of best choice
- **AI explanations**: Why one wins over another
- **Use cases**: When to use each algorithm

**When to use**: Deciding between algorithms for your specific use case

**Quick Guide**:
- **LSB**: High capacity, fast, simple
- **DCT**: JPEG-safe, robust to compression
- **DWT**: Highest security, best quality
- **Audio**: For WAV files, inaudible
- **Video**: Massive capacity, multiple formats

---

## 🎨 UI Improvements

### Mobile Navigation
- **Hamburger menu** on screens < 968px
- **Smooth slide-out** animation
- **Touch-optimized** for mobile devices
- **Auto-close** on navigation

### Dropdown Menus
- **Tools menu** organizes features
- **Hover to expand** on desktop
- **Always visible** on mobile

### Better Visual Design
- **Gradient accents** for important elements
- **Glassmorphism effects** on cards
- **Smooth animations** throughout
- **Color-coded categories** for clarity

---

## 📚 Features Guide

### History System
**Automatic tracking** of all operations:

```javascript
// Automatically saved:
- Operation type (encode/decode/analyze)
- Algorithm used
- Payload size
- Quality metrics (PSNR, SSIM)
- Timestamp
```

**View your stats**:
- Total operations
- Data hidden (total bytes)
- Average quality scores
- Algorithm preferences

**Location**: Dashboard → Recent Activity

---

### Presets System
**Save time** with preset configurations:

**5 Default Presets**:
1. **Maximum Security** 🔒
   - 1 bit/channel, LSB, encrypted
   - Lowest detection risk

2. **Balanced** ⚖️
   - 2 bits/channel, LSB, encrypted
   - Good capacity + security

3. **Maximum Capacity** 📦
   - 4 bits/channel, LSB
   - Highest capacity

4. **Robust (DCT)** 🛡️
   - DCT algorithm, encrypted
   - Compression-resistant

5. **High Quality (DWT)** ⭐
   - DWT algorithm, encrypted
   - Best imperceptibility

**Create custom presets**:
- Save your favorite settings
- Quick apply in any operation
- Manage from Dashboard

---

## 🤖 AI Features

### Context-Aware Chat
AI assistant now understands:
- Current page you're on
- Algorithm you're using
- Your operation history
- Image characteristics

**Quick Questions**:
- "What's the difference between LSB and DCT?"
- "How can I improve security?"
- "What is PSNR and why does it matter?"
- "Which algorithm should I use?"

### Smart Recommendations
AI suggests:
- Best algorithm for your image
- Optimal bits per channel
- Security considerations
- Detection risk level

---

## 🔧 Configuration

### Environment Variables

**Frontend** (`.env`):
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
```

**Backend** (`.env`):
```bash
GROK_API_KEY=your_grok_api_key_here
```

### File Limits
- **Max image size**: 50 MB
- **Max payload**: 10 MB
- **History entries**: 50 (most recent)
- **Preset limit**: Unlimited

---

## 📱 Mobile Usage

### Responsive Design
- **Desktop**: Full features, dropdown menus
- **Tablet** (< 968px): Hamburger menu
- **Mobile** (< 768px): Optimized layout
- **Small** (< 480px): Compact mode

### Touch Gestures
- **Tap** to open mobile menu
- **Swipe** to close menu
- **Long press** on presets to edit (future)
- **Pull to refresh** dashboard (future)

---

## 🎯 Workflows

### Encoding Workflow
1. **Dashboard** → Check capacity needs
2. **Capacity Calculator** → Verify file can hold payload
3. **Algorithm Comparison** → Choose best algorithm
4. **Encode** → Perform encoding
5. **Dashboard** → View in history

### Security-First Workflow
1. **Compare** LSB vs DCT vs DWT
2. **Choose** DWT for max security
3. **Calculator** → Verify capacity
4. **Encode** with encryption + low bits
5. **Steganalysis** → Verify undetectable

### Quick Encode Workflow
1. **Dashboard** → "Start Encoding"
2. **Select preset** (e.g., "Balanced")
3. **Upload + Encode**
4. **Download** result

---

## 🐛 Troubleshooting

### Common Issues

**1. "API not responding"**
```bash
# Check backend is running
cd backend
python main.py

# Should see: "Application startup complete"
# Running on http://0.0.0.0:8000
```

**2. "Mobile menu not working"**
- Clear browser cache
- Try different browser
- Check console for errors

**3. "History not saving"**
- Check localStorage enabled
- Check browser privacy mode
- Clear cookies and retry

**4. "AI features not working"**
- Check GROK_API_KEY in backend/.env
- Fallback mode should still work
- Check console for API errors

**5. "Capacity calculator wrong"**
- Ensure proper image format
- Try manual mode first
- Check file isn't corrupted

---

## 📊 Performance Tips

### Frontend Optimization
```javascript
// Lazy load heavy components
const Dashboard = React.lazy(() => import('./components/Dashboard'));

// Use React.memo for expensive renders
const ExpensiveComponent = React.memo(Component);
```

### Backend Optimization
- Use streaming for large files
- Implement caching for analysis
- Queue batch operations
- Rate limit API calls

### Browser Tips
- Use Chrome/Firefox for best performance
- Enable hardware acceleration
- Close unused tabs
- Clear cache periodically

---

## 🎓 Best Practices

### Security
✅ **Always encrypt** sensitive data  
✅ **Use strong keys** (16+ characters)  
✅ **Choose high-texture images** for LSB  
✅ **Monitor PSNR** (keep > 40 dB)  
✅ **Test with Steganalysis** before sharing  

### Capacity
✅ **Calculate first** before encoding  
✅ **Start with 1 bit** if unsure  
✅ **Use DWT** for large payloads in quality  
✅ **Consider compression** for text  

### Workflow
✅ **Use presets** to save time  
✅ **Check history** to learn from past  
✅ **Compare algorithms** before committing  
✅ **Save good presets** for reuse  
✅ **Use Dashboard** as starting point  

---

## 🚀 Deployment

### Development
```bash
# Frontend
npm start

# Backend
python main.py
```

### Production

**Frontend**:
```bash
npm run build
# Serve from /build directory with nginx/apache
```

**Backend**:
```bash
# Use gunicorn or uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Docker** (recommended):
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
```

---

## 📈 Feature Comparison

### v1.0 vs v2.0

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Dashboard | ❌ | ✅ |
| Mobile Menu | ❌ | ✅ |
| History Tracking | ❌ | ✅ |
| Presets | ❌ | ✅ |
| Capacity Calculator | ❌ | ✅ |
| Algorithm Comparison | Backend Only | ✅ Full UI |
| Configuration | Hardcoded | ✅ Environment |
| Responsive | Partial | ✅ Full |
| Dropdown Menus | ❌ | ✅ |
| AI Context | Limited | ✅ Enhanced |

---

## 🎯 Keyboard Shortcuts (Future v3.0)

Planned shortcuts:
- `Ctrl+E` - Quick Encode
- `Ctrl+D` - Quick Decode
- `Ctrl+K` - Open AI Chat
- `Ctrl+H` - View History
- `Ctrl+P` - Load Preset
- `/` - Search/Focus

---

## 📞 Support

### Getting Help
1. Check this guide
2. See `ENHANCEMENTS_V2.md` for details
3. Check console for errors
4. Open AI chat for questions

### Reporting Issues
Include:
- Browser & version
- Steps to reproduce
- Error messages
- Screenshots (if UI issue)

---

## 🎉 Next Steps

### For Users
1. ✅ Explore new Dashboard
2. ✅ Try Capacity Calculator
3. ✅ Compare algorithms
4. ✅ Create custom presets
5. ✅ Check your history

### For Developers
1. ✅ Read `ENHANCEMENTS_V2.md`
2. ✅ Review new utilities
3. ✅ Understand config system
4. ✅ Explore component structure
5. ✅ Plan v3.0 features

---

## 🏆 Success Metrics

**Track your improvement**:
- Operations performed
- Average PSNR/SSIM scores
- Algorithms mastered
- Presets created
- Data successfully hidden

**View in Dashboard** → Statistics section

---

## 💡 Pro Tips

### 1. Master the Dashboard
- Use it as your daily starting point
- Check recent activity before new operations
- Monitor your quality trends

### 2. Create Smart Presets
- Save presets for different use cases
- Name them clearly ("Work Docs", "Photos", etc.)
- Include encryption settings

### 3. Use Comparison Tool
- Compare before important operations
- Learn algorithm strengths
- Build your expertise

### 4. Calculate Capacity First
- Avoid "payload too large" errors
- Plan payload size ahead
- Optimize compression if needed

### 5. Leverage AI Chat
- Ask about error messages
- Get security advice
- Learn algorithm details

---

**Ready to start? Visit http://localhost:3000 after setup!**

**Happy Steganography! 🎭🔐**

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Questions?** Ask the AI Assistant 🤖