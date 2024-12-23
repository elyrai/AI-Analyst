
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:35:21 2024

@author: antoinepury
"""

import fitz  # library for the PDF extraction, it works more smooth than lang chain
import pandas as pd
import openai
import time
import sys
import requests
from bs4 import BeautifulSoup
import re  # Module that looks for the wait time whne the TPM limit is reached, and retrieve the info

# PDF Extractions
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Openai API key
def setup_openai(api_key):
    openai.api_key = api_key

# Extract text from the website of the shared project
def extract_text_from_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Get all text from the website 
        text = soup.get_text(separator="\n")
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website content: {e}")
        return ""

# Function for the process bar, to show where do we stand
def overall_progress_bar(current_step, total_steps):
    progress = (current_step) / total_steps
    bar_length = 40
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rProcessing: |{bar}| {int(progress * 100)}% Complete')
    sys.stdout.flush()
    if current_step == total_steps:
        print()  

# Get a rating (1 to 3) and rationale
def parse_rating_and_rationale(response):
    rating = None
    rationale = None
    
    for word in response.split():
        if word.isdigit() and int(word) in [1, 2, 3]:
            rating = int(word)
            break

    rationale = response.split(f"{rating}", 1)[-1].strip() if rating else response.strip()

    return rating, rationale

# Prompt that gives the commands to use parameter using both the whitepaper and the website content
def analyze_parameter(content, parameter):
    prompt = f"""Based on the content of the project (both the whitepaper and website), rate the parameter '{parameter}' from 1 to 3, where 1 is Poor, 2 is Average, and 3 is Excellent. 
    - 1 means significant flaws in the project related to {parameter}, such as lacking details or weak foundation.
    - 2 means there are some positive elements in the project regarding {parameter}, but still room for improvement.
    - 3 reflects a very strong execution of {parameter}, with comprehensive and well-researched content.

    Provide a rating and explain the rationale in at least 40 words. Ensure the rationale reflects specific details about the project.

    Project Content:\n{content}\n\nPlease provide your rating and specific rationale:"""
    
    while True:  # Loop that will keep the process going, until it is done. The loop starts again at the same parameter whtne the TPM limit is reached, so the the output is still the same
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  
                messages=[{"role": "system", "content": prompt}],
                max_tokens=350  
            )
            response_text = response['choices'][0]['message']['content'].strip()
            rating, rationale = parse_rating_and_rationale(response_text)
            
            if rating is not None:
                return {"Parameter": parameter, "Rating": rating, "Rationale": rationale}
            else:
                return {"Parameter": parameter, "Rating": "Uncertain", "Rationale": rationale}
        
        except openai.error.RateLimitError as e:
            # Extract the wait time from the error message
            wait_time = re.search(r"Please try again in (\d+(\.\d+)?)s", str(e))
            if wait_time:
                wait_seconds = float(wait_time.group(1))
                print(f"Rate limit exceeded for parameter '{parameter}'. Waiting for {wait_seconds} seconds before retrying...")
                time.sleep(wait_seconds)  # Wait for the required time before retrying, and complete the request again, not leaving any parameters blank
            else:
                print(f"Rate limit exceeded. Waiting for 60 seconds before retrying...")
                time.sleep(60)  # Default wait time if not whait time is given
        except Exception as e:
            print(f"Error processing parameter '{parameter}': {str(e)}")
            return {"Parameter": parameter, "Rating": "Error", "Rationale": str(e)}

# Analyze all parameters using both the whitepaper and the website content
def analyze_all_parameters(content, sections):
    results = []
    
    total_params = sum([len(params) for params in sections.values()])
    processed_params = 0
    
    for section, params in sections.items():
        results.append({"Parameter": section, "Rating": "", "Rationale": ""})  # Appends the sections content, to give a structure to the output
        for param in params:
            processed_params += 1
            result = analyze_parameter(content, param)
            results.append(result)
            overall_progress_bar(processed_params, total_params)
    
    return results

# Save results to an Excel file, at the destination that was provided
def save_results_to_excel(results, output_file):
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")

# Main part
def main():
    # Set up OpenAI API key
    openai_api_key = 'YOUR-API-KEY-HERE'
    setup_openai(openai_api_key)

    # Bot wakes up and says hi
    print("Hi Borger! 🤖")
    print("Please share the location of the project PDF whitepaper you want to analyze.\n")
    
    # Get the whitepaper pdf location
    whitepaper_pdf_path = input("📄 Full path to the whitepaper PDF file: ")
    whitepaper_text = extract_text_from_pdf(whitepaper_pdf_path)

    # Ask for the website URL
    project_website_url = input("🌐 Please provide the project website URL: ")
    website_text = extract_text_from_website(project_website_url)
    
    # Combine whitepaper and website content
    combined_content = whitepaper_text + "\n\n" + website_text

    # Business DD Questions (updated with missing points)
    sections = {
        "Philosophy": ["Mission / Vision Statement", "Whitepaper", "Pitch Deck", "Blog & Educational Content"],
        "Product": ["Product Stage", "Business Model Maturity", "Virality Level", "UX Level", "Competitive Positioning", "Regulatory Risk", "Level of Novelty"],
        "Token Economical Design": ["Token Allocation", "Token Distribution", "Token Smart Contract Quality"],
        "Token Utility Design": ["Utility", "Interconnection Between Business Model & Token"],
        "Product Growth Metrics": ["Total Users", "Weekly Active Users", "(if B2B2C) Total B Users"],
        "Social Media Growth Metrics": ["Twitter Followers", "Twitter Verified Account Followers", "Discord or TG Members", "Bot Level"],
        "Top of the Funnel Metrics": ["Email DB"],
        "Funding": ["VC Backing Popularity", "Angel Popularity"],
        "PR": ["PR Scoring (Google Search)", "Similar Web (Emerging Markets)", "Partnerships"],
        "KOLs": ["KOL Shill Traction"],
        "Underlying Theme/Sector": ["Web3.0 Maturity", "Theme Expected Popularity in Next Cycle"],
        "CEX Listing": ["Already Listed or Listing Confirmed"],
        "Launchpad": ["Already Done or Plan Confirmed"],
        "Team": ["Quality of the Team"],
        "Price": ["Primary Market Peers Valuation", "Secondary Market Peers Valuation - Tier 1"],
        "Liquidity": ["Cash Raised Total"],
        "TGE": ["Recent Deal TGE Valuation (Peers Group)"]
    }

    # Analyze all parameters using combined content
    results = analyze_all_parameters(combined_content, sections)

    # Ask user where to save the results
    print("\nThanks! Now, please tell me where to save the results as an Excel file.")
    output_excel_path = input("💾 Full path to save the Excel file: ")
    
    # Save the results to Excel file
    save_results_to_excel(results, output_excel_path)

    # Bye message
    print("\nAll done! 🎉 The analysis has been completed, and the results are saved.")
    print("Goodbye, Borger! 👋")

# Main function loop
if __name__ == "__main__":
    main()