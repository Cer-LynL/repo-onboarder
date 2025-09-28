#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Repo Onboarder with Anthropic integration
Creates a sample repository and tests with LLM features enabled
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from onboarder import RepoAnalyzer, Config

def create_test_repo():
    """Create a test repository for Anthropic testing"""
    temp_dir = tempfile.mkdtemp(prefix="anthropic_test_")
    repo_path = Path(temp_dir)
    
    # Create package.json
    package_json = {
        "name": "anthropic-test-app",
        "version": "1.0.0",
        "description": "A test application for Repo Onboarder with Anthropic integration",
        "scripts": {
            "start": "node server.js",
            "dev": "nodemon server.js",
            "test": "jest",
            "build": "webpack --mode production"
        },
        "dependencies": {
            "express": "^4.18.0",
            "mongoose": "^7.0.0",
            "stripe": "^12.0.0",
            "redis": "^4.6.0",
            "axios": "^1.4.0",
            "jsonwebtoken": "^9.0.0",
            "bcryptjs": "^2.4.3"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "nodemon": "^2.0.0",
            "webpack": "^5.80.0",
            "supertest": "^6.3.0"
        }
    }
    
    with open(repo_path / "package.json", 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create server.js
    server_js = """
const express = require('express');
const mongoose = require('mongoose');
const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const redis = require('redis');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/test-app');

// Connect to Redis
const redisClient = redis.createClient({
    url: process.env.REDIS_URL || 'redis://localhost:6379'
});

// Middleware
app.use(express.json());

// Auth middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }
    
    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Invalid token' });
        req.user = user;
        next();
    });
};

// Routes
app.get('/', (req, res) => {
    res.json({ 
        message: 'Welcome to Anthropic Test API',
        version: '1.0.0',
        endpoints: ['/api/users', '/api/payments', '/api/auth']
    });
});

// User routes
app.get('/api/users', authenticateToken, async (req, res) => {
    try {
        const users = await User.find().select('-password');
        res.json(users);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/users', async (req, res) => {
    try {
        const { name, email, password } = req.body;
        const hashedPassword = await bcrypt.hash(password, 10);
        const user = new User({ name, email, password: hashedPassword });
        await user.save();
        res.status(201).json({ id: user._id, name: user.name, email: user.email });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

app.get('/api/users/:id', authenticateToken, async (req, res) => {
    try {
        const user = await User.findById(req.params.id).select('-password');
        if (!user) return res.status(404).json({ error: 'User not found' });
        res.json(user);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Auth routes
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const user = await User.findOne({ email });
        if (!user || !await bcrypt.compare(password, user.password)) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        const token = jwt.sign({ userId: user._id }, process.env.JWT_SECRET, { expiresIn: '24h' });
        res.json({ token, user: { id: user._id, name: user.name, email: user.email } });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Payment routes
app.post('/api/payments/create-intent', authenticateToken, async (req, res) => {
    try {
        const { amount, currency = 'usd' } = req.body;
        const paymentIntent = await stripe.paymentIntents.create({
            amount: Math.round(amount * 100), // Convert to cents
            currency,
            metadata: { userId: req.user.userId }
        });
        res.json({ clientSecret: paymentIntent.client_secret });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

app.get('/api/payments/history', authenticateToken, async (req, res) => {
    try {
        const paymentIntents = await stripe.paymentIntents.list({
            limit: 10,
            metadata: { userId: req.user.userId }
        });
        res.json(paymentIntents.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});
"""
    
    with open(repo_path / "server.js", 'w') as f:
        f.write(server_js)
    
    # Create models directory and User model
    (repo_path / "models").mkdir()
    user_model = """
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true,
        minlength: 2,
        maxlength: 50
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true,
        match: [/^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$/, 'Please enter a valid email']
    },
    password: {
        type: String,
        required: true,
        minlength: 6
    },
    role: {
        type: String,
        enum: ['user', 'admin', 'moderator'],
        default: 'user'
    },
    isActive: {
        type: Boolean,
        default: true
    },
    lastLogin: {
        type: Date,
        default: null
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    updatedAt: {
        type: Date,
        default: Date.now
    }
});

// Update the updatedAt field before saving
userSchema.pre('save', function(next) {
    this.updatedAt = new Date();
    next();
});

module.exports = mongoose.model('User', userSchema);
"""
    
    with open(repo_path / "models" / "User.js", 'w') as f:
        f.write(user_model)
    
    # Create controllers
    (repo_path / "controllers").mkdir()
    user_controller = """
const User = require('../models/User');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const redis = require('redis');

class UserController {
    constructor() {
        this.redisClient = redis.createClient({
            url: process.env.REDIS_URL || 'redis://localhost:6379'
        });
    }
    
    async getAllUsers(req, res) {
        try {
            // Check cache first
            const cacheKey = 'users:all';
            const cached = await this.redisClient.get(cacheKey);
            
            if (cached) {
                return res.json(JSON.parse(cached));
            }
            
            const users = await User.find({ isActive: true })
                .select('-password')
                .sort({ createdAt: -1 });
            
            // Cache for 5 minutes
            await this.redisClient.setex(cacheKey, 300, JSON.stringify(users));
            
            res.json(users);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async createUser(req, res) {
        try {
            const { name, email, password, role = 'user' } = req.body;
            
            // Check if user already exists
            const existingUser = await User.findOne({ email });
            if (existingUser) {
                return res.status(400).json({ error: 'User already exists' });
            }
            
            // Hash password
            const hashedPassword = await bcrypt.hash(password, 12);
            
            // Create user
            const user = new User({
                name,
                email,
                password: hashedPassword,
                role
            });
            
            await user.save();
            
            // Invalidate cache
            await this.redisClient.del('users:all');
            
            res.status(201).json({
                id: user._id,
                name: user.name,
                email: user.email,
                role: user.role,
                createdAt: user.createdAt
            });
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }
    
    async getUserById(req, res) {
        try {
            const user = await User.findById(req.params.id).select('-password');
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            res.json(user);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
}

module.exports = new UserController();
"""
    
    with open(repo_path / "controllers" / "userController.js", 'w') as f:
        f.write(user_controller)
    
    # Create tests
    (repo_path / "tests").mkdir()
    test_file = """
const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('API Tests', () => {
    beforeEach(async () => {
        await User.deleteMany({});
    });
    
    describe('GET /', () => {
        test('should return welcome message', async () => {
            const response = await request(app).get('/');
            expect(response.status).toBe(200);
            expect(response.body.message).toBe('Welcome to Anthropic Test API');
        });
    });
    
    describe('POST /api/users', () => {
        test('should create a new user', async () => {
            const userData = {
                name: 'John Doe',
                email: 'john@example.com',
                password: 'password123'
            };
            
            const response = await request(app)
                .post('/api/users')
                .send(userData);
            
            expect(response.status).toBe(201);
            expect(response.body.name).toBe(userData.name);
            expect(response.body.email).toBe(userData.email);
        });
        
        test('should not create user with invalid email', async () => {
            const userData = {
                name: 'John Doe',
                email: 'invalid-email',
                password: 'password123'
            };
            
            const response = await request(app)
                .post('/api/users')
                .send(userData);
            
            expect(response.status).toBe(400);
        });
    });
});
"""
    
    with open(repo_path / "tests" / "api.test.js", 'w') as f:
        f.write(test_file)
    
    # Create README
    readme = """
# Anthropic Test App

A comprehensive Node.js application demonstrating various technologies and patterns for testing Repo Onboarder with Anthropic integration.

## Features

- **Authentication**: JWT-based authentication with bcrypt password hashing
- **User Management**: CRUD operations for users with validation
- **Payment Processing**: Stripe integration for payment intents
- **Caching**: Redis for caching user data
- **Database**: MongoDB with Mongoose ODM
- **Testing**: Comprehensive test suite with Jest and Supertest
- **Security**: Input validation, password hashing, token verification

## Tech Stack

- **Backend**: Node.js, Express.js
- **Database**: MongoDB with Mongoose
- **Cache**: Redis
- **Payments**: Stripe
- **Authentication**: JWT, bcrypt
- **Testing**: Jest, Supertest
- **Build**: Webpack

## API Endpoints

### Public
- `GET /` - Welcome message and API info
- `POST /api/users` - Create new user
- `POST /api/auth/login` - User login

### Protected (requires JWT token)
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/payments/create-intent` - Create payment intent
- `GET /api/payments/history` - Get payment history

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `STRIPE_API_KEY` - Stripe secret key
- `JWT_SECRET` - JWT signing secret
- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (development/production)

## Setup

1. Install dependencies: \`npm install\`
2. Set environment variables
3. Start MongoDB and Redis
4. Run: \`npm start\`
5. Test: \`npm test\`

## Architecture

The application follows a layered architecture:
- **Routes**: Express route handlers
- **Controllers**: Business logic layer
- **Models**: Data models and validation
- **Middleware**: Authentication and validation
- **Services**: External service integrations (Stripe, Redis)
"""
    
    with open(repo_path / "README.md", 'w') as f:
        f.write(readme)
    
    return repo_path

def test_with_anthropic():
    """Test the analyzer with Anthropic integration"""
    print("Creating test repository for Anthropic testing...")
    repo_path = create_test_repo()
    
    try:
        print("Running analysis with Anthropic integration...")
        
        # Check if ANTHROPIC_API_KEY is available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("⚠️  ANTHROPIC_API_KEY not found in environment")
            print("   Set it in your .env file or environment variables")
            print("   Analysis will continue without LLM features")
        
        config = Config()
        config.llm_enabled = bool(api_key)  # Enable only if API key is available
        
        analyzer = RepoAnalyzer(str(repo_path), config)
        analysis = analyzer.analyze()
        
        print("Generating outputs...")
        analyzer.generate_outputs()
        
        # Verify outputs
        output_dir = repo_path / "onboarding"
        assert output_dir.exists(), "Output directory not created"
        
        expected_files = [
            "index.html",
            "repo_overview.md", 
            "report.json",
            "mermaid_structure.mmd",
            "mermaid_routes.mmd",
            "mermaid_systems.mmd",
            "templates/style.css"
        ]
        
        for file in expected_files:
            file_path = output_dir / file
            assert file_path.exists(), "Missing file: " + file
            print("OK " + file)
        
        # Check analysis results
        assert "Express.js" in analysis["stack"]["frameworks"], "Express not detected"
        assert "JavaScript/TypeScript" in analysis["stack"]["languages"], "JS/TS not detected"
        assert "server.js" in analysis["entrypoints"], "Entrypoint not detected"
        assert len(analysis["routes"]) > 0, "No routes detected"
        assert "Stripe" in analysis["stack"]["externals"], "Stripe not detected"
        assert "Redis" in analysis["stack"]["externals"], "Redis not detected"
        
        # Check if LLM explanation was generated
        if config.llm_enabled and "llm_explanation" in analysis:
            print("✅ LLM explanation generated")
        elif config.llm_enabled:
            print("⚠️  LLM explanation not generated (API issue?)")
        else:
            print("ℹ️  LLM features disabled (no API key)")
        
        print("All tests passed!")
        print("Analysis results:")
        print("  - Languages: " + str(analysis['stack']['languages']))
        print("  - Frameworks: " + str(analysis['stack']['frameworks']))
        print("  - Entrypoints: " + str(analysis['entrypoints']))
        print("  - Routes: " + str(len(analysis['routes'])))
        print("  - External systems: " + str(analysis['stack']['externals']))
        
        if config.llm_enabled and "llm_explanation" in analysis:
            print("\n🤖 LLM Explanation Preview:")
            print(analysis["llm_explanation"][:200] + "...")
        
        return True
        
    except Exception as e:
        print("Test failed: " + str(e))
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(repo_path)
        print("Cleaned up test files")

if __name__ == "__main__":
    success = test_with_anthropic()
    exit(0 if success else 1)
