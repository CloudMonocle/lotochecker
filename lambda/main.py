"""Lambda Fucntion to get latest Loto numbers and compare with stored numbers."""

import json
import os

import boto3
import pandas as pd


def fetch_loto_numbers():
    """Fetch latest Loto numbers from National Lottery site."""
    loto_df = pd.read_csv(
        "https://www.national-lottery.co.uk/results/lotto/draw-history/csv"
    )
    first_row = (loto_df.head(1)).to_json(orient="records")
    return json.loads(first_row)[0]


def check_loto_numbers(loto_numbers, loto_bonus, check_numbers):
    """Fetch latest Loto numbers and compare with stored numbers."""
    match_numbers = []
    for i in range(1, 7):
        if loto_numbers[i - 1] in check_numbers:
            match_numbers.append(loto_numbers[i - 1])
    bonus_match = loto_bonus in check_numbers
    return {
        "checkednumbers": check_numbers,
        "matchednumbers": match_numbers,
        "matchcount": len(match_numbers),
        "bonusmatch": bonus_match,
    }


def format_sns_message(msgdata):
    """Format SNS message from loto results data."""
    sns_msg = f"Loto Results for {msgdata['drawdate']}\n"
    sns_msg += f"Numbers: {', '.join(str(n) for n in msgdata['numbers'])}\n"
    sns_msg += f"Bonus Ball: {msgdata['bonus ball']}\n"
    sns_msg += "Check Results:\n"
    for check in msgdata["checks"]:
        if check["matchcount"] > 1:
            sns_msg += (
                f" - Numbers: {', '.join(str(n) for n in check['checkednumbers'])}\n"
            )
            sns_msg += (
                f" \t Matched: {', '.join(str(n) for n in check['matchednumbers'])}\n"
            )
            sns_msg += f" \t Bonus Match: {'Yes' if check['bonusmatch'] else 'No'}"
            if check["matchcount"] == 2:
                sns_msg += "\n"
                sns_msg += "\t \t (Lucky Dip Win!)"
            # will add moew when knowing
            sns_msg += "\n"
    return sns_msg


def aws_send_sns_message(
    sns_msg, sns_topic_arn, aws_region, discord_channel="testingstuff"
):
    """Send SNS message using boto3."""
    sns = boto3.client(
        "sns",
        region_name=aws_region,
    )
    sns.publish(
        TopicArn=sns_topic_arn,
        Subject="Loto RESULTs",
        Message=sns_msg,
        MessageAttributes={
            "discord_channel": {"DataType": "String", "StringValue": discord_channel},
        },
    )


def lambda_handler(event, context):  # pylint: disable=W0613
    """Lambda handler function."""
    logores = fetch_loto_numbers()
    loto_results = {}

    # get the draw numbers and date
    loto_results["drawdate"] = logores["DrawDate"]
    loto_results["numbers"] = [logores[f"Ball {i}"] for i in range(1, 7)]
    loto_results["bonus ball"] = logores["Bonus Ball"]
    loto_results["checks"] = []

    # get stored numbers
    if os.environ.get("NUMBERS_JSON", None) is None:
        print("No stored numbers json found")
    elif os.path.exists(os.environ.get("NUMBERS_JSON")):
        json_path = os.environ.get("NUMBERS_JSON")
        with open(json_path, "r", encoding="utf-8") as f:
            for lnumb in json.load(f):
                loto_results["checks"].append(
                    check_loto_numbers(
                        loto_numbers=loto_results["numbers"],
                        loto_bonus=loto_results["bonus ball"],
                        check_numbers=lnumb,
                    )
                )
    sns_topic = os.environ.get("SNS_TOPIC_ARN", None)
    discord_channel = os.environ.get("DISCORD_CHANNEL")
    if (sns_topic is None or sns_topic == "") or (
        os.environ.get("DISCORD_CHANNEL", None) is None or discord_channel == ""
    ):
        print("No sns ARN found or no discord channel, returning results only")
        return {"statusCode": 200, "body": json.dumps(loto_results)}
    # sedn the message
    print(format_sns_message(loto_results))
    aws_send_sns_message(
        discord_channel=discord_channel,
        sns_msg=format_sns_message(loto_results),
        sns_topic_arn=sns_topic,
        aws_region=os.environ.get("AWS_REGION", boto3.session.Session().region_name),
    )
    return {"statusCode": 200}
