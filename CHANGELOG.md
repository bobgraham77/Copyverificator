# Changelog
## [Unreleased] - 2024-12-19
## [Unreleased] - 2024-12-19

### Modified
- Updated app.py
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated .file_hashes.json
- Updated CHANGELOG.md
- Updated app.py
- Updated requirements.txt
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated app.py
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated assets/copy_checker.svg
## [Unreleased] - 2024-12-19

### Modified
- Updated .file_hashes.json
- Updated CHANGELOG.md
- Updated app.py
- Updated assets/logo.svg
- Updated changelog_watcher_error.log
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated app.py
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated .streamlit/config.toml
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated config.toml

### Modified
- Updated app.py
## [Unreleased] - 2024-12-19


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated requirements.txt

### Modified
- Updated .file_hashes.json
- Updated .gitignore
- Updated .streamlit/config.toml
- Updated CHANGELOG.md
- Updated NEXT_ACTIONS.md
- Updated README.md
- Updated app.py
- Updated changelog_watcher.log
- Updated changelog_watcher_error.log
- Updated requirements.txt
- Updated test_consistency.py
- Updated ~/Library/LaunchAgents/com.copyverificator.changelog.plist

## [Unreleased] - 2024-12-19

### Modified
- Updated config.toml


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py


## [Unreleased] - 2024-12-19

### Modified
- Updated watchmedo.py


## [Unreleased] - 2024-12-19

### Modified
- Updated __init__.py


## [Unreleased] - 2024-12-19

### Modified
- Updated README.md


## [Unreleased] - 2024-12-19

### Modified
- Updated README.md


## [Unreleased] - 2024-12-18

### Modified
- Updated README.md

All notable changes to the Copywriting Impact Checker will be documented in this file.

## [1.0.1] - 2024-12-18

### Added
- Automatic changelog update system using Git pre-commit hook
- Git repository initialization for version control
- New development tools and scripts:
  - `update_changelog.py` (deprecated in favor of Git hook)
  - `.git/hooks/pre-commit` for automatic changelog updates

### Enhanced
- Improved score consistency with temperature reduction (0.1) and fixed seed
- Enhanced button design with subtle checkmark and green hover/active states
- Standardized blue color for final assessment text
- Increased token limit (2048) for complete analysis results

### Fixed
- Score parsing algorithm for better accuracy
- Text truncation issues in analysis results
- Color contrast issues in the UI

## [1.0.0] - 2024-12-18

### Added
- Initial release of the Copywriting Impact Checker
- Integration with Groq API for text analysis
- Modern UI with Streamlit framework
- 10 copywriting criteria evaluation:
  - Empathy (Understanding the audience)
  - Clarity (Clear and concise message)
  - Attention (Powerful headlines/hooks)
  - Flow (Logical structure)
  - Benefits (Focus on benefits)
  - Action (Strong call to action)
  - Trust (Credibility and authority)
  - Emotion (Storytelling)
  - Adaptation (Optimized for the medium)
  - Influence (Persuasion)
- Interactive score visualization with:
  - Circular progress chart
  - Individual score bars for each criterion
  - Color-coded scores (green, yellow, orange, red)
- Detailed improvement suggestions for each criterion
- Multi-language support (English, Spanish, French)
- Overall score calculation and final assessment
