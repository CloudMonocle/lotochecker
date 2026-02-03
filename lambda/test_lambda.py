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


def test_ssm_fetch_numbers():
    """Test fetching loto numbers from SSM Parameter Store."""
    parameter_name = "/lotocheck/lotonumbers"
    aws_region = "eu-west-1"
    numbers_json = main.fetch_numbers_from_ssm(parameter_name, aws_region)
    assert isinstance(numbers_json, list)


def test_check_loto_numbers():
    """Test the check_loto_numbers function."""
    loto_numbers = [5, 12, 23, 34, 45, 56]
    loto_bonus = 7
    check_numbers = [3, 12, 23, 34, 50, 7]
    result = main.check_loto_numbers(loto_numbers, loto_bonus, check_numbers)

    assert result["matchednumbers"] == [12, 23, 34]
    assert result["matchcount"] == 3
    assert result["bonusmatch"] is True
