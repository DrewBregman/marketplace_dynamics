#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to generate a professional marketplace analysis brief using OpenAI's o1 model
"""

import os
import glob
import base64
import argparse
from pathlib import Path
import openai
from PIL import Image
import io
from dotenv import load_dotenv
import openai

load_dotenv()

openai.organization = os.getenv("OPENAI_ORG_ID", "")
openai.api_key = os.getenv("OPENAI_SECRET_KEY", "")

def load_project_context():
    """Load the project context."""
    context_file = Path("context/project_context.txt")
    if context_file.exists():
        with open(context_file, "r") as f:
            return f.read()
    return "No project context available."

def load_plots():
    """Load all plots in the plots directory."""
    plot_dict = {}
    plot_dir = Path("output/plots")
    
    # Get all png files in the plots directory and its subdirectories
    plots = list(plot_dir.glob("**/*.png"))
    
    for plot_path in plots:
        try:
            # Convert image to base64 for API
            with open(plot_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                plot_dict[plot_path.name] = img_data
        except Exception as e:
            print(f"Error loading plot {plot_path}: {e}")
    
    return plot_dict

def create_prompt(context, plots):
    """Create the prompt for the API."""
    prompt = """I have the task of preparing a written brief to uncover the most interesting insights. It should be 3-6 pages long and be organized by type of analysis and relationships. Your brief should be insightful, clear, and professional—like something you'd see in Harvard Business Review or McKinsey reports. Analyze the given data on shift offers, worker behaviors, shift cancellations, no-shows, and payment rates.

Ensure your writing is:
- Natural, professional, and engaging
- Concise but thorough
- Clear and easily understandable, avoiding repetitive phrasing and overly formal language
- Insightful, showcasing thoughtful reflection rather than obvious facts

Please include analysis on these key areas:
- Worker behavior
- Workplace behavior
- First booking patterns
- Churn patterns (workplace, worker)
- Shift and pricing analysis
- Market segmentation and retention

And analyze any possible relationships between each.

Project context:
"""
    prompt += context
    
    prompt += "\n\nI've analyzed the data and generated the following visualizations:\n"
    
    # Add plot descriptions
    for plot_name in plots.keys():
        prompt += f"- {plot_name}\n"
    
    return prompt

def create_message_with_images(prompt, plots):
    """Create a message with images for the API."""
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    
    # Add images to the message
    for plot_name, plot_data in plots.items():
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{plot_data}",
                "detail": "low"  # Use low detail to reduce tokens
            }
        })
    
    return messages

def generate_report(messages):
    """Generate the report using OpenAI's o1 model."""
    try:
        response = openai.chat.completions.create(
            model="o1",
            messages=messages,
            reasoning_effort="high"
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating report: {e}")
        return f"Error generating report: {str(e)}"

def save_report(report):
    """Save the generated report."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "marketplace_analysis_brief.md"
    with open(output_file, "w") as f:
        f.write(report)
    
    print(f"Report saved to {output_file}")
    return output_file

def main():
    
    # Load project context
    context = load_project_context()
    
    # Load plots
    plots = load_plots()
    print(f"Loaded {len(plots)} plots.")
    
    # Create prompt
    prompt = create_prompt(context, plots)
    
    # Create message with images
    messages = create_message_with_images(prompt, plots)
    
    # Generate report
    print("Generating report using OpenAI's o1 model...")
    report = generate_report(messages)
    
    # Save report
    output_file = save_report(report)
    print(f"Analysis brief has been generated and saved to {output_file}")

if __name__ == "__main__":
    main()