"""Unit tests for lambda/main.py."""

import main
import requests


def test_url_fetch_loto_numbers():
    """Test fetching loto numbers from the URL."""
    url = "https://api-dfe.national-lottery.co.uk/draw-game/results/1"
    response = requests.get(url, timeout=10)
    assert response.status_code == 200
    data = response.json().get("drawResults", [])
    assert isinstance(data, list)
    assert len(data) > 0
    draw = data[0]
    assert "drawDate" in draw
    assert "primaryNumbers" in draw.get("drawnNumbers").get("drawnNumbers")
    assert "secondaryNumbers" in draw.get("drawnNumbers").get("drawnNumbers")


def test_check_loto_numbers():
    """Test the check_loto_numbers function."""
    loto_numbers = [5, 12, 23, 34, 45, 56]
    loto_bonus = 7
    check_numbers = [3, 12, 23, 34, 50, 7]
    result = main.check_loto_numbers(loto_numbers, loto_bonus, check_numbers)

    assert result["matchednumbers"] == [12, 23, 34]
    assert result["matchcount"] == 3
    assert result["bonusmatch"] is True


def test_fetch_loto_numbers():
    """Test the fetch_loto_numbers function."""
    result = main.fetch_loto_numbers()
    assert "DrawDate" in result
    assert all(f"Ball {i}" in result for i in range(1, 7))
    assert "Bonus Ball" in result


def test_format_sns_message():
    """Test the format_sns_message function."""
    msgdata = {
        "drawdate": "2024-06-01",
        "numbers": [5, 12, 23, 34, 45, 56],
        "bonus ball": 7,
        "checks": [
            {
                "checkednumbers": [3, 12, 23, 34, 50, 7],
                "matchednumbers": [12, 23, 34],
                "matchcount": 3,
                "bonusmatch": True,
            }
        ],
    }
    sns_msg = main.format_sns_message(msgdata)
    assert "Loto Results for 2024-06-01" in sns_msg
    assert "Numbers: 5, 12, 23, 34, 45, 56" in sns_msg
    assert "Bonus Ball: 7" in sns_msg
    assert "Matched: 12, 23, 34" in sns_msg
    assert "Bonus Match: Yes" in sns_msg


def test_sns_message():
    """Test the aws_send_sns_message function."""
    try:
        msgdata = {
            "drawdate": "2024-06-01",
            "numbers": [5, 12, 23, 34, 45, 56],
            "bonus ball": 7,
            "checks": [
                {
                    "checkednumbers": [3, 12, 23, 34, 50, 7],
                    "matchednumbers": [12, 23],
                    "matchcount": 2,
                    "bonusmatch": False,
                }
            ],
        }
        sns_msg = main.format_sns_message(msgdata)
        print(sns_msg)
        main.aws_send_sns_message(
            sns_msg,
            sns_topic_arn="arn:aws:sns:eu-west-1:519388350760:awssetup-dub-sns-orgalerts",
            aws_region="eu-west-1",
        )
    except Exception as e:  # pylint: disable=W0718
        assert False, f"aws_send_sns_message raised an exception: {e}"
