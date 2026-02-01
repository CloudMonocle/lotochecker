"""Automated process to check Loto numbers and send SNS message with results."""

import json
import logging
import os
from datetime import datetime

import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fetch_loto_numbers(today_date):
    """Retrieve Loto numbers from National Lottery API for the given date."""
    url = "https://api-dfe.national-lottery.co.uk/draw-game/results/1"
    response = requests.get(url, timeout=10)
    json_data = response.json().get("drawResults", [])
    for draw in json_data:
        drawdate = datetime.strptime(
            draw.get("drawDate"), "%Y-%m-%dT%H:%M:%S.%fZ"
        ).strftime("%d-%m-%Y")
        if drawdate == today_date:
            dawn_numbers = draw.get("drawnNumbers").get("drawnNumbers")
            return {
                "drawdate": drawdate,
                "mainnumbers": dawn_numbers.get("primaryNumbers"),
                "bonusnumber": dawn_numbers.get("secondaryNumbers")[0],
            }
    logger.warning("No draw found for date: %s", {today_date})
    return None


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
    loto_data = fetch_loto_numbers(datetime.today().strftime("%d-%m-%Y"))
    loto_results = []

    if os.environ.get("NUMBERS_JSON", None) is None:
        logger.warning("Missing json environment variable using test example data")

    json_path = os.environ.get("NUMBERS_JSON", "loto_numers.json.example")
    with open(json_path, "r", encoding="utf-8") as f:
        stored_numbers = json.load(f)
    for entry in stored_numbers:
        results = check_loto_numbers(
            loto_numbers=loto_data["mainnumbers"],
            loto_bonus=loto_data["bonusnumber"],
            check_numbers=entry,
        )
        if results.get("matchcount", 0) > 1:
            loto_results.append(results)

    sns_msg = f"Loto Draw Date: {loto_data['drawdate']}\n"
    sns_msg += f"\t- Numbers: {', '.join(str(n) for n in loto_data['mainnumbers'])}\n"
    sns_msg += f"\t- Bonus Ball: {loto_data['bonusnumber']}\n"
    if len(loto_results) > 0:
        sns_msg += "Loto Results:\n"
        for loto_result in loto_results:
            sns_msg += f"\t -Numbers: {', '.join(str(n) for n in loto_result['checkednumbers'])}\n"
            sns_msg += f" \t\t Matched: {', '.join(str(n) for n in loto_result['matchednumbers'])}"
            if loto_result["bonusmatch"]:
                sns_msg += " and Bonus Ball"

            if loto_result["matchcount"] == 6:
                sns_msg += " (!!JACKPOT WIN!!)"
            elif loto_result["matchcount"] == 5 and loto_result["bonusmatch"]:
                sns_msg += " (Good Cash Win!)"
            elif loto_result["matchcount"] == 5 or (
                loto_result["matchcount"] == 4 or loto_result["matchcount"] == 3
            ):
                sns_msg += " (Low Cash Win!)"
            elif loto_result["matchcount"] == 2:
                sns_msg += " (Lucky Dip Win!)"
            # will add moew when knowing
            sns_msg += "\n"
    else:
        sns_msg += "Loto Results: No numbers matched\n"

    sns_topic = os.environ.get("SNS_TOPIC_ARN", None)
    discord_channel = os.environ.get("DISCORD_CHANNEL")
    if (sns_topic is None or sns_topic == "") or (
        os.environ.get("DISCORD_CHANNEL", None) is None or discord_channel == ""
    ):
        logger.error("SNS Topic or Discord Channel not set, printing message instead")
        print(sns_msg)
        return {"statusCode": 200}

    logger.info("Sending SNS message")
    aws_send_sns_message(
        discord_channel=discord_channel,
        sns_msg=sns_msg,
        sns_topic_arn=sns_topic,
        aws_region=os.environ.get("AWS_REGION", boto3.session.Session().region_name),
    )
    return {"statusCode": 200}


# # For testing locally
# if __name__ == "__main__":
#     lambda_handler(None, None)
