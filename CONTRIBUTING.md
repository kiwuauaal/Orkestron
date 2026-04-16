# Contributing to Orkestron

Thank you for your interest in contributing to Orkestron! 🎉

We welcome contributions from everyone, regardless of experience level. This is an **open source** project, and we believe in the power of community collaboration.

## 🎯 How to Contribute

### 1. **Report Bugs** 🐛

Found a bug? Please open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your environment (OS, Python version, Node version)

### 2. **Suggest Features** 💡

Have an idea? We'd love to hear it!
- Open a feature request issue
- Explain the use case
- Describe the proposed solution
- Include any alternatives you've considered

### 3. **Submit Code** 💻

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/orkestron.git
   cd orkestron
   ```
3. **Set up the project**:
   ```bash
   setup.bat  # Windows
   # or
   pip install -r backend/requirements.txt
   ```
4. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

- **Code Style**: Follow PEP 8 for Python, ESLint for JavaScript/TypeScript
- **Testing**: Write tests for new features (we have 47 tests currently!)
- **Documentation**: Update docs if you change functionality
- **Commits**: Use clear, descriptive commit messages

#### Before Submitting

1. **Run tests**:
   ```bash
   pytest tests/test_suite.py -v
   ```
2. **Validate code**:
   ```bash
   python validate.py
   ```
3. **Update documentation** if needed

#### Submit Your Work

1. **Commit your changes**:
   ```bash
   git commit -m "feat: add amazing new feature"
   ```
2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Open a Pull Request** on GitHub

## 📋 Pull Request Guidelines

### PR Title Format
Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### PR Description
Include:
- What this PR does
- Why this change is needed
- How to test it
- Any breaking changes
- Related issues (use `Closes #123`)

### Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No breaking changes (or documented if any)

## 🚀 Development Workflow

1. **Pick an issue** or create one
2. **Comment** that you're working on it
3. **Fork and clone** the repository
4. **Create a feature branch**
5. **Make your changes**
6. **Test thoroughly**
7. **Submit a PR**
8. **Respond to feedback**
9. **Get merged!** 🎉

## 💡 Good First Issues

Look for issues labeled:
- `good first issue` - Perfect for beginners
- `help wanted` - We need your help!
- `bug` - Fix something broken
- `enhancement` - Improve existing features

## 🤝 Community Guidelines

### Be Respectful
- Treat everyone with respect
- Welcome newcomers
- Be constructive in feedback
- Assume good intentions

### Communication
- Use clear, concise language
- Link to relevant issues/PRs
- Ask questions if unsure
- Help others when you can

## 📝 Code of Conduct

We follow a Code of Conduct to ensure a welcoming community. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 🎓 Learning Resources

New to open source? Check out:
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Contributions](https://firstcontributions.github.io/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

## ❓ Questions?

- Open an issue with the `question` label
- Join our discussions
- Read existing issues

## 🙏 Thank You!

Every contribution matters, no matter how small. Thank you for helping make Orkestron better!

---

**Happy Contributing!** 🚀
