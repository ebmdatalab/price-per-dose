import pytest
import mock
from mock import patch
from mock import MagicMock
from ebmdatalab import bigquery
from lib import price_utils


@pytest.fixture
def load_test_data():
    bigquery.load_data_from_file(
        'test_hscic', 'prescribing_price_per_pill',
        'tests/data.csv', bigquery.PRESCRIBING_SCHEMA)


def test_get_savings_by_practice(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.get_savings(
        group_by='practice',
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')
    assert len(df) == 4
    assert df.loc[0].practice == 'C88087'
    assert df.loc[0].possible_savings == 900
    assert df.loc[1].practice == 'C88087'
    assert df.loc[1].possible_savings == 45
    assert df.loc[2].practice == 'Y02566'
    assert df.loc[2].possible_savings == 0
    assert df.loc[3].practice == 'Y02566'
    assert df.loc[3].possible_savings == 0


def test_get_savings_by_practice_empty_date(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.get_savings(
        group_by='practice',
        namespace='test_hscic',
        month='2012-08-01',
        prescribing_table='prescribing_price_per_pill')

    assert len(df) == 0


def test_get_savings_by_ccg(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.get_savings(
        group_by='pct',
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')
    assert len(df) == 2
    assert df.loc[0].pct == 'A'
    assert df.loc[0].possible_savings == 900
    assert df.loc[1].pct == 'A'
    assert df.loc[1].possible_savings == 45


def test_get_savings_by_product(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.get_savings(
        group_by='product',
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')

    assert len(df) == 2
    assert df.loc[0].generic_presentation == '040702040AAAMAM'
    assert df.loc[0].possible_savings == 900
    assert df.loc[1].generic_presentation == '040702040AAAGAG'
    assert df.loc[1].possible_savings == 45  # XXX is this what I'd expect?


def test_top_savings_per_entity(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.top_savings_per_entity(
        top_n=1,
        entity='practice',
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')
    assert len(df) == 2
    assert df.loc[0].practice == 'C88087'
    assert df.loc[0].top_savings_sum == 900


def test_all_presentations_in_per_entity_top_n(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.all_presentations_in_per_entity_top_n(
        top_n=1,
        entity='practice',
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')
    assert len(df) == 1
    assert df.loc[0].generic_presentation == '040702040AAAMAM'
    assert df.loc[0].top_savings_sum == 900


def test_cost_savings_at_minimum_for_practice_high(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.cost_savings_at_minimum_for_practice(
        minimum=100,
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')
    assert len(df) == 1
    assert df.loc[0].generic_presentation == '040702040AAAMAM'
    assert df.loc[0].top_savings_sum == 900


def test_cost_savings_at_minimum_for_practice_low(load_test_data, mocker):
    mocker.patch('requests.Session')
    mock_reader = mocker.patch('csv.reader')
    substitutes = [['', '040702040AAAMAM', '', '', '',
          'Y', '', '', 'XXXXXXXXXXXXXXX']]
    mock_reader.return_value.__iter__.return_value = substitutes

    df = price_utils.cost_savings_at_minimum_for_practice(
        minimum=1,
        namespace='test_hscic',
        month='2016-08-01',
        prescribing_table='prescribing_price_per_pill')
    assert len(df) == 2
    print df
    assert df.loc[0].generic_presentation == '040702040AAAMAM'
    assert df.loc[0].top_savings_sum == 900
    assert df.loc[1].generic_presentation == '040702040AAAGAG'
    assert df.loc[1].top_savings_sum == 45
