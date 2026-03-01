import os
import sys
import argparse
from github import Github, Auth
from git import Repo, InvalidGitRepositoryError
from dotenv import dotenv_values


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", type=str, help="Path to configuration file")
    args = parser.parse_args()

    if not os.path.exists(args.config_path):
        print(f"Error: Configuration file '{args.config_path}' not found.")
        sys.exit(1)

    config = dotenv_values(dotenv_path=args.config_path)

    if 'TOKEN_GITHUB' not in config.keys():
        print("Error: TOKEN_GITHUB missing from configuration file.")
        sys.exit(1)

    try:
        repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        with Repo(repo_path) as repo:
            remote_url = repo.remotes.origin.url
            github_repo_name = remote_url.split("github.com/")[-1].replace(".git", "")

            print(f'Updating secrets for repo "{github_repo_name}"')

            auth = Auth.Token(config['TOKEN_GITHUB'])
            github_client = Github(auth=auth)
            remote_repo = github_client.get_repo(github_repo_name)
            for k,v in config.items():
                if not k in ['TOKEN_GITHUB']:
                    print(f"   - Setting secret: {k}")
                    remote_repo.create_secret(k, v, "actions")
            print("\nAll secrets updated successfully.")

    except InvalidGitRepositoryError:
        print("Error: The current directory is not part of a Git repository.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        repo.close()