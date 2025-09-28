# Repository Overview

## Tech Snapshot

**Languages:** JavaScript/TypeScript
**Frameworks:** Next.js
**Package Managers:** npm
**Runtimes:** Node.js

## Entrypoints & Startup Scripts

- `api/github/webhooks/index.ts`
- `src/index.ts`

### NPM Scripts
- `start`: node -r dotenv/config ./dist/index.js
- `test`: jest
- `build`: rm -rf dist && rollup -c rollup.config.ts --configPlugin @rollup/plugin-typescript && ncc build src/github-action.cjs -o action
- `build:lambda`: ncc build src/aws-lambda.cjs -o lambda

## Project Structure

```
├── 📄 CODE_OF_CONDUCT.md
├── 📄 CONTRIBUTING.md
├── 📄 Dockerfile
├── 📄 LICENSE
├── 📄 README.ja.md
├── 📄 README.ko.md
├── 📄 README.md
├── 📄 README.zh-CN.md
├── 📄 README.zh-TW.md
├── 📁 action/
│   ├── 📄 37.index.cjs.js
│   ├── 📄 _tiktoken_bg.wasm
│   ├── 📄 encoder.json
│   ├── 📄 file.js
│   ├── 📄 github-action.js
│   ├── 📄 index.cjs
│   ├── 📄 middleware.d.ts
│   ├── 📄 multipart-parser-d1d13d05.js
│   ├── 📄 rollup.config.d.ts
│   ├── 📁 src/
│   │   ├── 📄 bot.d.ts
│   │   ├── 📄 chat.d.ts
│   │   ├── 📄 index.d.ts
│   │   └── 📄 log.d.ts
│   ├── 📄 vocab.bpe
│   ├── 📄 worker-pipeline.js
│   ├── 📄 worker.js
│   └── 📄 worker1.js
├── 📄 action.yml
├── 📁 api/
│   └── 📁 github/
│       └── 📁 webhooks/
├── 📄 app.yml
├── 📄 jest.config.js
├── 📄 middleware.ts
├── 📄 package-lock.json
├── 📄 package.json
├── 📄 pm2.config.cjs
├── 📁 public/
│   └── 📄 index.html
├── 📄 rollup.config.ts
├── 📄 serverless.yml
├── 📁 src/
│   ├── 📄 aws-lambda.cjs
│   ├── 📄 bot.ts
│   ├── 📄 chat.ts
│   ├── 📄 fetch-polyfill.cjs
│   ├── 📄 github-action.cjs
│   ├── 📄 index.ts
│   └── 📄 log.ts
├── 📁 test/
│   ├── 📁 fixtures/
│   │   ├── 📄 issues.opened.json
│   │   └── 📄 mock-cert.pem
│   └── 📄 index.test.ts
├── 📄 tsconfig.json
└── 📄 yarn.lock
```

## HTTP Routes

No routes detected

## External Systems & Integrations

**Dependencies:** OpenAI

**Environment Variables & URLs:**
- Environment Variables
- api.github.com
- api.openai.com
- developer.github.com
- example.com
- facebook.github.io
- github.com
- help.github.com
- help.github.com)
- models.github.ai
- opensource.guide
- platform.openai.com
- probot.github.io
- tbaggery.com
- user-images.githubusercontent.com
- www.contributor-covenant.org

## Key Files & Roles

- `CODE_OF_CONDUCT.md` - Documentation
- `CONTRIBUTING.md` - Documentation
- `README.ja.md` - Documentation
- `README.ko.md` - Documentation
- `README.md` - Documentation
- `README.zh-CN.md` - Documentation
- `README.zh-TW.md` - Documentation
- `action/37.index.cjs.js` - Entry Point
- `action/file.js` - JavaScript/TypeScript Code
- `action/middleware.d.ts` - HTTP Middleware
- `action/multipart-parser-d1d13d05.js` - JavaScript/TypeScript Code
- `action/rollup.config.d.ts` - Configuration
- `action/src/bot.d.ts` - JavaScript/TypeScript Code
- `action/src/chat.d.ts` - JavaScript/TypeScript Code
- `action/src/index.d.ts` - Entry Point
- `action/src/log.d.ts` - JavaScript/TypeScript Code
- `action/worker-pipeline.js` - JavaScript/TypeScript Code
- `action/worker.js` - JavaScript/TypeScript Code
- `action/worker1.js` - JavaScript/TypeScript Code
- `action.yml` - Configuration
- `app.yml` - Configuration
- `jest.config.js` - Configuration
- `middleware.ts` - HTTP Middleware
- `package.json` - Package Configuration
- `public/index.html` - Public Assets
- `rollup.config.ts` - Configuration
- `serverless.yml` - Styling
- `src/bot.ts` - JavaScript/TypeScript Code
- `src/chat.ts` - JavaScript/TypeScript Code
- `src/index.ts` - Entry Point
- `src/log.ts` - JavaScript/TypeScript Code
- `test/fixtures/issues.opened.json` - Tests
- `test/index.test.ts` - Tests
- `tsconfig.json` - Configuration

## High-Level Explainer

# Codebase Analysis

## 1. What this repo likely does

This repository appears to be a **GitHub bot/automation tool** that integrates with **OpenAI's API** to provide AI-powered assistance for GitHub repositories. Based on the tech stack and external systems, it likely:

- Responds to GitHub webhooks (pull requests, issues, comments)
- Uses OpenAI's API to generate intelligent responses, code reviews, or suggestions
- Can be deployed as either a **GitHub Action** or an **AWS Lambda function**
- Provides multilingual support (Japanese, Korean, Chinese variants)
- Automates repository management tasks using AI assistance

The dual build targets (`build` for GitHub Action, `build:lambda` for AWS Lambda) suggest this is a flexible AI bot that can run in multiple environments.

## 2. How to run it locally

### Prerequisites
- Node.js (latest LTS version)
- npm package manager
- GitHub account and repository access
- OpenAI API key

### Step-by-step setup:

```bash
# 1. Clone the repository
git clone <repository-url>
cd <repository-name>

# 2. Install dependencies
npm install

# 3. Set up environment variables
cp .env.example .env  # if available, or create .env file
# Add required environment variables:
# OPENAI_API_KEY=your_openai_api_key
# GITHUB_TOKEN=your_github_token
# Add any other required environment variables

# 4. Build the project
npm run build

# 5. Run locally
npm start

# Alternative: Run tests
npm test
```

### For GitHub Action deployment:
```bash
# Build the GitHub Action
npm run build
# The built action will be in the ./action directory
```

### For AWS Lambda deployment:
```bash
# Build the Lambda function
npm run build:lambda
# The built lambda will be in the ./lambda directory
```

## 3. Key moving parts and relations

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub        │    │   Main Bot       │    │   OpenAI API    │
│   Webhooks      │───▶│   Application    │───▶│   Integration   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Deployment     │
                    │   Options:       │
                    │   • GitHub Action│
                    │   • AWS Lambda   │
                    │   • Direct Node  │
                    └──────────────────┘
```

**Core Components:**
- **Webhook Handler** (`api/github/webhooks/index.ts`): Receives GitHub events
- **Bot Logic** (`src/bot.d.ts`): Core automation logic
- **Chat Integration** (`src/chat.d.ts`): OpenAI API communication
- **Build System**: Rollup + NCC for multiple deployment targets
- **Entry Points**: Different entry points for different deployment methods

## 4. External systems it touches

### Primary Integrations:
- **GitHub API** (`api.github.com`): Repository management, webhook processing
- **OpenAI API** (`api.openai.com`, `platform.openai.com`): AI-powered responses
- **GitHub Models** (`models.github.ai`): Potentially using GitHub's AI models

### Documentation & Resources:
- **GitHub Documentation**: `developer.github.com`, `help.github.com`
- **Community Resources**: `opensource.guide`, `probot.github.io`
- **Standards**: `contributor-covenant.org` for code of conduct

### Infrastructure:
- **Environment Variables**: Configuration management
- **GitHub Actions**: CI/CD and automation platform
- **AWS Lambda**: Serverless deployment option

## 5. File analysis

### Entry Points
- **`api/github/webhooks/index.ts`**: Main webhook handler that receives GitHub events (issues, PRs, comments) and routes them to appropriate handlers
- **`src/index.ts`**: Primary application entry point for direct Node
