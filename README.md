# ListHive: Multi-LLM List Response Aggregator

A specialized Python tool that collects, compares, and analyzes list-based responses from multiple Large Language Models (LLMs). Perfect for consensus analysis, trend identification, and comparative evaluation of different LLMs' responses to list-based queries.

## Features

- **Multi-Model Support**: Queries multiple AI models through OpenRouter API
- **Parallel Processing**: Makes concurrent API calls for efficient data collection
- **Smart Analysis**:
  - Fuzzy matching to identify similar items
  - Canonical form tracking for variations of the same item
  - Per-model mention counting
  - Overall item ranking
- **Beautiful Output**:
  - Interactive HTML table with animations
  - Clean markdown summary
  - Colored console output
- **Error Handling**: Robust error handling with informative messages

## Prerequisites

- Python 3.7+
- OpenRouter API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your OpenRouter API key as an environment variable:
```bash
# Windows
set OPENROUTER_API_KEY=your_api_key_here

# Linux/Mac
export OPENROUTER_API_KEY=your_api_key_here
```

## Usage

1. Run the script:
```bash
python main.py
```

The script will:
- Query multiple AI models in parallel
- Process and analyze their responses
- Generate both HTML and Markdown reports
- Show progress and results in the console

## Configuration

Key constants in `main.py`:

- `MODELS`: List of AI models to query
- `USER_QUESTION`: The question to ask each model
- `REPETITIONS`: Number of times to query each model
- `SIMILARITY_THRESHOLD`: Threshold for fuzzy matching (0.0 to 1.0)

## Output Files

### results.html
- Beautiful, interactive table with:
  - Item rankings
  - Total mention counts
  - Per-model mention counts
  - Animated transitions
  - Dark mode theme

### results.md
- Clean, markdown-formatted table showing:
  - Item rankings
  - Total mentions
  - Model-specific counts

## Technical Details

### Smart Matching Algorithm

The tool uses a sophisticated matching system to identify similar items:
1. Direct matching
2. Substring containment
3. Fuzzy string matching using SequenceMatcher
4. Canonical form tracking

### Response Processing

1. Extracts content between `<response></response>` tags
2. Removes common list markers and prefixes
3. Normalizes and cleans the text
4. Groups similar items under canonical forms

### Visualization

- Uses DaisyUI for styling
- Anime.js for smooth animations
- Responsive design
- Badge-based model mention display

## Error Handling

The script includes comprehensive error handling:
- API call failures
- Response parsing issues
- File I/O errors
- Invalid configurations

## Models Currently Supported

- OpenAI Models:
  - GPT-4 Latest
  - O1 Mini
  - O1 Preview
- Other Models:
  - DeepSeek Chat
  - Qwen
  - Grok
  - Nova Pro
  - Claude 3.5 (Haiku and Sonnet)

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Your chosen license]

## Acknowledgments

- OpenRouter for API access
- DaisyUI for UI components
- Anime.js for animations 
