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

This repository appears to be an **AI-powered GitHub code review bot** that integrates with OpenAI's API to automatically review pull requests and provide intelligent feedback. The system can be deployed in multiple ways:

- As a **GitHub Action** for CI/CD pipelines
- As an **AWS Lambda function** for serverless deployment
- As a **GitHub App/Probot** for webhook-based integration
- As a standalone **Node.js application**

The bot analyzes code patches/diffs from pull requests, sends them to OpenAI for analysis, and returns structured feedback including whether the code looks good to merge (LGTM - "Looks Good To Me") and detailed review comments.

## 2. How to run it locally

### Prerequisites
- Node.js (latest LTS version)
- npm package manager
- GitHub personal access token or GitHub App credentials
- OpenAI API key

### Step-by-step setup:

```bash
# 1. Clone the repository
git clone <repository-url>
cd <repository-name>

# 2. Install dependencies
npm install

# 3. Create environment configuration
cp .env.example .env  # if available, or create new .env file

# 4. Configure environment variables in .env file
echo "GITHUB_TOKEN=your_github_token_here" >> .env
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
echo "WEBHOOK_SECRET=your_webhook_secret" >> .env

# 5. Build the project
npm run build

# 6. Start the application
npm start

# Alternative: For development with auto-reload
npm run dev  # if available
```

### For GitHub Action deployment:
```bash
# Build the GitHub Action
npm run build
# The action will be built in the ./action directory
```

### For AWS Lambda deployment:
```bash
# Build the Lambda function
npm run build:lambda
# The lambda function will be built in the ./lambda directory
```

## 3. Key moving parts and relations

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub        │    │   Code Review    │    │   OpenAI API    │
│   Webhooks      │───▶│   Bot (Probot)   │───▶│   GPT Models    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Chat Service   │
                       │   (AI Interface) │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Response       │
                       │   Processing     │
                       └──────────────────┘
```

**Core Components:**
- **Probot Framework**: Handles GitHub webhook events and API interactions
- **Chat Service**: Manages OpenAI API communication and prompt generation
- **Bot Logic**: Orchestrates the review process and response formatting
- **Multiple Deployment Targets**: GitHub Action, AWS Lambda, and standalone server

**Data Flow:**
1. GitHub sends webhook (PR opened/updated) → Bot receives event
2. Bot extracts code diff/patch → Sends to Chat service
3. Chat service formats prompt → Calls OpenAI API
4. OpenAI returns analysis → Chat service processes response
5. Bot posts review comments → GitHub PR updated

## 4. External systems it touches

### Primary Integrations:
- **GitHub API** (`api.github.com`): Pull request management, comments, status updates
- **OpenAI API** (`api.openai.com`, `platform.openai.com`): Code analysis and review generation
- **GitHub Models** (`models.github.ai`): Alternative AI model provider

### Documentation & Resources:
- **GitHub Developer** (`developer.github.com`): API documentation
- **GitHub Help** (`help.github.com`): Platform guidance
- **Probot Framework** (`probot.github.
