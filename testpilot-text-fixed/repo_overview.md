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

This repository appears to be an **AI-powered GitHub code review bot** that integrates with OpenAI's API to provide automated code reviews on pull requests. The system is designed to work as both a GitHub Action and an AWS Lambda function, offering multiple deployment options.

Key capabilities:
- Automatically reviews code changes in GitHub pull requests
- Uses OpenAI's language models (including Azure OpenAI and GitHub Models) to analyze code patches
- Provides intelligent feedback and determines if code changes look good to merge (LGTM)
- Supports webhook-based integration with GitHub
- Can be deployed as a GitHub Action, AWS Lambda, or standalone Node.js application

## 2. How to run it locally (step-by-step setup instructions)

### Prerequisites
- Node.js runtime installed
- npm package manager
- GitHub repository access
- OpenAI API key

### Setup Steps

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   npm install
   ```

2. **Environment Configuration**
   Create a `.env` file with required variables:
   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # GitHub Configuration (for webhook integration)
   GITHUB_TOKEN=your_github_token
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   
   # Optional: Azure OpenAI or GitHub Models configuration
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint
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

5. **For GitHub Action deployment**
   ```bash
   npm run build  # This creates the action/ directory
   ```

6. **For AWS Lambda deployment**
   ```bash
   npm run build:lambda  # This creates the lambda/ directory
   ```

7. **Run tests**
   ```bash
   npm test
   ```

## 3. Key moving parts and relations

### Core Components Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub        │    │   Webhook       │    │   Chat/AI       │
│   Events        │───▶│   Handler       │───▶│   Processor     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Probot        │    │   Bot Logic     │    │   OpenAI API    │
│   Framework     │◀───│   (robot)       │◀───│   Integration   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Relations
- **Webhook Entry Point** (`api/github/webhooks/index.ts`) receives GitHub events
- **Bot Logic** (`src/bot.ts`) processes GitHub events using Probot framework
- **Chat Module** (`src/chat.ts`) handles AI interactions with OpenAI
- **Multiple Deployment Targets**: GitHub Action, AWS Lambda, and standalone server
- **Build System**: Uses Rollup and NCC for different deployment bundles

## 4. External systems it touches

### Primary Integrations
- **GitHub API** (`api.github.com`) - Repository access, PR management, webhook events
- **OpenAI API** (`api.openai.com`, `platform.openai.com`) - AI-powered code analysis
- **GitHub Models** (`models.github.ai`) - Alternative AI model provider
- **Azure OpenAI** - Enterprise AI service integration

### Documentation & Resources
- **GitHub Developer Platform** (`developer.
