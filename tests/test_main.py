from unittest.mock import Mock

import pytest

import main


def test_default_main(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py"])

    mock_init_db = Mock()
    mock_get_jobs = Mock()
    mock_get_sources = Mock()

    mock_get_jobs.return_value = []

    monkeypatch.setattr(main, "init_db", mock_init_db)
    monkeypatch.setattr(main, "get_jobs", mock_get_jobs)
    monkeypatch.setattr(main, "get_sources", mock_get_sources)

    main.main()
    captured = capsys.readouterr()

    mock_init_db.assert_called_once()
    mock_get_jobs.assert_called_once_with(50, "jobs.db")
    mock_get_sources.assert_not_called()

    assert "No jobs found." in captured.out


def test_fetch_main(monkeypatch, caplog):
    monkeypatch.setattr("sys.argv", ["main.py", "--fetch"])

    mock_settings = Mock()
    mock_settings_from_env = Mock(return_value=mock_settings)
    mock_init_db = Mock()
    mock_get_sources = Mock()
    mock_save_jobs = Mock()

    mock_settings.database_path = "jobs.db"
    mock_settings.log_level = "INFO"

    mock_source_1 = Mock()
    mock_source_2 = Mock()

    mock_source_1.fetch.return_value = []
    mock_source_2.fetch.return_value = []

    mock_get_sources.return_value = [mock_source_1, mock_source_2]
    mock_save_jobs.return_value = 0

    monkeypatch.setattr(main.Settings, "from_env", mock_settings_from_env)
    monkeypatch.setattr(main, "init_db", mock_init_db)
    monkeypatch.setattr(main, "get_sources", mock_get_sources)
    monkeypatch.setattr(main, "save_jobs", mock_save_jobs)

    main.main()

    mock_init_db.assert_called_once()
    mock_get_sources.assert_called_once_with(mock_settings)

    mock_source_1.fetch.assert_called_once()
    mock_source_2.fetch.assert_called_once()

    assert mock_save_jobs.call_count == 2
    assert "Fetched 0 jobs" in caplog.text
    assert "Inserted 0 new jobs" in caplog.text


def test_search_main(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "--search", "python"])

    mock_init_db = Mock()
    mock_search_jobs = Mock()
    mock_get_sources = Mock()

    mock_search_jobs.return_value = []

    monkeypatch.setattr(main, "init_db", mock_init_db)
    monkeypatch.setattr(main, "search_jobs", mock_search_jobs)
    monkeypatch.setattr(main, "get_sources", mock_get_sources)

    main.main()
    captured = capsys.readouterr()

    mock_init_db.assert_called_once()
    mock_search_jobs.assert_called_once_with("python", 50, "jobs.db")
    mock_get_sources.assert_not_called()

    assert "Jobs matching 'python':" in captured.out
    assert "No jobs found." in captured.out


def test_search_fetch_main(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "--fetch", "--search", "python"])

    with pytest.raises(SystemExit):
        main.main()
