#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Repo Onboarder
Creates a sample repository structure and tests the analyzer
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from onboarder import RepoAnalyzer, Config

def create_sample_repo():
    """Create a sample repository for testing"""
    temp_dir = tempfile.mkdtemp(prefix="onboarder_test_")
    repo_path = Path(temp_dir)
    
    # Create package.json for Node.js project
    package_json = {
        "name": "test-app",
        "version": "1.0.0",
        "scripts": {
            "start": "node server.js",
            "dev": "nodemon server.js",
            "test": "jest"
        },
        "dependencies": {
            "express": "^4.18.0",
            "stripe": "^12.0.0",
            "redis": "^4.6.0"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "nodemon": "^2.0.0"
        }
    }
    
    with open(repo_path / "package.json", 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create server.js with Express routes
    server_js = """
const express = require('express');
const app = express();

// Routes
app.get('/', (req, res) => {
    res.json({ message: 'Hello World' });
});

app.post('/api/users', (req, res) => {
    res.json({ message: 'User created' });
});

app.get('/api/users/:id', (req, res) => {
    res.json({ user: { id: req.params.id } });
});

app.put('/api/users/:id', (req, res) => {
    res.json({ message: 'User updated' });
});

app.delete('/api/users/:id', (req, res) => {
    res.json({ message: 'User deleted' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
"""
    
    with open(repo_path / "server.js", 'w') as f:
        f.write(server_js)
    
    # Create some additional files
    (repo_path / "controllers").mkdir()
    (repo_path / "models").mkdir()
    (repo_path / "tests").mkdir()
    
    # Create controller file
    controller_js = """
const stripe = require('stripe')(process.env.STRIPE_API_KEY);
const redis = require('redis');

class UserController {
    async createUser(req, res) {
        // Create user logic
        res.json({ success: true });
    }
    
    async getUser(req, res) {
        // Get user logic
        res.json({ user: req.params.id });
    }
}

module.exports = UserController;
"""
    
    with open(repo_path / "controllers" / "userController.js", 'w') as f:
        f.write(controller_js)
    
    # Create model file
    model_js = """
const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
    name: String,
    email: String,
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', UserSchema);
"""
    
    with open(repo_path / "models" / "User.js", 'w') as f:
        f.write(model_js)
    
    # Create test file
    test_js = """
const request = require('supertest');
const app = require('../server');

describe('API Tests', () => {
    test('GET / should return hello world', async () => {
        const response = await request(app).get('/');
        expect(response.status).toBe(200);
    });
});
"""
    
    with open(repo_path / "tests" / "api.test.js", 'w') as f:
        f.write(test_js)
    
    # Create README
    readme = """
# Test App

A sample Express.js application with user management.

## Setup

1. Install dependencies: `npm install`
2. Set environment variables: `STRIPE_API_KEY=your_key`
3. Run: `npm start`

## API Endpoints

- GET / - Hello world
- POST /api/users - Create user
- GET /api/users/:id - Get user
- PUT /api/users/:id - Update user
- DELETE /api/users/:id - Delete user
"""
    
    with open(repo_path / "README.md", 'w') as f:
        f.write(readme)
    
    return repo_path

def test_analyzer():
    """Test the analyzer with sample repository"""
    print("Creating sample repository...")
    repo_path = create_sample_repo()
    
    try:
        print("Running analysis...")
        config = Config()
        config.llm_enabled = False  # Disable LLM for testing
        
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
        
        print("All tests passed!")
        print("Analysis results:")
        print("  - Languages: " + str(analysis['stack']['languages']))
        print("  - Frameworks: " + str(analysis['stack']['frameworks']))
        print("  - Entrypoints: " + str(analysis['entrypoints']))
        print("  - Routes: " + str(len(analysis['routes'])))
        print("  - External systems: " + str(analysis['stack']['externals']))
        
        return True
        
    except Exception as e:
        print("Test failed: " + str(e))
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(repo_path)
        print("Cleaned up test files")

if __name__ == "__main__":
    success = test_analyzer()
    exit(0 if success else 1)
