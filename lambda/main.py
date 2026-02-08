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
    logger.info("Fetched Loto numbers from API for date: %s", today_date)
    for draw in json_data:
        drawdate = datetime.strptime(
            draw.get("drawDate"), "%Y-%m-%dT%H:%M:%S.%fZ"
        ).strftime("%d-%m-%Y")
        if drawdate == today_date:
            logger.info("Found draw for date: %s", today_date)
            dawn_numbers = draw.get("drawnNumbers").get("drawnNumbers")
            return {
                "drawdate": drawdate,
                "mainnumbers": dawn_numbers.get("primaryNumbers"),
                "bonusnumber": dawn_numbers.get("secondaryNumbers")[0],
            }
    logger.warning("No draw found for date: %s", {today_date})
    raise KeyError("No draw found for the given date")


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


def fetch_numbers_from_ssm(parameter_name, aws_region):
    """Retrieve Loto numbers JSON from SSM Parameter Store."""
    ssm = boto3.client("ssm", region_name=aws_region)
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        numbers_json = json.loads(response["Parameter"]["Value"])
        logger.info(
            "Successfully retrieved numbers from SSM parameter: %s", parameter_name
        )
        return numbers_json
    except ssm.exceptions.ParameterNotFound:
        logger.error("SSM parameter not found: %s", parameter_name)
        raise
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON from SSM parameter: %s", str(e))
        raise


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
    datetouse = os.environ.get("DATE_TO_USE", datetime.today().strftime("%d-%m-%Y"))
    loto_data = fetch_loto_numbers(datetouse)
    loto_results = []

    aws_region = os.environ.get("AWS_REGION", boto3.session.Session().region_name)
    ssm_parameter_name = os.environ.get("SSM_PARAMETER_NAME", "/lotocheck/lotonumbers")

    try:
        stored_numbers = fetch_numbers_from_ssm(ssm_parameter_name, aws_region)
    except Exception as e:
        logger.error("Failed to retrieve numbers from SSM: %s", str(e))
        raise
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
