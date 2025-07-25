# Telegram Dialogs Mirror

[![Donate](https://img.shields.io/badge/Donate-Support%20Project-gold.svg)](docs/donations.md)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/zv09/TelegramDialogsMirror)](https://github.com/zv09/TelegramDialogsMirror/releases/latest)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/zv09/TelegramDialogsMirror)](https://github.com/zv09/TelegramDialogsMirror/tags)
[![Visits Badge](https://komarev.com/ghpvc/?username=zv09&style=flat-square&color=blue)](https://github.com/zv09/pyTelegramDialogsMirror)


## [Support the Project](docs/donations.md) <a name="support"></a>

If you find this tool useful, please consider supporting its development. Donations help cover server costs and allow for more time to be dedicated to new features and maintenance.

For more information on how to donate, please see the [Donations page](docs/donations.md).

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
    cd TelegramDialogsMirror
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
    APP_NAME=TelegramDialogsMirror
    CHANNEL_MAPPINGS_STR="SOURCE_CHANNEL_ID_1,TARGET_CHANNEL_ID_1;SOURCE_CHANNEL_ID_2,TARGET_CHANNEL_ID_2"
    ```

    -   `API_ID` and `API_HASH`: Obtain these from [my.telegram.org](https://my.telegram.org/).
    -   `APP_NAME`: A name for your application session file (e.g., `TelegramDialogsMirror`).
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

### Live Forwarding Mode

To start the application in live forwarding mode, which will monitor source channels and forward new messages as they arrive, run:

```bash
python3 main.py
```

### Synchronization Mode

To run a one-time synchronization that ensures the target channel is a perfect mirror of the source channel, use the `--copy` flag:

```bash
python3 main.py --copy
```

This mode will:
1.  Fetch messages from both the source and target channels.
2.  Compare them to find the first difference.
3.  Delete all incorrect messages from the target channel starting from the point of divergence.
4.  Resend the correct sequence of messages (including all media and system message placeholders) from the source.



## Contributing

Contributions are welcome! If you'd like to contribute to the project, please see the [Contributing Guidelines](CONTRIBUTING.md) for more information on how to get started, the project structure, and the release process.


