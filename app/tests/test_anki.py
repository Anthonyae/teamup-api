"""
This is a testing module for anki
"""

import pytest
import pandas as pd


from app.anki import AnkiDB


def test_call_anki_class():
    """
    Checks to see if anki object exists.
    """
    obj = AnkiDB()
    assert obj


def test_query_anki_db():
    """
    Checks to see that the the anki class can query the database.
    """
    anki = AnkiDB()
    result_set = anki.query_db("select 1 as test")
    assert result_set


def test_query_exception_handling():
    """
    Confirms that running invalid sql code returns an error from the AnkiDB class.
    """
    anki = AnkiDB()
    with pytest.raises(Exception):
        anki.query_db("invalid sql")


def test_reviews_dataframe():
    """
    Checks to seee a dataframe and its post processed column is handled correctly.
    """
    anki = AnkiDB()
    result_df = anki.reviews(ending_parameters="limit 5")
    assert isinstance(result_df, pd.DataFrame)
    assert "deck_name" in result_df.columns


def test_create_habitify_entry():
    """
    Confirms that the entry matches Habitify api requirement for submitting time entries.
    """
    for col in columns:
        assert col in result.columns
