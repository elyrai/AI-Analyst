
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 17:37:10 2024

@author: antoinepury
"""

import pandas as pd
import openai
import sys

def setup_openai(api_key):
    openai.api_key = api_key

def analyze_tweet(tweet_text, likes, retweets, views):
    prompt = f"""
    Evaluate the following tweet for its engagement and quality on a scale of 1 to 10. Include specific rationale for the score. 
    Metrics to consider:
    - Relevance
    - Informational Value
    - Engagement Potential
    - Creativity
    - Emotional Resonance
    - Call-to-Action Effectiveness
    - Clarity and Conciseness
    - Visual Appeal
    - Transparency and Ethics
    - Consistency and Tone
    
    Engagement Data:
    - Likes: {likes}
    - Retweets: {retweets}
    - Views: {views}
    
    Tweet Content:\n"{tweet_text}"\n
    Provide a score (1-10) for each metric and a rationale summarizing the tweet's strengths and weaknesses.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=500
        )
        response_text = response['choices'][0]['message']['content'].strip()
        return response_text
    except Exception as e:
        return f"Error processing tweet: {str(e)}"

def display_progress_bar(current, total):
    bar_length = 40
    progress = current / total
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {current}/{total} tweets analyzed')
    sys.stdout.flush()
    if current == total:
        print()

def analyze_last_15_tweets(file_path, output_file):
    tweets_df = pd.read_csv(file_path)
    
    if "text" not in tweets_df.columns:
        raise ValueError("The CSV must contain a 'text' column with the tweet content.")
    
    last_15_tweets = tweets_df.tail(15)
    analysis_results = []
    total_tweets = len(last_15_tweets)
    
    for idx, row in last_15_tweets.iterrows():
        tweet_text = row["text"]
        likes = row.get("likes", 0)
        retweets = row.get("retweets", 0)
        views = row.get("views", 0)
        analysis_result = analyze_tweet(tweet_text, likes, retweets, views)
        analysis_results.append({"text": tweet_text, "analysis": analysis_result})
        display_progress_bar(idx + 1, total_tweets)
    
    results_df = pd.DataFrame(analysis_results)
    results_df.to_csv(output_file, index=False)
    
    overall_analysis = summarize_activity(analysis_results)
    summary_file = output_file.replace('.csv', '_summary.txt')
    with open(summary_file, 'w') as f:
        f.write(overall_analysis)
    
    print(f"Detailed tweet analysis for the last 15 tweets saved to {output_file}")
    print(f"Overall activity summary saved to {summary_file}")

def summarize_activity(results):
    strengths = []
    improvements = []
    examples = {"strengths": [], "improvements": []}
    
    for result in results:
        analysis = result["analysis"]
        
        if "strength" in analysis.lower():
            strengths.append(analysis)
            examples["strengths"].append(result["text"])
        
        if "improvement" in analysis.lower() or "weakness" in analysis.lower():
            improvements.append(analysis)
            examples["improvements"].append(result["text"])
    
    summary = "=== Summary of Twitter Account Activity ===\n\n"
    summary += "Top 3 Strengths:\n"
    for i, strength in enumerate(strengths[:3], 1):
        summary += f"{i}. {strength.strip()}\n"
    summary += "\nExamples:\n"
    for i, example in enumerate(examples["strengths"][:3], 1):
        summary += f"  Example {i}: {example.strip()}\n"
    
    summary += "\nAreas for Improvement:\n"
    for i, improvement in enumerate(improvements[:3], 1):
        summary += f"{i}. {improvement.strip()}\n"
    summary += "\nExamples:\n"
    for i, example in enumerate(examples["improvements"][:3], 1):
        summary += f"  Example {i}: {example.strip()}\n"
    
    summary += "\n==========================================="
    return summary

def main():
    openai_api_key = 'PUT KEY OF FINE TUNEED MODEL HERE'
    setup_openai(openai_api_key)
    
    print("Welcome to the Twitter AI Agent Analysis Tool!")
    input_file = input("Enter the path to the CSV file containing tweets: ")
    output_file = input("Enter the path to save the analysis results (CSV): ")
    
    try:
        analyze_last_15_tweets(input_file, output_file)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    print("Goodbye!")

if __name__ == "__main__":
    main()