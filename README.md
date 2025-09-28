# Repo Onboarder 📚

A GitHub-integrated repository analyzer that generates comprehensive onboarding documentation for new developers. It analyzes codebases (read-only) and creates an interactive HTML viewer with tech stack insights, project structure, HTTP routes, external systems, and AI-powered explanations.

## Features

- 🔍 **Tech Stack Detection**: Automatically detects languages, frameworks, package managers, and runtimes
- 🚀 **Entrypoint Discovery**: Finds application entry points and startup scripts
- 📁 **Structure Analysis**: Generates condensed project structure with Mermaid diagrams
- 🛣️ **Route Extraction**: Discovers HTTP routes from Express, Flask, FastAPI, Django, and more
- 🔗 **External Systems**: Detects integrations with databases, APIs, and cloud services
- 🤖 **AI Enhancement**: Uses Anthropic Claude for intelligent explanations
- 📊 **Interactive Viewer**: Single-page HTML viewer with tabs and diagrams
- ⚙️ **Configurable**: Customizable analysis depth, ignore patterns, and output options

## Quick Start

### Local Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run analysis:**
   ```bash
   python onboarder.py /path/to/repository
   ```

3. **Open the results:**
   ```bash
   open onboarding/index.html
   ```

### GitHub Integration

1. **Add the workflow** to your repository by copying `.github/workflows/onboarder.yml`

2. **Set up secrets** (optional, for AI features):
   - Go to Repository Settings → Secrets and variables → Actions
   - Add `ANTHROPIC_API_KEY` with your Anthropic API key

3. **Trigger analysis:**
   - Go to Actions tab → "Repo Onboarder" → "Run workflow"
   - Or create a Pull Request to automatically generate onboarding docs

## Output Files

The tool generates an `onboarding/` directory with:

- **`index.html`** - Interactive viewer with tabs and diagrams
- **`repo_overview.md`** - Markdown overview of the repository
- **`report.json`** - Machine-readable analysis data
- **`mermaid_*.mmd`** - Mermaid diagram source files
- **`templates/style.css`** - Styling for the viewer

## Configuration

Create a `.onboarder.yml` file in your repository root:

```yaml
# Analysis depth and limits
depth: 3
max_items_per_dir: 10

# Files to ignore
ignore:
  - node_modules
  - .git
  - dist
  - build

# Output directory
output:
  dir: "onboarding"

# Enable AI features
llm:
  enabled: true
  model: "claude-3-haiku-20240307"
```

## Supported Technologies

### Languages & Frameworks
- **Node.js**: Express, Next.js, React, Vue, Svelte, NestJS
- **Python**: Flask, FastAPI, Django
- **Go**: Standard Go modules
- **Rust**: Cargo projects
- **Java/Kotlin**: Maven, Gradle

### Route Detection
- Express.js: `app.get()`, `router.post()`, etc.
- Flask: `@app.route()`
- FastAPI: `@app.get()`, `@app.post()`, etc.
- Django: `path()` in urls.py

### External Systems
- Databases: PostgreSQL, MySQL, MongoDB, Redis
- Cloud: AWS, GCP, Azure
- APIs: Stripe, Twilio, Sentry, OpenAI, Anthropic
- Message Queues: Kafka, RabbitMQ

## GitHub Actions

The included workflow supports:

- **Manual trigger**: Use "Run workflow" button
- **PR integration**: Automatically runs on pull requests
- **Artifact upload**: Downloads onboarding docs as build artifacts
- **PR comments**: Posts/updates a single comment with download link

## CLI Options

```bash
python onboarder.py [OPTIONS] PATH

Arguments:
  PATH  Path to repository to analyze

Options:
  --config PATH    Path to config file (default: .onboarder.yml)
  --output PATH    Output directory (default: onboarding)
  --no-llm         Disable LLM explanation
  --help           Show help message
```

## Examples

### Analyze a Node.js project
```bash
python onboarder.py ./my-node-app
```

### Analyze with custom config
```bash
python onboarder.py ./my-project --config custom-config.yml --output docs
```

### Disable AI features
```bash
python onboarder.py ./my-project --no-llm
```

## Performance & Safety

- **Read-only**: Never executes repository code
- **Safe limits**: Caps file sizes and analysis depth
- **Efficient**: Uses ignore patterns and smart filtering
- **Deterministic**: Same input always produces same output

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Install with `pip install -r requirements.txt`
2. **Permission errors**: Ensure you have read access to the repository
3. **Large repositories**: Adjust `depth` and `max_items_per_dir` in config
4. **LLM errors**: Check your `ANTHROPIC_API_KEY` is valid

### Debug Mode

Add `--verbose` flag to see detailed analysis progress:

```bash
python onboarder.py ./my-project --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📖 [Documentation](https://github.com/your-org/repo-onboarder)
- 🐛 [Issues](https://github.com/your-org/repo-onboarder/issues)
- 💬 [Discussions](https://github.com/your-org/repo-onboarder/discussions)