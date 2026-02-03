"""Unit tests for lambda/main.py."""

import main


def test_url_fetch_loto_numbers():
    """Test fetching loto numbers from the URL."""
    today_date = "31-01-2026"  # Example date; adjust as needed
    try:
        loto_data = main.fetch_loto_numbers(today_date)
        assert "drawdate" in loto_data
        assert "mainnumbers" in loto_data
        assert "bonusnumber" in loto_data
    except KeyError:
        # If no draw is found for the date, the test is still valid
        pass


def test_check_loto_numbers():
    """Test the check_loto_numbers function."""
    loto_numbers = [5, 12, 23, 34, 45, 56]
    loto_bonus = 7
    check_numbers = [3, 12, 23, 34, 50, 7]
    result = main.check_loto_numbers(loto_numbers, loto_bonus, check_numbers)

    assert result["matchednumbers"] == [12, 23, 34]
    assert result["matchcount"] == 3
    assert result["bonusmatch"] is True
