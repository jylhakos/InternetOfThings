# Contributing to AI Agent Observability

Thank you for your interest in contributing to this project! This guide will help you get started.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/OBSERVABILITY.git
   cd OBSERVABILITY
   ```

2. **Run Setup Script**
   ```bash
   ./setup.sh
   ```

3. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

4. **Verify Installation**
   ```bash
   python sources/test_installation.py
   ```

## Code Style

We follow Python best practices:

- **PEP 8** for code formatting
- **Black** for automatic code formatting (line length: 100)
- **isort** for import sorting
- **Type hints** where appropriate
- **Docstrings** for all functions and classes

### Format Code Before Committing

```bash
# Install development dependencies
pip install black isort flake8

# Format code
black sources/
isort sources/

# Check for issues
flake8 sources/
```

## Testing

### Run All Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Evaluation tests
python sources/run_evaluation.py --dataset fallback --num-samples 5
```

### Add New Tests

When adding new features, include:
- Unit tests in `tests/`
- Integration tests if applicable
- Update evaluation datasets if needed

## Adding New Features

### 1. Evaluation Metrics

To add a new evaluation metric:

1. Update `sources/llm_judge_evaluator.py`
2. Add the new evaluation method
3. Update documentation
4. Add tests

Example:
```python
@observe(name="evaluate_safety")
def evaluate_safety(self, answer: str) -> Dict:
    """Evaluate content safety."""
    # Your implementation
    pass
```

### 2. Observability Tools

To integrate a new observability tool:

1. Add to `requirements.txt`
2. Create integration in `sources/`
3. Update `README.md` with tool information
4. Add to comparison table
5. Provide setup instructions

### 3. Cloud Provider Support

To add support for a new cloud provider:

1. Add SDK to `requirements.txt`
2. Add configuration to `.env.example`
3. Create setup guide in `README.md`
4. Add example code in `sources/`

## Documentation

### Update README

When making changes:
- Keep Table of Contents updated
- Add references to new tools/libraries
- Include code examples
- Update comparison tables

### Code Documentation

All functions should have docstrings:

```python
def evaluate_agent(query: str, expected: str) -> Dict:
    """
    Evaluate agent response quality.
    
    Args:
        query: User's input query
        expected: Expected output
    
    Returns:
        Dictionary with evaluation results including score and reasoning
    """
    pass
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(evaluation): Add semantic similarity metric"
git commit -m "fix(langfuse): Handle connection timeout errors"
git commit -m "docs(readme): Add Azure deployment guide"
```

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Format and Test**
   ```bash
   black sources/
   isort sources/
   pytest tests/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push to Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Create PR from your branch
   - Fill in PR template
   - Wait for CI checks to pass

## CI/CD Pipeline

Our GitHub Actions workflow runs:
- Code formatting checks (Black, isort)
- Linting (flake8)
- Evaluation tests
- Threshold validation

Ensure all checks pass before requesting review.

## Adding Dependencies

1. **Add to requirements.txt**
   ```bash
   echo "new-package>=1.0.0" >> requirements.txt
   ```

2. **Install and Test**
   ```bash
   pip install new-package
   # Test the integration
   ```

3. **Update Documentation**
   - Mention in README.md
   - Add to setup instructions if needed

4. **Commit**
   ```bash
   git add requirements.txt
   git commit -m "chore(deps): Add new-package for feature X"
   ```

## Project Structure

```
OBSERVABILITY/
├── sources/              # Main source code
│   ├── agent_evaluation.py
│   ├── run_evaluation.py
│   ├── check_thresholds.py
│   ├── llm_judge_evaluator.py
│   └── test_installation.py
│
├── tests/               # Test files (create this)
│   ├── test_evaluation.py
│   ├── test_llm_judge.py
│   └── integration/
│
├── configs/            # Configuration files
│   └── thresholds.json
│
├── docker/             # Docker configurations
│   └── docker-compose.yml
│
├── .github/            # GitHub workflows
│   └── workflows/
│       └── evaluation.yml
│
└── docs/              # Additional documentation (create if needed)
```

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.