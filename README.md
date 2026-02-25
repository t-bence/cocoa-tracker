# Cocoa Tracker 🍫 🎶

An automated scraper that monitors the Budapest Festival Orchestra (BFZ) website for new "Cocoa Concert" dates and sends notifications via Telegram.

## Features
- **Scraper**: Periodically checks for new concert dates on the BFZ website.
- **Deduplication**: Uses an S3-backed cache to ensure you only get notified about *new* dates.
- **Notifications**: Sends instant alerts to a Telegram chat.
- **Deployment**: Designed to run as an AWS Lambda function.

## Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)
- AWS Account (for Lambda and S3 storage)
- Telegram Bot Token and Chat ID

## Local Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd cocoa-tracker
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Environment Variables**:
    Create a `.env` file or export the following variables:
    - `TELEGRAM_TOKEN`: Your Telegram Bot API token.
    - `TELEGRAM_CHAT_ID`: The ID of the chat where notifications should be sent.
    - `BUCKET`: The name of the S3 bucket for storing the date cache.

4.  **Run tests**:
    ```bash
    uv run pytest
    ```

## Project Structure
- `src/`: Core logic (scraper, storage, notifications).
- `lambda_function.py`: AWS Lambda entry point.
- `tests/`: Unit and integration tests.
- `build.sh`: Script to package the application for AWS Lambda.

## Deployment

### 1. Build the Package
Run the build script to create a deployment ZIP:
```bash
./build.sh
```
This generates `my_deployment_package.zip`.

### 2. AWS Lambda Setup
1. Create a new Lambda function (Python 3.13).
2. Upload `my_deployment_package.zip`.
3. Set the handler to `lambda_function.lambda_handler`.
4. Configure the required environment variables in the Lambda settings.
5. Ensure the Lambda has an IAM role with permissions to read/write to your S3 bucket.

### 3. S3 Setup
Create an S3 bucket to store the `dates.json` file used for tracking notified dates.

## Development

### Linting and Formatting
This project uses `ruff` for linting and formatting. Pre-commit hooks are configured to run these checks automatically.
```bash
uv run ruff check .
uv run ruff format .
```
