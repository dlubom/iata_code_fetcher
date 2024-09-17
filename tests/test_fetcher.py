"""
This module contains unit tests for the iata_code_fetcher.fetcher module, verifying both individual functions
and integration points, with a focus on the fetch_and_process_data and process_and_save_data functions.
"""

from string import ascii_uppercase, digits
from unittest.mock import patch, mock_open
import pytest
from requests.exceptions import RequestException
from iata_code_fetcher.fetcher import (
    generate_codes,
    fetch_and_process_data,
    process_and_save_data,
    CodeType,
)


@pytest.fixture(name="carrier_response_mock")
def mock_carrier_response():
    """
    Provides a mock HTML response for a carrier code search.
    """
    return """
    <table class="datatable">
        <thead>
        <tr>
            <td>Company name</td>
            <td>Country / Territory</td>
            <td>2-letter code</td>
        </tr>
        </thead>
        <tbody>
            <tr>
                <td>BONZA AVIATION PTY LTD</td>
                <td>Australia</td>
                <td>AB</td>
            </tr>
            <tr>
                <td>West Atlantic Sweden AB</td>
                <td>Sweden</td>
                <td>T2</td>
            </tr>
        </tbody>
    </table>
    """


@pytest.fixture(name="airport_response_mock")
def mock_airport_response():
    """
    Provides a mock HTML response for an airport code search.
    """
    return """
    <table class="datatable">
        <thead>
        <tr>
            <td>City Name</td>
            <td>Airport Name</td>
            <td>3-letter location code</td>
        </tr>
        </thead>
        <tbody>
            <tr>
                <td>Anaa</td>
                <td>Anaa Airport</td>
                <td>AAA</td>
            </tr>
        </tbody>
    </table>
    """


@patch("requests.get")
def test_fetch_and_process_data_carrier(mock_get, carrier_response_mock):
    """
    Test fetch_and_process_data function with a mocked carrier code response to ensure it parses data correctly.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = carrier_response_mock

    data = fetch_and_process_data("AA", CodeType.CARRIER)

    expected_data = [
        {
            "Company name": "BONZA AVIATION PTY LTD",
            "Country / Territory": "Australia",
            "2-letter code": "AB",
        },
        {
            "Company name": "West Atlantic Sweden AB",
            "Country / Territory": "Sweden",
            "2-letter code": "T2",
        },
    ]

    assert data == expected_data


@patch("requests.get")
def test_fetch_and_process_data_airport(mock_get, airport_response_mock):
    """
    Test fetch_and_process_data function with a mocked airport code response to ensure it correctly parses data.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = airport_response_mock

    data = fetch_and_process_data("AAA", CodeType.AIRPORT)

    expected_data = [
        {
            "City Name": "Anaa",
            "Airport Name": "Anaa Airport",
            "3-letter location code": "AAA",
        }
    ]

    assert data == expected_data


@patch("requests.get")
def test_fetch_and_process_data_error(mock_get):
    """
    Test fetch_and_process_data function with network error.
    """
    mock_get.side_effect = RequestException("Network error")

    with pytest.raises(RequestException):
        _ = fetch_and_process_data("AA", CodeType.CARRIER)


@patch("builtins.open", new_callable=mock_open)
@patch("requests.get")
def test_process_and_save_data_carrier(mock_get, mock_file, carrier_response_mock):
    """
    Test test_process_and_save_data_carrier function with a mocked carrier code.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = carrier_response_mock

    with patch("time.sleep", return_value=None):
        process_and_save_data(CodeType.CARRIER)

    mock_file.assert_called_with("carrier_data_full.jsonl", "a", encoding="UTF-8")
    mock_file().write.assert_any_call(
        '{"Company name": "BONZA AVIATION PTY LTD", "Country / Territory": "Australia", "2-letter code": "AB"}\n'
    )
    mock_file().write.assert_any_call(
        '{"Company name": "West Atlantic Sweden AB", "Country / Territory": "Sweden", "2-letter code": "T2"}\n'
    )


@patch("builtins.open", new_callable=mock_open)
@patch("requests.get")
def test_process_and_save_data_airport(mock_get, mock_file, airport_response_mock):
    """
    Test test_process_and_save_data_carrier function with a mocked airport code.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = airport_response_mock

    with patch("time.sleep", return_value=None):
        process_and_save_data(CodeType.AIRPORT)

    mock_file.assert_called_with("airport_data_full.jsonl", "a", encoding="UTF-8")
    mock_file().write.assert_any_call(
        '{"City Name": "Anaa", "Airport Name": "Anaa Airport", "3-letter location code": "AAA"}\n'
    )


def test_generate_codes_for_two_letter_codes():
    """
    Test to ensure the function generates two-letter codes correctly,
    including letters and digits.
    """
    length = 2  # Test with two-character codes
    codes = list(generate_codes(length))
    expected_number_of_codes = 36**2  # 26 letters + 10 digits = 36 characters

    # Check if all codes have the correct length
    assert all(len(code) == length for code in codes), f"All codes must have the specified length of {length}"

    # Check the total number of generated codes
    assert (
        len(codes) == expected_number_of_codes
    ), f"The number of generated two-character codes should be {expected_number_of_codes}"

    # Check specific codes to ensure correct sequence
    assert codes[0] == "AA", "The first code should be 'AA'"
    assert codes[-1] == "99", "The last code should be '99'"

    # Optional: Check that all codes consist of only uppercase letters and digits
    allowed_characters = set(ascii_uppercase + digits)
    assert all(all(char in allowed_characters for char in code) for code in codes), "All codes must consist of uppercase letters and digits"


def test_generate_codes_for_three_letter_codes():
    """
    Test to ensure the function generates three-letter codes correctly,
    including letters and digits.
    """
    length = 3  # Test with three-character codes
    codes = list(generate_codes(length))
    expected_number_of_codes = 36**3  # 26 letters + 10 digits = 36 characters

    # Check if all codes have the correct length
    assert all(len(code) == length for code in codes), f"All codes must have the specified length of {length}"

    # Check the total number of generated codes
    assert (
        len(codes) == expected_number_of_codes
    ), f"The number of generated three-character codes should be {expected_number_of_codes}"

    # Check specific codes to ensure correct sequence
    assert codes[0] == "AAA", "The first code should be 'AAA'"
    assert codes[-1] == "999", "The last code should be '999'"

    # Optional: Check that all codes consist of only uppercase letters and digits
    allowed_characters = set(ascii_uppercase + digits)
    assert all(all(char in allowed_characters for char in code) for code in codes), "All codes must consist of uppercase letters and digits"


if __name__ == "__main__":
    pytest.main()
