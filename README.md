# Alexa Skill to manage KitchenOwl lists

## Prerequisites

1. You will need an Amazon Developer account as well as an AWS account
1. Clone the repository
1. [Create AWS credentials](https://developer.amazon.com/de-DE/docs/alexa/smapi/manage-credentials-with-ask-cli.html#create-aws-credentials)

1. Install the Alexa Skill Kit - <https://developer.amazon.com/en-US/docs/alexa/alexa-skills-kit-sdk-for-python/set-up-the-sdk.html>
1. Configure the Alexa Skill Kit

    ```shell
    ask configure
    ```

    You will need to associate an AWS Profile with ASK CLI.
    When asked for access keys:
    1. Go to the IAM user list and click on the user you just created
    2. Click on the security credentials tab
    3. Scroll down to the access keys section and create a new key
    4. After finish, copy the access keys to ask cli

    If you have trouble getting it to work you can also try it by [using your main aws account](https://stackoverflow.com/a/37947853).

1. Set the correct region (i.e. region=eu-west-1)

    ```
    vim ~/.aws/credentials
    ```

1. Set up config

    Rename `lambda/.env-example` to `lambda/.env`

    Fill in `lambda/.env`

    OR

    You may also set those in the AWS UI as "Environment Variables"
1. Update `skill.json` on first run. This file stores info about endpoints to use after the deployment.

    Rename `skill-package/skill.sample.json` to `skill.json`
1. Install dependencies for development.

    ```
    cd lambda/
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Configuration

- **KITCHENOWL_API_URL**: URL to your instance of KitchenOwl API (for example <https://app.kitchenowl.org/api>)

- **KITCHENOWL_API_KEY**: API token to authenticate against the API. Go to `Profile -> Sessions -> Long-lived tokens` in the WebUI

- **KITCHENOWL_HOUSEHOLD_ID**: The ID of the Household to manage. Visible in the URL when you open KitchenOwl items list in the browser.

## Deployment

### New skill

1. Run

    ```
    ask deploy
    ```

### Existing skill

1. Get the ARN of your lambda function and update `skill-package/skill.json`

    ```json
    "apis": {
      "custom": {}
    },
    ```

    to

    ```json
      "apis": {
        "custom": {
          "endpoint": {
            "uri": "arn:aws:lambda:..."
          }
        }
      },
    ```

1. Add the `/.ask/ask-states.json` you saved from your last deployment
1. Run

    ```
    ask deploy
    ```

## Debugging

```
ask dialog --locale en-US
```
