from unittest.mock import Mock

import pytest

import main


def test_default_main(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py"])

    mock_init_db = Mock()
    mock_get_jobs = Mock()
    mock_source = Mock()

    mock_get_jobs.return_value = []

    monkeypatch.setattr(main, "init_db", mock_init_db)
    monkeypatch.setattr(main, "get_jobs", mock_get_jobs)
    monkeypatch.setattr(main, "HimalayasSource", mock_source)

    main.main()
    captured = capsys.readouterr()

    mock_init_db.assert_called_once()
    mock_get_jobs.assert_called_once_with(50, "jobs.db")
    mock_source.assert_not_called()

    assert "No jobs found." in captured.out


def test_fetch_main(monkeypatch, caplog):
    monkeypatch.setattr("sys.argv", ["main.py", "--fetch"])

    mock_settings = Mock()
    mock_settings_from_env = Mock(return_value=mock_settings)
    mock_init_db = Mock()
    mock_source = Mock()
    mock_save_jobs = Mock()

    mock_settings.himalayas_rss_url = "https://test.example/rss"
    mock_settings.database_path = "jobs.db"
    mock_settings.fetch_timeout = 10
    mock_settings.log_level = "INFO"
    mock_source_instance = mock_source.return_value
    mock_source_instance.fetch.return_value = []
    mock_save_jobs.return_value = 0

    monkeypatch.setattr(main.Settings, "from_env", mock_settings_from_env)
    monkeypatch.setattr(main, "init_db", mock_init_db)
    monkeypatch.setattr(main, "HimalayasSource", mock_source)
    monkeypatch.setattr(main, "save_jobs", mock_save_jobs)

    main.main()

    mock_init_db.assert_called_once()
    mock_source.assert_called_once_with("https://test.example/rss", 10)
    mock_save_jobs.assert_called_once_with([], "jobs.db")
    mock_source_instance.fetch.assert_called_once()

    assert "Fetched 0 jobs" in caplog.text
    assert "Inserted 0 new jobs" in caplog.text


def test_search_main(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["main.py", "--search", "python"])

    mock_init_db = Mock()
    mock_search_jobs = Mock()
    mock_source = Mock()

    mock_search_jobs.return_value = []

    monkeypatch.setattr(main, "init_db", mock_init_db)
    monkeypatch.setattr(main, "search_jobs", mock_search_jobs)
    monkeypatch.setattr(main, "HimalayasSource", mock_source)

    main.main()
    captured = capsys.readouterr()

    mock_init_db.assert_called_once()
    mock_search_jobs.assert_called_once_with("python", 50, "jobs.db")
    mock_source.assert_not_called()

    assert "Jobs matching 'python':" in captured.out
    assert "No jobs found." in captured.out


def test_search_fetch_main(monkeypatch):
    monkeypatch.setattr("sys.argv", ["main.py", "--fetch", "--search", "python"])

    with pytest.raises(SystemExit):
        main.main()
