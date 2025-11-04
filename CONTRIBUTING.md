# Contributing to StegoGen

Thank you for your interest in contributing to StegoGen! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to:

- Be respectful and considerate
- Accept constructive criticism gracefully
- Focus on what is best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Trolling, insulting comments, or personal attacks
- Publishing private information without permission
- Any conduct that could be considered inappropriate

---

## How Can I Contribute?

### 1. Report Bugs

Found a bug? Please check if it's already reported in [Issues](https://github.com/yourusername/steganoGen/issues). If not, create a new issue with:

- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, browser)

### 2. Suggest Enhancements

Have an idea? Open an issue with:

- Clear description of the feature
- Use cases and benefits
- Possible implementation approach
- Any relevant examples

### 3. Submit Code

- Fix bugs
- Implement new features
- Improve documentation
- Add tests
- Optimize performance

### 4. Improve Documentation

- Fix typos or clarify existing docs
- Add examples and tutorials
- Translate documentation
- Create video guides

---

## Development Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- Git
- FFmpeg (for video processing)

### Initial Setup

```bash
# Fork and clone repository
git clone https://github.com/YOUR_USERNAME/steganoGen.git
cd steganoGen

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings

# Frontend setup
cd ../frontend
npm install
```

### Running Development Servers

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

---

## Coding Standards

### Python (Backend)

**Follow PEP 8 Style Guide**

```python
# Good
def encode_message(carrier_path: str, payload: bytes, bits: int = 1) -> str:
    """
    Encode message into carrier image using LSB.
    
    Args:
        carrier_path: Path to carrier image
        payload: Bytes to encode
        bits: Bits per channel (1-4)
        
    Returns:
        Path to stego image
    """
    pass

# Bad
def EncodeMsg(c,p,b=1):  # No docstring, unclear names
    pass
```

**Code Structure**:
- Use type hints
- Write docstrings for all functions/classes
- Keep functions focused and under 50 lines
- Use meaningful variable names
- Add comments for complex logic

**Error Handling**:
```python
# Good
try:
    image = Image.open(path)
except FileNotFoundError:
    logger.error(f"Carrier file not found: {path}")
    raise HTTPException(status_code=404, detail="Carrier file not found")
except Exception as e:
    logger.error(f"Error opening image: {e}")
    raise HTTPException(status_code=500, detail="Image processing failed")

# Bad
try:
    image = Image.open(path)
except:  # Too broad
    pass  # Silent failure
```

### JavaScript/React (Frontend)

**Follow ES6+ Standards**

```javascript
// Good - Functional component with hooks
const Encode = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleEncode = async () => {
    setLoading(true);
    try {
      const response = await apiClient.encode(file);
      // Handle response
    } catch (error) {
      console.error('Encoding failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="encode-container">
      {/* JSX */}
    </div>
  );
};

// Bad - Class component, inconsistent naming
class encode extends React.Component {
  render() {
    return <div>...</div>;
  }
}
```

**Code Structure**:
- Use functional components with hooks
- Keep components under 300 lines
- Extract reusable logic into custom hooks
- Use meaningful prop names
- Add PropTypes or TypeScript

**CSS**:
```css
/* Good - Use CSS variables */
.button-primary {
  background: var(--accent-primary);
  color: var(--text-light);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}

/* Bad - Hardcoded values */
.button {
  background: #5b6edb;
  color: white;
  padding: 12px;
  border-radius: 8px;
}
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples**:

```bash
# Good
git commit -m "feat(encode): add DWT algorithm support"
git commit -m "fix(decode): handle empty payload gracefully"
git commit -m "docs(readme): update API reference"

# Bad
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "asdfasdf"
```

**Detailed Commit**:
```bash
git commit -m "feat(ui): add algorithm comparison page

- Implement side-by-side algorithm comparison
- Add scoring system (capacity, security, robustness)
- Add animated progress bars with winner highlighting
- Include file upload for AI recommendations

Closes #123"
```

---

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All tests pass

## Screenshots (if applicable)
![Screenshot](url)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
```

### Review Process

1. **Automated Checks**: CI/CD runs tests (if configured)
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: At least one maintainer approves
5. **Merge**: Maintainer merges PR

---

## Bug Reports

### Before Reporting

1. **Search existing issues**: Avoid duplicates
2. **Try latest version**: Bug may be fixed
3. **Gather information**: Logs, screenshots, steps

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Screenshots
![Screenshot](url)

## Environment
- OS: [e.g., macOS 13.0]
- Python: [e.g., 3.11.0]
- Browser: [e.g., Chrome 120]
- Node: [e.g., 18.0.0]

## Additional Context
Any other relevant information

## Possible Solution (optional)
Ideas on how to fix
```

---

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Problem It Solves
What problem does this address?

## Proposed Solution
How should this work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Mockups, examples, references

## Implementation Complexity
- [ ] Small (< 1 day)
- [ ] Medium (1-3 days)
- [ ] Large (> 3 days)
```

---

## Testing

### Backend Testing

```python
# Example test structure (when tests are added)
import pytest
from stego.lsb_encoder import encode_lsb

def test_lsb_encode_basic():
    result = encode_lsb(
        carrier_path="test.png",
        payload=b"secret",
        bits=1
    )
    assert result is not None
    assert os.path.exists(result)
```

### Frontend Testing

```javascript
// Example test structure (when tests are added)
import { render, screen, fireEvent } from '@testing-library/react';
import Encode from './Encode';

test('renders encode button', () => {
  render(<Encode />);
  const button = screen.getByText(/Encode Now/i);
  expect(button).toBeInTheDocument();
});
```

---

## Documentation Standards

### Code Documentation

```python
def analyze_image(image_path: str, goal: str = "max_invisibility") -> dict:
    """
    Analyze image characteristics for steganography.
    
    Calculates entropy, variance, texture score, and edge density
    to determine optimal embedding parameters.
    
    Args:
        image_path (str): Path to image file
        goal (str): Optimization goal - "max_invisibility" or "max_capacity"
        
    Returns:
        dict: Analysis results containing:
            - dimensions (tuple): Width and height
            - entropy (float): Shannon entropy (0-8)
            - variance (float): Pixel variance
            - texture_score (float): Texture complexity
            - edge_density (float): Edge pixel ratio (0-1)
            
    Raises:
        FileNotFoundError: If image_path doesn't exist
        ValueError: If goal is invalid
        
    Example:
        >>> stats = analyze_image("carrier.png")
        >>> print(stats['entropy'])
        7.45
    """
    pass
```

### README Updates

- Keep sections organized
- Update version numbers
- Add examples for new features
- Include screenshots/GIFs
- Update API reference

---

## Questions?

- 📧 Email: [wamiqworkspace@example.com](mailto:wamiqworkspace@example.com)
- 💬 Discussions: [GitHub Discussions](https://github.com/syedwam7q/steganoGen/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/syedwam7q/steganoGen/issues)

---

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing to StegoGen! 🎉
