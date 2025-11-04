we need to focus on Ai implementation in the project.
1. 
2. AI-Assisted Report Generator
Goal: Auto-generate a technical report after each encode/decode.
Includes: Algorithm details, parameters, PSNR/SSIM, AI explanations, and visual comparisons.
Implementation: /api/ai/report
Uses Grok/OpenAI to write a short summary in human language.
Generates downloadable PDF (via reportlab).
3. AI-Explainer & Learning Assistant (Chat)
Purpose: Add an “Explain with AI” section in the UI.
Functionality:
Users can ask: “Why was DCT chosen instead of LSB?” or “What’s my risk level if I share this on Instagram?”
Uses OpenAI/Grok API to provide contextual explanations, referencing image analysis and algorithm logic.
Frontend: Chatbox on right side with contextual awareness of current session.
4. AI Steganalysis - new page that analyses images/video/ausio for steganography. and provides detailed report.