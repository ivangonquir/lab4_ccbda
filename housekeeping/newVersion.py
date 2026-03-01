import os
import json
import argparse
from git import Repo
from dotenv import dotenv_values


def get_next_version(repo, level=2):
    """Calculates next version. Defaults to v1.0.0 if no tags exist."""
    if not repo.tags:
        return "v1.0.0"

    tag_names = []
    for tag in repo.tags:
        try:
            # Strip 'v', split by '.', convert to ints
            numbers = list(map(int, tag.name.lstrip('v').split('.')))
            tag_names.append(numbers)
        except ValueError:
            continue  # Skip tags that aren't semver (e.g. 'latest')

    if not tag_names:
        return "v1.0.0"

    tag_names.sort()
    last_version = tag_names[-1]

    # Increment the chosen level
    last_version[level] += 1
    # Reset everything after that level to 0
    for i in range(level + 1, len(last_version)):
        last_version[i] = 0

    return f"v{'.'.join(map(str, last_version))}"


def update_json_and_commit(repo, new_version, config):
    """Updates the JSON file and commits it so the tag includes the change."""
    json_path = os.path.join(repo.working_tree_dir, 'housekeeping', 'elasticbeanstalk', "Dockerrun.aws.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Could not find {json_path}. Check your folder structure!")

    # 1. Update the File
    with open(json_path, "r") as f:
        data = json.load(f)

    data['Image']['Name'] = f"{config['AWS_USER_ID']}.dkr.ecr.{config['AWS_DEFAULT_REGION']}.amazonaws.com/{config['ECR_REPOSITORY']}:{new_version}"

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    # 2. Commit the change
    repo.index.add([json_path])
    repo.index.commit(f"Bump version to {new_version}")


def create_git_tag(repo, version_name):
    """Creates tag and pushes both the commit and the tag."""
    try:
        print(f"Creating tag: {version_name}...")
        new_tag = repo.create_tag(version_name, message=f"Release {version_name}")

        print(f"Pushing to remote...")
        origin = repo.remote(name='origin')
        origin.push()  # Push the commit with the updated JSON
        origin.push(new_tag)  # Push the version tag
        return True
    except Exception as e:
        print(f"Git Error: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=2, choices=[0, 1, 2], help="0:Major, 1:Minor, 2:Patch (default)")
    parser.add_argument("configuration", type=str, help="Path to configuration file")
    args = parser.parse_args()

    config = dotenv_values(dotenv_path=args.configuration)
    repo_path = os.path.abspath("..")

    with Repo(repo_path) as repo:
        new_v = get_next_version(repo, args.level)
        print(f"Targeting version: {new_v}")

        update_json_and_commit(repo, new_v, config)

        if create_git_tag(repo, new_v):
            print("Done!")

        repo.close()
