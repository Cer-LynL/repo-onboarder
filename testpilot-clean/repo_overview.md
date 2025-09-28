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

# Comprehensive Codebase Analysis

## 1. What this repo likely does

This repository appears to be an **AI-powered GitHub code review bot** that integrates with GitHub repositories to provide automated code reviews using OpenAI's language models. The system can be deployed in multiple ways:

- As a **GitHub Action** for CI/CD pipelines
- As an **AWS Lambda function** for serverless deployment  
- As a **GitHub App/Probot** for webhook-based integration
- As a **standalone Node.js application**

The bot analyzes pull request diffs/patches and provides intelligent feedback, determining whether code changes look good to merge (LGTM - "Looks Good To Me") or if there are issues that need attention. It supports multiple AI providers including OpenAI, Azure OpenAI, and GitHub Models.

## 2. How to run it locally (step-by-step setup instructions)

### Prerequisites
- Node.js (latest LTS version)
- npm package manager
- OpenAI API key or GitHub Models access
- GitHub repository with appropriate permissions

### Setup Steps

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   npm install
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   GITHUB_TOKEN=your_github_token_here
   # Optional: For Azure OpenAI
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint
   # Optional: For GitHub Models
   GITHUB_MODELS_TOKEN=your_github_models_token
   ```

3. **Build the application**
   ```bash
   npm run build
   ```

4. **Run locally**
   ```bash
   npm start
   ```

### Alternative deployment options:

**As GitHub Action:**
- The `action.yml` file is already configured
- Push to GitHub and reference in your workflow files

**As AWS Lambda:**
```bash
npm run build:lambda
# Deploy the generated lambda/ directory to AWS
```

**For development/testing:**
```bash
npm test
```

## 3. Key moving parts and relations

### Core Components Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub        │    │   Entry Points   │    │   AI Service    │
│   Webhooks      │───▶│   - Probot       │───▶│   - OpenAI      │
│   - PR Events   │    │   - GitHub Action│    │   - Azure       │
│   - Push Events │    │   - Lambda       │    │   - GitHub      │
└─────────────────┘    │   - Standalone   │    │     Models      │
                       └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │   Core Logic     │
                       │   - Chat class   │
                       │   - Bot logic    │
                       │   - Multipart    │
                       │     Parser       │
                       └──────────────────┘
```

### Key Relationships:
- **Entry Points** → Multiple deployment targets (Action, Lambda, Probot, Standalone)
- **Bot Logic** → Handles GitHub webhook events and orchestrates reviews
- **Chat Class** → Interfaces with AI services for code analysis
- **Multipart Parser** → Handles form data processing for HTTP requests
- **Build System** → Rollup + NCC for different deployment bundles

## 4. External systems it touches

### Primary Integrations:
- **GitHub API** (`api.github.com`) - Repository data, PR information, comments
- **OpenAI API** (`api.openai.com`, `platform.openai.com`) - AI-powered code analysis
- **GitHub Models** (`models.github.ai`) - Alternative AI provider
- **Azure OpenAI** - Enterprise AI service option

### Documentation & Resources:
- **GitHub Developer** (`developer.github.com`) - API documentation
- **Probot Framework** (`probot.github.io`)
