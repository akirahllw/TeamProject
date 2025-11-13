# Contributing to ScrumFlow

Thank you for considering contributing to ScrumFlow! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the project and community
- Show empathy towards other contributors

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Commit your changes following our commit conventions
6. Push to your fork
7. Create a Pull Request

## Development Setup

See the [README.md](README.md) file for detailed setup instructions.

## Branch Naming Convention

- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation changes
- `refactor/*` - Code refactoring
- `test/*` - Test additions or modifications
- `chore/*` - Maintenance tasks

Examples:
- `feature/user-authentication`
- `fix/api-response-error`
- `docs/update-readme`

## Commit Message Format

We follow the Conventional Commits specification:

```
type: subject

body (optional)

footer (optional)
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (formatting, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to build process or auxiliary tools
- **ci**: Changes to CI configuration files and scripts

### Examples

```
feat: add user login endpoint

Implements JWT-based authentication for user login.
Includes validation and error handling.
```

```
fix: resolve CORS issue in API

Corrects CORS configuration to allow requests from frontend
```

## Pull Request Process

1. **Update Documentation**: Ensure README and other docs are updated if needed
2. **Add Tests**: Include tests for new features or bug fixes
3. **Code Quality**: Run linters and formatters before submitting
4. **Description**: Provide a clear description of changes in the PR
5. **Link Issues**: Reference related issues using `Fixes #issue-number`

### PR Title Format

PR titles must follow the conventional commits format:

```
type: description
```

Example: `feat: implement project board view`

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] No new warnings or errors

## Code Style Guidelines

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions and classes
- Keep functions small and focused
- Maximum line length: 88 characters (Black default)

```python
def calculate_total(items: list[Item]) -> float:
    """Calculate the total price of items.

    Args:
        items: List of items to calculate total for

    Returns:
        Total price as a float
    """
    return sum(item.price for item in items)
```

### Frontend (TypeScript/React)

- Use TypeScript for type safety
- Follow React best practices and hooks guidelines
- Use functional components
- Keep components small and reusable
- Use meaningful variable and function names

```typescript
interface Project {
  id: string
  name: string
  description: string
}

const ProjectCard: React.FC<{ project: Project }> = ({ project }) => {
  return (
    <div className="project-card">
      <h3>{project.name}</h3>
      <p>{project.description}</p>
    </div>
  )
}
```

## Testing Guidelines

### Backend Tests

- Write unit tests for all new functions
- Use pytest fixtures for setup
- Mock external dependencies
- Aim for >80% code coverage

```python
def test_create_project():
    """Test project creation."""
    project = create_project("Test Project")
    assert project.name == "Test Project"
    assert project.id is not None
```

### Frontend Tests

- Write unit tests for components
- Test user interactions
- Test edge cases and error states
- Use React Testing Library

```typescript
import { render, screen } from '@testing-library/react'
import { ProjectCard } from './ProjectCard'

test('renders project name', () => {
  const project = { id: '1', name: 'Test Project', description: 'Test' }
  render(<ProjectCard project={project} />)
  expect(screen.getByText('Test Project')).toBeInTheDocument()
})
```

## Running Quality Checks

Before submitting a PR, run:

```bash
# Backend
cd backend
black .                  # Format code
flake8 .                # Lint
mypy app                # Type check
pytest                  # Run tests

# Frontend
cd frontend
npm run format          # Format code
npm run lint            # Lint
npm run test            # Run tests
```

Or use the Makefile:

```bash
make lint              # Run all linters
make test              # Run all tests
make lint-fix          # Auto-fix issues
```

## Review Process

1. At least one approval required before merging
2. All CI checks must pass
3. Conflicts must be resolved
4. Changes should be squashed when merging

## Questions or Problems?

- Check existing issues and discussions
- Create a new issue with the question label
- Reach out to team members

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to ScrumFlow!
