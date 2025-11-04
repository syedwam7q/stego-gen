# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-01-XX

### Added
- **Algorithm Comparison Page** with detailed scoring system
  - Side-by-side comparison of any two algorithms
  - Scoring metrics: Capacity (0-100), Security (0-100), Robustness (0-100), Complexity (0-100)
  - Animated progress bars with winner highlighting
  - Detailed explanations for each metric
- **File Upload for AI Recommendations** on Compare page
  - Drag-and-drop file upload interface
  - Ranked algorithm suggestions with match percentages
  - File statistics display (dimensions, entropy, variance, texture)
  - Winner highlighted with trophy emoji and green border
- **MIT License** for open-source distribution
- **Contributing Guidelines** (CONTRIBUTING.md)
- **GitHub Issue Templates** (Bug Report, Feature Request)
- **GitHub PR Template**
- **Professional README** with badges, tables, and comprehensive documentation

### Fixed
- **Blurry Text on Stat Cards** - Replaced CSS gradient-clip with solid colors
  - Affected: PSNR values, SSIM values, capacity percentages
  - Files: `frontend/src/App.css`, `frontend/src/components/Home.css`
  - Result: Crystal-clear readability across all browsers
- **Algorithm Comparison "Depends" Issue** - Implemented comprehensive scoring system
  - Previous: Generic "Depends" for most comparisons
  - Now: Specific scores with dynamic winner calculation
  - File: `backend/stego/ai_explainer.py`

### Changed
- **Algorithm Comparison Logic** - Complete rewrite of `_fallback_comparison()` method
  - Dynamic scoring for all algorithm pairs (25+ combinations)
  - Objective, data-driven comparisons
  - Consistent explanations
- **UI/UX Polish** across all pages
  - Improved typography hierarchy
  - Enhanced hover states and animations
  - Better mobile responsiveness
  - Consistent color scheme using CSS variables

### Improved
- **Documentation Quality**
  - Comprehensive README with 2000+ lines
  - Professional formatting with badges and tables
  - Clear API reference with examples
  - Algorithm details with technical specifications
  - Security best practices section
- **Code Organization**
  - Better separation of concerns
  - Improved error handling
  - Consistent naming conventions

---

## [2.0.0] - 2025-11-XX

### Added
- **Multi-Algorithm Support**
  - LSB (Least Significant Bit) encoding/decoding
  - DCT (Discrete Cosine Transform) encoding/decoding
  - DWT (Discrete Wavelet Transform) encoding/decoding
  - Audio steganography (WAV)
  - Video steganography (MP4, AVI, MOV, MKV)
- **AI-Powered Recommendations** via Grok API
  - Intelligent parameter suggestions
  - Carrier analysis (entropy, variance, texture)
  - Goal-based optimization (max_invisibility, max_capacity)
  - Fallback scoring system for offline operation
- **Binary File Support** - Hide any file type
- **AES-256 Encryption** - Military-grade security
- **Quality Metrics** - PSNR and SSIM calculation
- **Modern React UI** with glassmorphism and dark mode
- **RESTful API** - 15+ FastAPI endpoints
- **CLI Tool** - Command-line interface for automation
- **Comprehensive Error Handling** and logging

### Changed
- Complete UI/UX overhaul
- Migrated to FastAPI from Flask
- React 18 with modern hooks
- Modular architecture

---

## [1.0.0] - 2024-XX-XX

### Added
- Initial release
- Basic LSB steganography
- Simple web interface
- Image encoding/decoding

---

## Upcoming Features

### Planned for v2.2.0
- [ ] Batch processing support
- [ ] Steganalysis detection mode
- [ ] Docker containerization
- [ ] Unit and integration tests
- [ ] Performance benchmarks
- [ ] API rate limiting

### Planned for v3.0.0
- [ ] Mobile app (React Native)
- [ ] Advanced AI features (custom model training)
- [ ] Custom encryption algorithms
- [ ] Real-time collaboration
- [ ] Cloud storage integration
- [ ] API key authentication

---

## Version Naming

- **Major** (X.0.0): Breaking changes, major feature additions
- **Minor** (0.X.0): New features, non-breaking changes
- **Patch** (0.0.X): Bug fixes, minor improvements

---

[2.1.0]: https://github.com/yourusername/steganoGen/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/yourusername/steganoGen/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/yourusername/steganoGen/releases/tag/v1.0.0