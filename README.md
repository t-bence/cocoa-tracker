# Cocoa Tracker 🍫 🎶

An automated scraper that monitors the Budapest Festival Orchestra (BFZ) website for new "Cocoa Concert" dates and sends notifications via Telegram. It also provides home status monitoring via AWS IoT Core.

## Features

- **Scraper**: Periodically checks for new concert dates on the BFZ website.
- **On-Demand Query**: Trigger an immediate concert check by sending `/query`.
- **Home Status**: Fetch real-time temperature and humidity from an AWS IoT Core Thing by sending `/home`.
- **Deduplication**: Uses an S3-backed cache to ensure you only get notified about *new* dates during scheduled runs.
- **Security**: On-demand commands are restricted to your authorized `TELEGRAM_CHAT_ID`.
- **Notifications**: Sends instant alerts to a Telegram chat.
- **Deployment**: Designed to run as an AWS Lambda function.

## Usage

### Scheduled Runs

The bot is typically triggered by an AWS EventBridge (CloudWatch Events) rule (e.g., once an hour). In this mode, it only notifies you if **new** dates are found since the last run.

### On-Demand Commands

Send these commands to your bot in Telegram:

- **`/query`**: Immediate scrape for all available cocoa concert dates.
- **`/home`**: Fetches current temperature and humidity from your AWS IoT Thing shadow.

Only messages from the `TELEGRAM_CHAT_ID` specified in your configuration will be processed.

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
4. Configure the environment variables in the Lambda settings:
   - `TELEGRAM_TOKEN`: Your Telegram Bot API token.
   - `TELEGRAM_CHAT_ID`: The ID of the chat where notifications should be sent.
   - `BUCKET`: The name of the S3 bucket for storing the date cache.
   - `IOT_THING_NAME`: The name of your AWS IoT Thing.
   - `IOT_SHADOW_NAME` (Optional): The name of the shadow if using a named shadow.
5. Ensure the Lambda has an IAM role with permissions for:
   - **S3**: `s3:GetObject` and `s3:PutObject` for your bucket.
   - **IoT**: `iot:GetThingShadow` for your thing.

### 3. S3 Setup

Create an S3 bucket to store the `dates.json` file used for tracking notified dates.

### 4. Enable On-Demand Commands (Webhook)

To use the `/query` or `/home` commands, you must connect your Telegram bot to your Lambda function:

1. **Create a Function URL**:
   - In the Lambda console, go to **Configuration** -> **Function URL**.
   - Click **Create function URL**.
   - Set **Auth type** to `NONE` (Telegram requires public access).
   - Save and copy the **Function URL**.

2. **Register the Webhook**:
   Run the following command in your terminal (replace placeholders):

   ```bash
   curl -F "url=https://<your-lambda-url-id>.lambda-url.eu-central-1.on.aws/" https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook
   ```

## Development

### Linting and Formatting

This project uses `ruff` for linting and formatting. Pre-commit hooks are configured to run these checks automatically.

```bash
uv run ruff check .
uv run ruff format .
```
