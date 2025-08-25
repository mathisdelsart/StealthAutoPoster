# Facebook Group Automation Tool

A modular, professional Facebook automation tool for posting to multiple groups with human-like behavior and anti-detection measures.

## 🚀 Features

- **Modular Architecture**: Clean, maintainable code structure with separate components
- **Human-like Behavior**: Realistic typing, scrolling, and interaction patterns
- **Anti-Detection**: Stealth browser configuration and random delays
- **Flexible Configuration**: Environment variables and command-line options
- **Multiple Modes**: Full automation, testing, group extraction only, or targeted publishing
- **Comprehensive Logging**: Detailed logs with multiple levels
- **Error Handling**: Robust error handling and recovery mechanisms
- **Dry Run Mode**: Test functionality without actually posting

## 📁 Project Structure

```
facebook_automation/
  ├── __init__.py                # Package initialization
  ├── config.py                  # Configuration management
  ├── driver_manager.py          # WebDriver management
  ├── human_behavior.py          # Human-like behavior simulation
  ├── facebook_auth.py           # Facebook authentication
  ├── group_extractor.py         # Group discovery and extraction
  ├── post_publisher.py          # Post publishing functionality
  └── facebook_automation.py     # Main orchestrator
.gitignore                 # Git ignore rules
main.py                    # Command-line interface
requirements.txt           # Dependencies
.github/workflows/run.yml  # GitHub Actions workflow
README.md                  # This file
```

## 🛠 Installation

1. **Clone or download the project files**
   ```bash
   git clone https://github.com/Mathis003/SocialAutoPoster.git
   cd SocialAutoPoster
   ```

2. **Create environment:**
   ```bash
   python3 -m venv <name_env>
   source <name_env>/bin/activate   # Mac/Linux
   <name_env>\Scripts\activate      # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### Environment Variables (.env file)

```bash
# Facebook Credentials
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_secure_password

# Post Content
POST_TEXT=Your post content here...

# Automation Settings
DRY_RUN=true              # Set to false for live posting
MAX_GROUPS=10             # Limit number of groups (optional)
MAX_SCROLL_TIME=10        # Minutes to scroll for groups
POST_DELAY_MIN=5.0        # Minimum delay between posts (seconds)
POST_DELAY_MAX=10.0       # Maximum delay between posts (seconds)
```
> ⚠️ Never commit `.env` to GitHub. Make sure `.env` is listed in `.gitignore`.

## 🚀 Usage

### Command Line Interface

#### Full Automation (Default)
```bash
python3 main.py
```

#### Test Login Only
```bash
python3 main.py --mode login-test
```

#### Extract Groups Only
```bash
python3 main.py --mode extract-only [--output-file my_groups.txt]
```

#### Publish to Specific Groups
```bash
python3 main.py --mode publish-only --groups-file groups.txt
```

#### Advanced Options
```bash
# Run with custom settings
python3 main.py --dry-run --max-groups 5 --log-level DEBUG

# Custom post content
python3 main.py --mode publish-only --groups-file groups.txt --post-content "Custom message"
```

## 📊 Output and Logging

The tool provides comprehensive feedback:

- **Console Output**: Real-time progress updates
- **Log Files**: Detailed logs saved to `facebook_automation.log`
- **Statistics**: Success rates, timing, and error summaries

### Example Output
```
📊 Automation Results Summary:
• Total groups processed: 15
• Successful posts: 13 ✅
• Failed posts: 2 ❌
• Success rate: 86.7%
• Mode: Live Posting
```

## 🛡️ Security Features

- **Environment Variables**: Credentials stored securely
- **Anti-Detection**: 
  - Realistic user agents
  - Random delays and timing
  - Human-like scrolling and typing
  - Stealth browser configuration
- **Error Handling**: Graceful failure handling
- **Dry Run Mode**: Test without consequences

## 🎛️ Customization

### Adding Custom Selectors

```python
# In config.py, modify FacebookSelectors.default()
selectors.write_selectors.append('//your-custom-selector')
```

### Custom Human Behavior

```python
# Extend HumanBehavior class
class MyHumanBehavior(HumanBehavior):
    def custom_delay(self):
        return self.random_delay(2, 5)
```

### Custom Post Publishing Logic

```python
# Extend PostPublisher class
class MyPostPublisher(PostPublisher):
    def custom_publish_logic(self, driver, group_url):
        # Your custom logic here
        pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Login Failures**
   - Verify credentials in .env file
   - Check for 2FA requirements
   - Facebook may require manual verification

2. **Element Not Found Errors**
   - Facebook frequently changes selectors
   - Update selectors in config.py
   - Run in DEBUG mode for more details

---