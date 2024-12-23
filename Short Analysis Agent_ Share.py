#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 23:51:41 2024

@author: antoinepury
"""

import pandas as pd
import openai

def setup_openai(api_key):
    openai.api_key = api_key

def generate_account_feedback(tweets_combined):
    prompt = f"""
    Analyze the overall communication style and content quality of these tweets as if they represent a single account.
    
    Provide feedback in the following style:
    1. Start with a compliment on the account's strengths (e.g., clarity, wit, creativity).
    2. Suggest one or two areas where the account could improve its communication or tone.
    3. End with an inspiring takeaway or analogy (e.g., "Think like Solana—fast and clean, but also packed with real value").
    
    Combined Tweets: "{tweets_combined}"
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

def analyze_account(file_path, output_file):
    tweets_df = pd.read_csv(file_path)
    if "text" not in tweets_df.columns:
        raise ValueError("The CSV must contain a 'text' column with the tweet content.")
    original_tweets = tweets_df[tweets_df["is_retweet"] == False]
    tweets_combined = " ".join(original_tweets["text"].tail(50))
    feedback = generate_account_feedback(tweets_combined)
    with open(output_file, 'w') as f:
        f.write("=== Twitter Account Feedback ===\n\n")
        f.write(feedback)
        f.write("\n=================================\n")
    print(f"Account feedback saved to {output_file}")

def main():
    openai_api_key = input("Enter your OpenAI API key: ")
    setup_openai(openai_api_key)
    print("Welcome to the Concise Twitter Account Feedback Tool!")
    input_file = input("Enter the path to the CSV file containing tweets: ")
    output_file = input("Enter the path to save the account feedback (TXT): ")
    try:
        analyze_account(input_file, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")
    print("Goodbye!")

if __name__ == "__main__":
    main()