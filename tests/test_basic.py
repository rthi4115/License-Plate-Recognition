def test_main_importable():
    import importlib.util
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    main_path = repo_root / "main.py"
    assert main_path.exists(), "main.py should exist in the repository root"

    spec = importlib.util.spec_from_file_location("main", str(main_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "__file__")
