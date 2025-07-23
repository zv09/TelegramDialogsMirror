# Contributing to pyTelegramDialogsMirror

First off, thank you for considering contributing! Any contributions you make are **greatly appreciated**.

This document provides all the information you need to get started with development.

## Setting up a Development Environment

To get your development environment set up, follow these steps:

1.  **Fork and clone the repository:**

    ```bash
    git clone https://github.com/YOUR_USERNAME/pyTelegramDialogsMirror.git
    cd pyTelegramDialogsMirror
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3.  **Install all dependencies:**

    This project separates production and development dependencies. To install everything needed for development, including tools like `bump-my-version`, use the `requirements-dev.txt` file:

    ```bash
    pip install -r requirements-dev.txt
    ```

4.  **Set up your `.env` file:**

    Copy `env_example.txt` to `.env` and add your Telegram API credentials.

## GPG Signing for Releases

To enhance security and verify the integrity of releases, this project requires that all version tags be signed with a GPG key.

If you are a contributor who is responsible for creating new releases, you must have a GPG key configured in your local environment.

### 1. Generating a GPG Key

If you don't already have a GPG key, you can generate one by following the instructions on [GitHub's documentation](https://docs.github.com/en/authentication/managing-commit-signature-verification/generating-a-new-gpg-key).

### 2. Adding the GPG Key to Your GitHub Account

Once you have a key, you need to add it to your GitHub account. You can find instructions on how to do this [here](https://docs.github.com/en/authentication/managing-commit-signature-verification/adding-a-new-gpg-key-to-your-github-account).

### 3. Configuring Git to Use Your GPG Key

After adding your key to GitHub, you need to configure Git to use it for signing.

First, list your GPG keys to find the key ID:

```bash
gpg --list-secret-keys --keyid-format LONG
```

From the output, copy the GPG key ID that you want to use. It's the long string of characters after `rsa4096/`.

Then, configure Git to use this key:

```bash
git config --global user.signingkey YOUR_KEY_ID
```

### 4. Updating Your GPG Key's User ID (Optional)

If you need to change the name or email associated with your GPG key, you can do so with the following steps:

1.  Start the interactive key editing process:

    ```bash
    gpg --edit-key YOUR_KEY_ID
    ```

2.  Use the `adduid` command to add a new user ID. You will be prompted for a name and email.

3.  Set the new user ID as the primary one.

4.  Delete the old user ID.

5.  Save your changes.

For a more detailed walkthrough, you can refer to the manual steps provided in the project's documentation.

## Project Structure

The project is organized to separate concerns and make the codebase easy to navigate:

```
.env                 # Your private environment variables
.gitignore           # Git ignore file
README.md            # Main user-facing documentation
CONTRIBUTING.md      # This file: developer-facing documentation
requirements.txt     # Production dependencies for end-users
requirements-dev.txt # All dependencies for developers
main.py              # Minimalist application entry point
release.sh           # Script to automate version bumping and releases

app/                 # Core application logic
├── launcher.py      # Main application orchestrator
├── forwarder.py     # Handles live message forwarding
├── synchronizer.py  # Handles the --copy synchronization logic
└── ...              # Other core modules

config/              # Configuration management
├── config.py        # Pydantic settings class
└── logger.py        # Logging configuration

Logs/                # Directory for log files
sessions/            # Directory for Telethon session files
cache/               # Directory for cached message data
```

## Release Process

Releasing a new version is automated with the `release.sh` script. This script handles updating the version number, generating changelog entries, and creating the git commit and tag.

To create a new release, simply run the script from the `master` branch and specify the part of the version to bump (`patch`, `minor`, or `major`).

**Example: Bumping the patch version**

```bash
./release.sh patch
```

This will:
1.  Find the latest git tag.
2.  Collect all commit messages since that tag.
3.  Run `bump-my-version` to update the version in `pyproject.toml`.
4.  Update `changelog.md` with the new version, date, and the collected commit messages.
5.  Create a new commit with the release.
6.  Create a new git tag for the release.

## Commit Message Guidelines

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. This makes the commit history more readable and allows for automated changelog generation.

Each commit message consists of a **header**, a **body**, and a **footer**.

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Type

Must be one of the following:

-   **feat**: A new feature
-   **fix**: A bug fix
-   **docs**: Documentation only changes
-   **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
-   **refactor**: A code change that neither fixes a bug nor adds a feature
-   **perf**: A code change that improves performance
-   **test**: Adding missing tests or correcting existing tests
-   **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Description

The description should be a short, imperative-tense summary of the change.

**Example**

```
feat: add support for forwarding stickers
```
