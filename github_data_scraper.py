import requests
import pandas as pd
import time  # To add delay between requests and avoid rate limiting

# GitHub API token
GITHUB_TOKEN = "your_personal_access_token_here"
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

# Search for users in Dublin with over 50 followers
USER_SEARCH_URL = "https://api.github.com/search/users"
def fetch_users(location="Dublin", min_followers=50):
    users = []
    page = 1
    while True:
        params = {
            'q': f'location:{location} followers:>{min_followers}',
            'per_page': 30,
            'page': page
        }
        response = requests.get(USER_SEARCH_URL, headers=HEADERS, params=params)
        data = response.json()

        if 'items' not in data:
            break  # Stop if no items found (API might be rate-limiting)

        for user in data['items']:
            user_data = {
                'login': user.get('login', ''),
                'name': '',  # Will fetch in detail
                'company': '',
                'location': location,
                'email': '',
                'hireable': '',
                'bio': '',
                'public_repos': user.get('public_repos', ''),
                'followers': user.get('followers', ''),
                'following': user.get('following', ''),
                'created_at': user.get('created_at', '')
            }
            users.append(user_data)
        
        # Check if there are more pages
        if 'next' not in response.links:
            break
        page += 1
        time.sleep(1)  # Pause to avoid hitting rate limits

    return users
def fetch_repositories(user_login):
    repos = []
    REPO_URL = f"https://api.github.com/users/{user_login}/repos"
    page = 1

    while True:
        params = {
            'per_page': 30,
            'page': page,
            'sort': 'pushed'  # Most recent pushed repos first
        }
        response = requests.get(REPO_URL, headers=HEADERS, params=params)
        repo_data = response.json()

        if not isinstance(repo_data, list):
            break  # Stop if no repositories found (API limit reached)

        for repo in repo_data:
            repos.append({
                'login': user_login,
                'full_name': repo.get('full_name', ''),
                'created_at': repo.get('created_at', ''),
                'stargazers_count': repo.get('stargazers_count', 0),
                'watchers_count': repo.get('watchers_count', 0),
                'language': repo.get('language', ''),
                'has_projects': repo.get('has_projects', False),
                'has_wiki': repo.get('has_wiki', False),
                'license_name': repo.get('license', {}).get('key', '')
            })

        if 'next' not in response.links:
            break
        page += 1
        time.sleep(1)  # Pause to avoid hitting rate limits

    return repos
def save_to_csv(users, repositories):
    # Save users
    users_df = pd.DataFrame(users)
    users_df.to_csv("users.csv", index=False)

    # Save repositories
    repos_df = pd.DataFrame(repositories)
    repos_df.to_csv("repositories.csv", index=False)

def main():
    users = fetch_users()
    all_repositories = []
    
    for user in users:
        repos = fetch_repositories(user['login'])
        all_repositories.extend(repos)
    
    save_to_csv(users, all_repositories)

if __name__ == "__main__":
    main()
