<div align="center">

# StealthAutoPoster

### Automated Facebook Group Publishing with Human-Like Behavior

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

*A modular automation tool for posting to multiple Facebook groups with anti-detection measures and realistic human behavior patterns.*

</div>

---

## About

**StealthAutoPoster** is a Python-based automation tool designed to streamline the process of publishing content to multiple Facebook groups. Built with a focus on stealth and reliability, it mimics human behavior patterns to avoid detection while maintaining a clean, modular architecture.

Originally developed to automate promotional posts for educational services across Belgian Facebook groups, the tool features intelligent timing, realistic typing patterns, and comprehensive error handling.

## Motivation

Managing social media presence across dozens of Facebook groups is time-consuming and repetitive. This project automates the process while maintaining authenticity through:

- **Human-like interactions**: Random delays, realistic typing speed, natural scrolling
- **Stealth configuration**: Custom user agents, anti-detection browser settings
- **Flexible scheduling**: GitHub Actions integration for automated posting
- **Safe testing**: Dry-run mode to validate behavior before live posting

## Key Features

**Modular Architecture** - Clean separation of concerns with dedicated modules for authentication, group extraction, and publishing  
**Anti-Detection** - Stealth browser configuration with randomized timing and human-like behavior  
**Multiple Operation Modes** - Full automation, login-only, group extraction, or targeted publishing  
**Comprehensive Logging** - Detailed logs with configurable verbosity levels  
**Dry Run Mode** - Test functionality without actually posting  
**GitHub Actions** - Automated scheduled posting via workflows

## Architecture

```
facebook_automation/
├── config.py              # Configuration and credentials management
├── driver_manager.py      # WebDriver initialization and management
├── human_behavior.py      # Human-like behavior simulation
├── facebook_auth.py       # Facebook authentication logic
├── group_extractor.py     # Group discovery and extraction
├── post_publisher.py      # Post publishing functionality
└── facebook_automation.py # Main orchestrator
```

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mathisdelsart/StealthAutoPoster.git
cd StealthAutoPoster

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your credentials:

```bash
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password
POST_TEXT=Your post content here...
```

**Important**: Never commit `.env` to version control. The file is already included in `.gitignore`.

### Usage

**Full automation** (login + extract groups + publish):
```bash
python3 main.py
```

**Login only**:
```bash
python3 main.py --mode="login"
```

**Extract groups** to a file:
```bash
python3 main.py --mode="extract" --output-file="groups.txt"
```

**Publish to specific groups**:
```bash
python3 main.py --mode="publish" --groups-file="groups.txt"
```

**Test without posting** (dry-run):
```bash
python3 main.py --dry-run
```

**Advanced options**:
```bash
python3 main.py --dry-run --max-groups=5 --log-level="DEBUG"
```

## GitHub Actions Integration

The project includes a workflow for automated posting. Configure secrets in your repository settings:

- `FACEBOOK_EMAIL`
- `FACEBOOK_PASSWORD`
- `POST_TEXT`

The workflow can be triggered manually or scheduled via cron expressions.

## How It Works

1. **Authentication**: Logs into Facebook using provided credentials with human-like typing
2. **Group Discovery**: Navigates to "My Groups" and scrolls to load all joined groups
3. **Extraction**: Parses group names and URLs, saves to file if requested
4. **Publishing**: Iterates through groups, opens each one, and publishes content
5. **Anti-Detection**: Random delays, realistic scrolling, stealth browser configuration

## Security

All sensitive data is managed through environment variables and GitHub Secrets:
- No hardcoded credentials in the codebase
- `.env` file excluded from version control
- Secure credential handling via `dotenv`

## Technical Stack

- **Automation**: Selenium WebDriver with undetected-chromedriver
- **Browser**: Chrome with stealth configuration
- **Logging**: Python logging module with file + console output
- **CI/CD**: GitHub Actions for scheduled automation

## Disclaimer

This tool was developed as a learning project to explore browser automation and web scraping techniques. **Warning**: Automated posting violates Facebook's Terms of Service and may result in account restrictions or permanent bans. Use this tool at your own risk.

---

<div align="center">

**Built for Social Media Automation**

</div>
