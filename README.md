# pyTelegramDialogsMirror

<p align="center">
  <a href="https://github.com/zv09/pyTelegramDialogsMirror">
    <img src="https://komarev.com/ghpvc/?username=zv09&label=Visits&color=ff69b4&style=flat-square" alt="Visits"/>
  </a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python Version"/>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"/>
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-lightgrey.svg" alt="License: MIT"/>
  </a>
</p>
<p align="center">
  <a href="https://github.com/zv09/pyTelegramDialogsMirror/releases/latest">
    <img src="https://img.shields.io/github/v/release/zv09/pyTelegramDialogsMirror?color=add8e6" alt="GitHub release (latest by date)"/>
  </a>
  <a href="https://github.com/zv09/pyTelegramDialogsMirror/tags">
    <img src="https://img.shields.io/github/v/tag/zv09/pyTelegramDialogsMirror?color=add8e6" alt="GitHub tag (latest by date)"/>
  </a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/zv09/pyTelegramDialogsMirror"/>
</p>
<p align="center">
  <a href="docs/donations.md">
    <img src="https://img.shields.io/badge/Donate-Support%20Project-gold.svg" alt="Donate"/>
  </a>
</p>


## [Support the Project](docs/donations.md) <a name="support"></a>

If you find this tool useful, please consider supporting its development. Donations help cover server costs and allow for more time to be dedicated to new features and maintenance.

- <img src="https://cdn.simpleicons.org/ton/0098EA?viewbox=auto" alt="TON" height="20" /> TON or <img src="https://cdn.simpleicons.org/tether/50AF95?viewbox=auto" alt="USDT" height="20" /> USDT (TON): `UQBayvQUyg8Ks--mVmQVCw0dTbsjIs8TuPgPrShtd0lWt4Pc`
- <img src="https://cdn.simpleicons.org/tether/50AF95?viewbox=auto" alt="USDT" height="20" /> USDT (TRC-20): `TEMU7xgvHMKC2VowLzcaDqgVmamzZKwDxL`

**For more information and addresses** on how to donate, please see the [Donations page](docs/donations.md).


## Outline

- [Support the Project](#support)
- [Overview](#overview)
- [Features](#features)
- [Setup](#setup)
- [Configuration](#configuration)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Usage](#usage)
- [Development Workflow Diagram](#development-workflow-diagram)
- [Contributing](#contributing)

## Overview

This is a Python script that forwards messages from specified source Telegram channels to target Telegram channels. It is built using `telethon` and `pydantic-settings` for robust configuration management.

## Features

-   **Full Media Support:** Forwards all message types, including text, photos, videos, documents, audio, and web page previews.
-   **System Message Handling:** Correctly forwards system messages (e.g., "user joined") as placeholders to maintain sequence integrity.
-   **Message Synchronization (`--copy` mode):** A powerful command-line option to perform a deep synchronization between a source and target channel. It intelligently finds the first point of divergence, deletes incorrect messages from the target, and resends the correct sequence from the source, ensuring a perfect mirror.
-   **Robust Error Handling:** Includes specific handling for common `telethon` exceptions and uses a batching strategy with pauses to effectively avoid `FloodWaitError` during synchronization.
-   **Performance Caching:** Caches message data to disk to speed up subsequent synchronization runs.
-   **Dynamic Channel Mappings:** Configure multiple source-to-target channel forwarding rules.
-   **Informative Logging:** Provides detailed logs including sender information and message types.
-   **Graceful Shutdown:** Handles `Ctrl+C` and `SIGTERM` for clean application termination.
-   **OOP Structure:** A clean, object-oriented design for maintainability and extensibility.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd pyTelegramDialogsMirror
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**

    Copy the `env_example.txt` file to `.env` and fill in your Telegram API credentials and channel mappings.

    ```bash
    cp env_example.txt .env
    ```

    Open `.env` and replace the placeholder values:

    ```
    API_ID=YOUR_API_ID
    API_HASH=YOUR_API_HASH
    APP_NAME=pyTelegramDialogsMirror
    CHANNEL_MAPPINGS_STR="SOURCE_CHANNEL_ID_1,TARGET_CHANNEL_ID_1;SOURCE_CHANNEL_ID_2,TARGET_CHANNEL_ID_2"
    ```

    -   `API_ID` and `API_HASH`: Obtain these from [my.telegram.org](https://my.telegram.org/).
    -   `APP_NAME`: A name for your application session file (e.g., `pyTelegramDialogsMirror`).
    -   `CHANNEL_MAPPINGS_STR`: A semicolon-separated string of source and target channel ID pairs. For example, `"-100123456789,-100987654321"` would forward messages from channel `-100123456789` to `-100987654321`.

## Configuration

The following environment variables can be configured in the `.env` file to fine-tune the application's performance:

-   `BATCH_SIZE`: The number of messages to process in a single batch during synchronization (`--copy` mode). A smaller batch size can help avoid `FloodWaitError` but may slow down the overall process. Default: `150`.
-   `MAX_CACHE_SIZE`: The maximum number of dialog (user/channel) names to keep in memory. This is a performance optimization that uses a small amount of memory to avoid repeated lookups for dialog names. A larger size can improve performance if you interact with many different users/channels. Memory usage is minimal: 200 items is ~35KB; 1000 items is ~175KB. Default: `200`.

For developers, more detailed configuration parameters and their implications are discussed in the [Contributing Guidelines](CONTRIBUTING.md#configuration-parameters). Users seeking advanced customization should refer to the developer documentation.

## Advanced Configuration <a name="advanced-configuration"></a>

This section will contain more advanced configuration options. (Content to be added later)

## Troubleshooting <a name="troubleshooting"></a>

This section will contain common issues and their solutions. (Content to be added later)

## Usage

### Live Forwarding Mode

To start the application in live forwarding mode, which will monitor source channels and forward new messages as they arrive, run:

**On Linux or macOS:**
```bash
./main.py
```

**On Windows:**
```bash
python main.py
```

### Synchronization Mode

To run a one-time synchronization that ensures the target channel is a perfect mirror of the source channel, use the `--copy` flag:

**On Linux or macOS:**
```bash
./main.py --copy
```

**On Windows:**
```bash
python main.py --copy
```

This mode will:
1.  Fetch messages from both the source and target channels.
2.  Compare them to find the first difference.
3.  Delete all incorrect messages from the target channel starting from the point of divergence.
4.  Resend the correct sequence of messages (including all media and system message placeholders) from the source.

### Dry Run Mode (Safe Preview)

To see what the Synchronization Mode *would* do without making any actual changes, use the `--dry-run` (or `-dr`) flag along with `--copy`.

**On Linux or macOS:**
```bash
./main.py --copy --dry-run
```

**On Windows:**
```bash
python main.py --copy --dry-run
```

This will perform a full analysis, showing you exactly how many messages would be copied and deleted, and then exit without modifying anything. It is highly recommended to run this first to ensure your configuration is correct.

### Session Management

The application now includes robust session management to handle multiple accounts or session files gracefully.

**Automatic Session Handling:**
- **No Sessions:** If no `.session` files are found, the application will create a new one using the `APP_NAME` from your `.env` file.
- **One Session:** If a single `.session` file is found, it will be used automatically.
- **Multiple Sessions:** If multiple `.session` files are found, you will be prompted to choose which one to use.

**Manual Session Selection:**

You can bypass the automatic selection and specify a session file directly using the `-s` or `--session` flag. The application will look for this file in the `sessions/` directory.

**Example:**
```bash
./main.py -s my_other_session
```
This command will force the application to use the `sessions/my_other_session.session` file.



## Contributing

Contributions are welcome! If you'd like to contribute to the project, please see the [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started, the project structure, and the release process.
