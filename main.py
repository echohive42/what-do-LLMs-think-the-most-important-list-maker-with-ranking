import os
import asyncio
from termcolor import cprint
from openai import AsyncOpenAI
import json
from datetime import datetime
import re
from collections import defaultdict
from difflib import SequenceMatcher

# Constants
MODELS = [
    "openai/chatgpt-4o-latest",
    "openai/o1-mini-2024-09-12",
    "openai/o1-preview",
    # "openai/o1",
    "deepseek/deepseek-chat",
    "qwen/qwq-32b-preview",
    # "google/gemini-2.0-flash-thinking-exp:free",
    "x-ai/grok-2-1212",
    # "google/gemini-exp-1206:free",
    "amazon/nova-pro-v1",
    "anthropic/claude-3.5-haiku-20241022:beta",
    "anthropic/claude-3.5-sonnet:beta"
]
USER_QUESTION = "List 3 most useful books in human history"
REPETITIONS = 3
API_KEY = os.getenv("OPENROUTER_API_KEY")
SIMILARITY_THRESHOLD = 0.85  # Threshold for fuzzy matching

# Initialize OpenAI client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

def extract_list_items(response_text: str) -> list:
    """Extract list items from between response tags."""
    try:
        # First try to get content between response tags
        match = re.search(r'<response>(.*?)</response>', response_text, re.DOTALL)
        content = match.group(1).strip() if match else response_text
        
        # Split into lines and clean up
        lines = content.split('\n')
        items = []
        
        # Common AI model disclaimers to exclude
        disclaimer_patterns = [
            r'sorry.+ai( language)? model',
            r'as an ai( language)? model',
            r'i (can\'?t|cannot|don\'?t) (have|provide|assist|help)',
            r'i apologize',
            r'i am not able to',
            r'i do not have personal',
            r'i must decline',
            r'i don\'?t have personal',
            r'i am an ai',
            r'i\'m an ai'
        ]
        
        disclaimer_regex = re.compile('|'.join(disclaimer_patterns), re.IGNORECASE)
        
        for line in lines:
            # Remove common list markers and clean up
            clean_line = re.sub(r'^[\d\-\.\*\•\○\●\)\s]+', '', line.strip())
            
            # Skip empty lines, common prefixes, and AI disclaimers
            if (clean_line and 
                not clean_line.lower().startswith(('here', 'these', 'the', 'following')) and
                not disclaimer_regex.search(clean_line)):
                items.append(clean_line.strip())
        
        return items
    except Exception:
        return []

def are_items_similar(item1: str, item2: str) -> bool:
    """Check if two items are similar using fuzzy matching."""
    # Convert to lowercase for comparison
    item1 = item1.lower()
    item2 = item2.lower()
    
    # Direct match
    if item1 == item2:
        return True
    
    # Check if one is contained in the other
    if item1 in item2 or item2 in item1:
        return True
    
    # Fuzzy matching
    similarity = SequenceMatcher(None, item1, item2).ratio()
    return similarity >= SIMILARITY_THRESHOLD

def find_or_add_canonical_item(item: str, canonical_items: dict) -> str:
    """Find a matching canonical item or add this as a new one."""
    for canonical, variations in canonical_items.items():
        if any(are_items_similar(item, var) for var in variations):
            variations.add(item)
            return canonical
    
    # If no match found, add as new canonical item
    canonical_items[item] = {item}
    return item

def analyze_item_mentions(responses: list) -> tuple[dict, dict]:
    """Analyze items mentioned across responses with smart fuzzy matching."""
    canonical_items = {}  # Maps canonical form to set of variations
    item_counts = defaultdict(int)
    item_by_model = defaultdict(lambda: defaultdict(int))
    
    for resp in responses:
        model = resp["model"]
        items = extract_list_items(resp["response"])
        
        seen_items = set()  # Track items seen in this response
        for item in items:
            # Find or create canonical form
            canonical = find_or_add_canonical_item(item, canonical_items)
            
            if canonical not in seen_items:
                item_counts[canonical] += 1
                item_by_model[canonical][model] += 1
                seen_items.add(canonical)
    
    # Sort results
    sorted_item_counts = dict(sorted(
        item_counts.items(),
        key=lambda x: (x[1], len(item_by_model[x[0]])),
        reverse=True
    ))
    
    return sorted_item_counts, item_by_model

def save_markdown_table(item_counts: dict, item_by_model: dict):
    """Save ranked list of items and their mentions in markdown."""
    try:
        with open("results.md", "w", encoding="utf-8") as f:
            f.write("# Item Rankings\n\n")
            f.write("| Rank | Item | Total Mentions | Models |\n")
            f.write("|------|------|----------------|--------|\n")
            
            for rank, (item, count) in enumerate(item_counts.items(), 1):
                models = item_by_model[item]
                model_mentions = [f"{model}({count})" for model, count in models.items()]
                f.write(f"| {rank} | {item} | {count} | {', '.join(model_mentions)} |\n")
        
        cprint("Markdown table saved to results.md", "green")
    except Exception as e:
        cprint(f"Error saving markdown table: {str(e)}", "red")

def save_html_table(item_counts: dict, item_by_model: dict):
    """Save ranked list of items and their mentions in a beautiful HTML table."""
    try:
        html_template = """
        <!DOCTYPE html>
        <html lang="en" data-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Item Rankings</title>
            <link href="https://cdn.jsdelivr.net/npm/daisyui@3.9.4/dist/full.css" rel="stylesheet">
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>
            <style>
                .fade-in {
                    opacity: 0;
                    transform: translateY(20px);
                }
            </style>
        </head>
        <body class="bg-gray-900 min-h-screen p-8">
            <div class="container mx-auto">
                <h1 class="text-4xl font-bold mb-8 text-white text-center">Item Rankings</h1>
                <div class="card bg-base-200 shadow-xl">
                    <div class="card-body">
                        <div class="overflow-x-auto">
                            <table class="table table-zebra w-full">
                                <thead>
                                    <tr class="text-white">
                                        <th>Rank</th>
                                        <th>Item</th>
                                        <th>Total Mentions</th>
                                        <th>Models (with mention counts)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for rank, (item, count) in enumerate(item_counts.items(), 1) %}
                                    <tr class="fade-in text-white">
                                        <td>{{ rank }}</td>
                                        <td>{{ item }}</td>
                                        <td>{{ count }}</td>
                                        <td>
                                            {% for model, model_count in item_by_model[item].items() %}
                                            <span class="badge badge-primary mr-2 mb-1">
                                                {{ model.split('/')[-1] }}: {{ model_count }}
                                            </span>
                                            {% endfor %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <script>
                anime({
                    targets: '.fade-in',
                    opacity: [0, 1],
                    translateY: [20, 0],
                    delay: anime.stagger(100),
                    easing: 'easeOutExpo',
                    duration: 1000
                });
            </script>
        </body>
        </html>
        """
        
        from jinja2 import Template
        template = Template(html_template)
        html_content = template.render(
            enumerate=enumerate,
            item_counts=item_counts,
            item_by_model=item_by_model
        )
        
        with open("results.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        cprint("HTML table saved to results.html", "green")
    except Exception as e:
        cprint(f"Error saving HTML table: {str(e)}", "red")

async def get_model_response(model: str, question: str) -> dict:
    """Get response from a specific model."""
    try:
        cprint(f"Querying {model}...", "yellow")
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a precise list generator. Follow these rules EXACTLY:
1. Start your response with <response>
2. List each item on a new line
3. Do not include any numbers, bullets, or markers
4. Do not add any explanations or commentary
5. Do not use prefixes like 'here are' or 'the following'
6. Keep each item concise but complete
7. End your response with </response>

Example correct format:
<response>
First item here
Second item here
Third item here
</response>"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        response = completion.choices[0].message.content
        cprint(f"Received response from {model}", "green")
        return {
            "model": model,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        cprint(f"Error with {model}: {str(e)}", "red")
        return {
            "model": model,
            "response": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

async def gather_responses():
    """Gather responses from all models with repetitions."""
    tasks = []
    for model in MODELS:
        for _ in range(REPETITIONS):
            tasks.append(get_model_response(model, USER_QUESTION))
    
    cprint("Starting to gather responses from all models...", "cyan")
    responses = await asyncio.gather(*tasks)
    cprint("All responses gathered!", "green")
    return responses

async def main():
    """Main function to orchestrate the process."""
    try:
        if not API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable not set!")
        
        cprint("Starting the process...", "cyan")
        responses = await gather_responses()
        
        cprint("Analyzing responses...", "yellow")
        item_counts, item_by_model = analyze_item_mentions(responses)
        
        cprint("Saving results...", "yellow")
        save_markdown_table(item_counts, item_by_model)
        save_html_table(item_counts, item_by_model)
        
        # Print top mentioned items to console
        cprint("\nTop mentioned items and their models:", "cyan")
        for rank, (item, count) in enumerate(list(item_counts.items())[:10], 1):
            cprint(f"\n{rank}. {item}: {count} total mentions", "green")
            for model, model_count in item_by_model[item].items():
                cprint(f"  - {model}: {model_count} mentions", "yellow")
        
        cprint("\nProcess completed successfully!", "green")
    except Exception as e:
        cprint(f"Error in main process: {str(e)}", "red")

if __name__ == "__main__":
    asyncio.run(main()) 
