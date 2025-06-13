import os
import requests
from datetime import datetime, timedelta
import json

# Get environment variables set by GitHub Actions
GITHUB_TOKEN = os.getenv('GTH_TOK') # Your custom secret for the PAT
GITHUB_USERNAME = os.getenv('GH_USERNAME') # This will now be 'kenil-gopani' from the workflow

def get_merged_prs(username, start_date_str):
    """
    Fetches merged PRs for a given user from a specific start date.
    Handles pagination. Counts PRs where the user is the 'author'.
    """
    base_url = "https://api.github.com/search/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Query for merged PRs authored by the user and merged after the start date
    query = f"is:pr is:merged author:{username} merged:>{start_date_str}"

    all_merged_prs = []
    page = 1

    while True:
        params = {"q": query, "per_page": 100, "page": page} # Max per_page is 100
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes

        data = response.json()
        items = data.get('items', [])

        if not items:
            break # No more PRs

        all_merged_prs.extend(items)

        if len(items) < 100:
            break # If less than per_page, it's the last page
        page += 1

    return len(all_merged_prs)

if __name__ == "__main__":
    today = datetime.now()

    # Calculate start of today for daily count
    start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)

    # Calculate start of month for monthly count
    start_of_month = datetime(today.year, today.month, 1, 0, 0, 0)

    # Calculate start of year for yearly count
    start_of_year = datetime(today.year, 1, 1, 0, 0, 0) # January 1st of the current year

    prs_today = get_merged_prs(GITHUB_USERNAME, start_of_day.isoformat(timespec='seconds'))
    prs_month = get_merged_prs(GITHUB_USERNAME, start_of_month.isoformat(timespec='seconds'))
    prs_year = get_merged_prs(GITHUB_USERNAME, start_of_year.isoformat(timespec='seconds'))

    # Print values (useful for debugging in action logs)
    print(f"Daily Merged PRs: {prs_today}")
    print(f"Monthly Merged PRs: {prs_month}")
    print(f"Yearly Merged PRs: {prs_year}")

    # Output these values so the GitHub Action can use them in subsequent steps
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f'prs_today={prs_today}', file=fh)
        print(f'prs_month={prs_month}', file=fh)
        print(f'prs_year={prs_year}', file=fh)
