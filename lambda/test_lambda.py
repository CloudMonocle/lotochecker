"""Unit tests for lambda/main.py."""

import main


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
