#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for Repo Onboarder
Shows how to use the onboarder programmatically
"""

import os
import tempfile
import shutil
from pathlib import Path
from onboarder import RepoAnalyzer, Config

def create_demo_repo():
    """Create a demo repository with multiple technologies"""
    temp_dir = tempfile.mkdtemp(prefix="onboarder_demo_")
    repo_path = Path(temp_dir)
    
    # Create a mixed Node.js + Python project
    # package.json
    package_json = {
        "name": "demo-app",
        "version": "1.0.0",
        "scripts": {
            "start": "node server.js",
            "dev": "nodemon server.js",
            "test": "jest",
            "build": "webpack"
        },
        "dependencies": {
            "express": "^4.18.0",
            "mongoose": "^7.0.0",
            "stripe": "^12.0.0",
            "redis": "^4.6.0",
            "axios": "^1.4.0"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "nodemon": "^2.0.0",
            "webpack": "^5.80.0"
        }
    }
    
    with open(repo_path / "package.json", 'w') as f:
        import json
        json.dump(package_json, f, indent=2)
    
    # server.js with Express routes
    server_js = """
const express = require('express');
const mongoose = require('mongoose');
const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const redis = require('redis');

const app = express();

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI);

// Connect to Redis
const redisClient = redis.createClient({
    url: process.env.REDIS_URL
});

// Middleware
app.use(express.json());

// Routes
app.get('/', (req, res) => {
    res.json({ message: 'Welcome to Demo API' });
});

app.get('/api/users', async (req, res) => {
    try {
        const users = await User.find();
        res.json(users);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/users', async (req, res) => {
    try {
        const user = new User(req.body);
        await user.save();
        res.status(201).json(user);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

app.get('/api/users/:id', async (req, res) => {
    try {
        const user = await User.findById(req.params.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        res.json(user);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.put('/api/users/:id', async (req, res) => {
    try {
        const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        res.json(user);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

app.delete('/api/users/:id', async (req, res) => {
    try {
        const user = await User.findByIdAndDelete(req.params.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        res.json({ message: 'User deleted successfully' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Payment routes
app.post('/api/payments', async (req, res) => {
    try {
        const { amount, currency } = req.body;
        const paymentIntent = await stripe.paymentIntents.create({
            amount: amount * 100, // Convert to cents
            currency: currency || 'usd',
        });
        res.json({ clientSecret: paymentIntent.client_secret });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
"""
    
    with open(repo_path / "server.js", 'w') as f:
        f.write(server_js)
    
    # Create directories and files
    (repo_path / "models").mkdir()
    (repo_path / "controllers").mkdir()
    (repo_path / "middleware").mkdir()
    (repo_path / "tests").mkdir()
    (repo_path / "config").mkdir()
    
    # User model
    user_model = """
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true
    },
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true
    },
    password: {
        type: String,
        required: true,
        minlength: 6
    },
    role: {
        type: String,
        enum: ['user', 'admin'],
        default: 'user'
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

module.exports = mongoose.model('User', userSchema);
"""
    
    with open(repo_path / "models" / "User.js", 'w') as f:
        f.write(user_model)
    
    # User controller
    user_controller = """
const User = require('../models/User');
const redis = require('redis');

class UserController {
    constructor() {
        this.redisClient = redis.createClient({
            url: process.env.REDIS_URL
        });
    }
    
    async getAllUsers(req, res) {
        try {
            // Check cache first
            const cached = await this.redisClient.get('users:all');
            if (cached) {
                return res.json(JSON.parse(cached));
            }
            
            const users = await User.find().select('-password');
            
            // Cache for 5 minutes
            await this.redisClient.setex('users:all', 300, JSON.stringify(users));
            
            res.json(users);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async createUser(req, res) {
        try {
            const user = new User(req.body);
            await user.save();
            
            // Invalidate cache
            await this.redisClient.del('users:all');
            
            res.status(201).json(user);
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }
}

module.exports = new UserController();
"""
    
    with open(repo_path / "controllers" / "userController.js", 'w') as f:
        f.write(user_controller)
    
    # Auth middleware
    auth_middleware = """
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const authMiddleware = async (req, res, next) => {
    try {
        const token = req.header('Authorization')?.replace('Bearer ', '');
        
        if (!token) {
            return res.status(401).json({ error: 'No token provided' });
        }
        
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        const user = await User.findById(decoded.userId).select('-password');
        
        if (!user) {
            return res.status(401).json({ error: 'Invalid token' });
        }
        
        req.user = user;
        next();
    } catch (error) {
        res.status(401).json({ error: 'Invalid token' });
    }
};

module.exports = authMiddleware;
"""
    
    with open(repo_path / "middleware" / "auth.js", 'w') as f:
        f.write(auth_middleware)
    
    # Config file
    config_js = """
module.exports = {
    port: process.env.PORT || 3000,
    mongodb: {
        uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/demo-app'
    },
    redis: {
        url: process.env.REDIS_URL || 'redis://localhost:6379'
    },
    stripe: {
        secretKey: process.env.STRIPE_SECRET_KEY,
        publishableKey: process.env.STRIPE_PUBLISHABLE_KEY
    },
    jwt: {
        secret: process.env.JWT_SECRET || 'your-secret-key',
        expiresIn: '24h'
    }
};
"""
    
    with open(repo_path / "config" / "index.js", 'w') as f:
        f.write(config_js)
    
    # Test file
    test_js = """
const request = require('supertest');
const app = require('../server');
const User = require('../models/User');

describe('User API', () => {
    beforeEach(async () => {
        await User.deleteMany({});
    });
    
    test('GET /api/users should return empty array', async () => {
        const response = await request(app).get('/api/users');
        expect(response.status).toBe(200);
        expect(response.body).toEqual([]);
    });
    
    test('POST /api/users should create a new user', async () => {
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
});
"""
    
    with open(repo_path / "tests" / "user.test.js", 'w') as f:
        f.write(test_js)
    
    # README
    readme = """
# Demo App

A full-stack Node.js application with Express, MongoDB, Redis, and Stripe integration.

## Features

- User management API
- JWT authentication
- Redis caching
- Stripe payment processing
- MongoDB data persistence
- Comprehensive test suite

## Setup

1. Install dependencies: \`npm install\`
2. Set environment variables:
   - \`MONGODB_URI\` - MongoDB connection string
   - \`REDIS_URL\` - Redis connection string
   - \`STRIPE_SECRET_KEY\` - Stripe secret key
   - \`JWT_SECRET\` - JWT signing secret
3. Run: \`npm start\`

## API Endpoints

- \`GET /api/users\` - Get all users
- \`POST /api/users\` - Create user
- \`GET /api/users/:id\` - Get user by ID
- \`PUT /api/users/:id\` - Update user
- \`DELETE /api/users/:id\` - Delete user
- \`POST /api/payments\` - Create payment intent

## Testing

Run tests with: \`npm test\`
"""
    
    with open(repo_path / "README.md", 'w') as f:
        f.write(readme)
    
    return repo_path

def run_demo():
    """Run the demo"""
    print("🚀 Creating demo repository...")
    repo_path = create_demo_repo()
    
    try:
        print("🔍 Running Repo Onboarder analysis...")
        
        # Create custom config
        config = Config()
        config.depth = 2
        config.max_items_per_dir = 8
        config.llm_enabled = False  # Disable for demo
        
        # Run analysis
        analyzer = RepoAnalyzer(str(repo_path), config)
        analysis = analyzer.analyze()
        
        # Generate outputs
        analyzer.generate_outputs()
        
        print("✅ Demo complete!")
        print(f"📁 Output directory: {repo_path / 'onboarding'}")
        print(f"🌐 Open: {repo_path / 'onboarding' / 'index.html'}")
        
        # Show some results
        print("\n📊 Analysis Results:")
        print(f"  Languages: {', '.join(analysis['stack']['languages'])}")
        print(f"  Frameworks: {', '.join(analysis['stack']['frameworks'])}")
        print(f"  Entrypoints: {len(analysis['entrypoints'])}")
        print(f"  HTTP Routes: {len(analysis['routes'])}")
        print(f"  External Systems: {len(analysis['stack']['externals'])}")
        
        return str(repo_path)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    demo_path = run_demo()
    if demo_path:
        print(f"\n🎉 Demo completed successfully!")
        print(f"📂 Demo files are in: {demo_path}")
        print(f"🌐 Open the HTML viewer: {demo_path}/onboarding/index.html")
    else:
        print("❌ Demo failed")
