# Changelog
## [Unreleased] - 2024-12-19
## [Unreleased] - 2024-12-19

### Modified
- Updated app.py


## [Unreleased] - 2024-12-19

### Modified
- Updated app.py

### Modified
- Updated CHANGELOG.md
All notable changes to the Copywriting Impact Checker will be documented in this file.

## [Unreleased] - 2024-12-19

### Modified
- Updated .file_hashes.json
- Updated CHANGELOG.md
- Updated app.py
- Updated requirements.txt

## [1.2.0] - 2024-12-19

### Added
- Automatic email delivery of PDF reports using Resend
- Professional HTML email template with score summary
- Improved PDF report formatting with better spacing and readability
- Automatic email collection through Resend dashboard

### Changed
- Replaced download button with automatic email delivery
- Updated PDF layout with better typography and spacing
- Improved error handling for email sending
- Simplified dependencies in requirements.txt

### Fixed
- PDF encoding issues that caused display problems
- Dependency conflicts with numpy and streamlit versions
- Issues with PDF truncation in the report

## [1.1.0] - 2024-12-19

### Added
- Email capture functionality
- PDF report generation with detailed analysis
- Custom logo integration
- Progress bars for score visualization

### Changed
- Updated UI layout with two-column design
- Enhanced error messages and user feedback
- Improved text analysis prompts

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
