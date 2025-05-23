import unittest
from unittest.mock import patch, MagicMock

# It's important to be able to import the DataStore class
# This might require sys.path manipulation if 'libs' isn't installed
# or recognized as a package in the test environment.
# For now, we assume it can be imported.
# If not, the test execution will fail at the import stage,
# and we might need to add sys.path adjustments in tests/main.py or here.
from libs.datastore.main import DataStore
from libs.datastore.db import Database # Imported for type hinting if needed, not directly used by tests yet

# Environment variable for the database connection string
# We need to ensure this is set, even if mocked, to prevent Database class's own checks from failing
# if its __init__ or get_pool methods are inadvertently called without full mocking.
import os
os.environ['QDB_CONNECTION_STRING'] = 'mock_connection_string_for_testing'


@patch('libs.datastore.db.psycopg_pool.ConnectionPool')
class TestDataStore(unittest.TestCase):

    @patch('libs.datastore.db.Database.get_connection')
    def test_get_ticker_found(self, mock_get_connection, mock_psycopg_pool):
        # Example of setting up the mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Configure mock_get_connection to return a context manager that yields mock_conn
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Configure mock_cursor.fetchone to return sample data
        sample_ticker_data = ('TEST.NSE', 'FETCH_KEY_TEST', 'NSE', 'TESTTICKER', 0.05, 
                              'Test Ticker Name', 'EQ', 'IND', 'NSE', '12345', 1.0, 1.0, 
                              True, False, '2023-01-01 10:00:00', '2023-01-01 09:00:00')
        mock_cursor.fetchone.return_value = sample_ticker_data

        ds = DataStore()
        result = ds.get_ticker('TEST.NSE')

        self.assertEqual(result, sample_ticker_data)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM symbols WHERE query_key = %s", ('TEST.NSE',))
        # Example: mock_psycopg_pool.assert_not_called() # Or assert it was called if expected

    @patch('libs.datastore.db.Database.get_connection')
    def test_get_ticker_not_found(self, mock_get_connection, mock_psycopg_pool):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Configure mock_cursor.fetchone to return None
        mock_cursor.fetchone.return_value = None

        ds = DataStore()
        
        with self.assertRaises(ValueError) as context:
            ds.get_ticker('UNKNOWN.NSE')
        
        self.assertEqual(str(context.exception), "Ticker UNKNOWN.NSE not found in database")
        mock_cursor.execute.assert_called_once_with("SELECT * FROM symbols WHERE query_key = %s", ('UNKNOWN.NSE',))

    @patch('libs.datastore.db.Database.get_connection')
    @patch('libs.datastore.main.DataStore.get_ticker') # Mocking get_ticker directly for some tests
    def test_add_to_priority_success(self, mock_get_ticker, mock_get_connection, mock_psycopg_pool):
        # Configure mock_get_ticker to simulate ticker found
        mock_get_ticker.return_value = ('TEST.NSE', 'details...') # Only needs to be non-None

        # Configure database mocks for the UPDATE operation
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1 # Simulate successful update

        ds = DataStore()
        ds.add_to_priority('TEST.NSE')

        mock_get_ticker.assert_called_once_with('TEST.NSE')
        mock_cursor.execute.assert_called_once_with(
            "UPDATE symbols SET priority = TRUE WHERE query_key = %s", ('TEST.NSE',)
        )
        mock_conn.commit.assert_called_once()

    @patch('libs.datastore.main.DataStore.get_ticker')
    def test_add_to_priority_ticker_not_found(self, mock_get_ticker, mock_psycopg_pool):
        # Configure mock_get_ticker to simulate ticker not found by raising ValueError
        # This matches the behavior if the underlying DB call in get_ticker found nothing.
        mock_get_ticker.side_effect = ValueError("Ticker TEST.NSE not found in database")

        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.add_to_priority('TEST.NSE')
        
        self.assertEqual(str(context.exception), "Ticker TEST.NSE not found in database")
        mock_get_ticker.assert_called_once_with('TEST.NSE')

    @patch('libs.datastore.db.Database.get_connection')
    @patch('libs.datastore.main.DataStore.get_ticker')
    def test_add_to_priority_update_fails(self, mock_get_ticker, mock_get_connection, mock_psycopg_pool):
        # Configure mock_get_ticker
        mock_get_ticker.return_value = ('TEST.NSE', 'details...')

        # Configure database mocks for the UPDATE operation
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0 # Simulate failed update (no rows affected)

        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.add_to_priority('TEST.NSE')
        
        self.assertEqual(str(context.exception), "Failed to update priority for ticker TEST.NSE")
        mock_get_ticker.assert_called_once_with('TEST.NSE')
        mock_cursor.execute.assert_called_once_with(
            "UPDATE symbols SET priority = TRUE WHERE query_key = %s", ('TEST.NSE',)
        )
        mock_conn.commit.assert_not_called() # Commit should not be called if rowcount is 0

    def test_add_to_priority_ticker_is_none(self, mock_psycopg_pool):
        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.add_to_priority(None) # type: ignore
        self.assertEqual(str(context.exception), "Ticker cannot be None")

    @patch('libs.datastore.db.Database.get_connection')
    @patch('libs.datastore.main.DataStore.get_ticker')
    def test_remove_from_priority_success(self, mock_get_ticker, mock_get_connection, mock_psycopg_pool):
        mock_get_ticker.return_value = ('TEST.NSE', 'details...')

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1 # Simulate successful update

        ds = DataStore()
        ds.remove_from_priority('TEST.NSE')

        mock_get_ticker.assert_called_once_with('TEST.NSE')
        mock_cursor.execute.assert_called_once_with(
            "UPDATE symbols SET priority = FALSE WHERE query_key = %s", ('TEST.NSE',)
        )
        mock_conn.commit.assert_called_once()

    @patch('libs.datastore.main.DataStore.get_ticker')
    def test_remove_from_priority_ticker_not_found(self, mock_get_ticker, mock_psycopg_pool):
        mock_get_ticker.side_effect = ValueError("Ticker TEST.NSE is not available") # Match expected error message

        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.remove_from_priority('TEST.NSE')
        
        self.assertEqual(str(context.exception), "Ticker TEST.NSE is not available")
        mock_get_ticker.assert_called_once_with('TEST.NSE')

    @patch('libs.datastore.db.Database.get_connection')
    @patch('libs.datastore.main.DataStore.get_ticker')
    def test_remove_from_priority_update_fails(self, mock_get_ticker, mock_get_connection, mock_psycopg_pool):
        mock_get_ticker.return_value = ('TEST.NSE', 'details...')

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0 # Simulate failed update

        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.remove_from_priority('TEST.NSE')
        
        self.assertEqual(str(context.exception), "Failed to update priority for ticker TEST.NSE")
        mock_get_ticker.assert_called_once_with('TEST.NSE')
        mock_cursor.execute.assert_called_once_with(
            "UPDATE symbols SET priority = FALSE WHERE query_key = %s", ('TEST.NSE',)
        )
        mock_conn.commit.assert_not_called()

    def test_remove_from_priority_ticker_is_none(self, mock_psycopg_pool):
        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.remove_from_priority(None) # type: ignore
        self.assertEqual(str(context.exception), "Please provide the ticker") # Match expected error

    @patch('libs.datastore.db.Database.get_connection')
    def test_get_historic_data_success_1m(self, mock_get_connection, mock_psycopg_pool):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        sample_db_data = [
            ('TEST.NSE', '2023-01-01 09:15:00', 100.0, 102.0, 99.0, 101.0, 1000),
            ('TEST.NSE', '2023-01-01 09:16:00', 101.0, 103.0, 100.0, 102.0, 1200),
        ]
        mock_cursor.fetchall.return_value = sample_db_data

        ds = DataStore()
        df = ds.get_historic_data('TEST.NSE', freq='1M')

        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM market_data WHERE ticker = %s ORDER BY ts;", ['TEST.NSE']
        )
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 2)
        self.assertEqual(df.index.name, 'ts')
        expected_columns = ["ticker", "open", "high", "low", "close", "volume", "oi"]
        self.assertListEqual(list(df.columns), expected_columns)
        self.assertTrue(df['oi'].isna().all())


    @patch('libs.datastore.db.Database.get_connection')
    def test_get_historic_data_query_with_dates(self, mock_get_connection, mock_psycopg_pool):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [ 
            ('TEST.NSE', '2023-01-01 09:15:00', 100.0, 102.0, 99.0, 101.0, 1000)
        ]


        ds = DataStore()
        ds.get_historic_data('TEST.NSE', freq='1M', start_date='2023-01-01', end_date='2023-01-02')

        expected_query = "SELECT * FROM market_data WHERE ticker = %s AND ts >= %s AND ts <= %s ORDER BY ts;"
        expected_params = ['TEST.NSE', '2023-01-01', '2023-01-02']
        mock_cursor.execute.assert_called_once_with(expected_query, expected_params)

    @patch('libs.datastore.db.Database.get_connection')
    def test_get_historic_data_no_data_found_error(self, mock_get_connection, mock_psycopg_pool):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = None 

        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.get_historic_data('TEST.NSE', freq='1M')
        
        self.assertEqual(str(context.exception), "No data found for ticker TEST.NSE")

    def test_get_historic_data_invalid_frequency(self, mock_psycopg_pool):
        ds = DataStore()
        with self.assertRaises(ValueError) as context:
            ds.get_historic_data('TEST.NSE', freq='3M') 
        
        self.assertEqual(str(context.exception), "Invalid frequency: 3M")

if __name__ == '__main__':
    unittest.main()
