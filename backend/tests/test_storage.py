import os
import pytest
from app.services.storage import LocalStorageBackend, storage_backend


def test_storage_save_read_exists_and_delete(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    test_content = b"%PDF-1.4 sample resume binary content for unit test"
    filename = "test_resume_001.pdf"

    # 1. Initially does not exist
    assert backend.exists("resumes", filename) is False

    # 2. Save
    saved_path = backend.save("resumes", filename, test_content)
    assert os.path.exists(saved_path)
    assert backend.exists("resumes", filename) is True

    # 3. Read
    content = backend.read("resumes", filename)
    assert content == test_content

    # 4. Get path
    resolved_path = backend.get_path("resumes", filename)
    assert resolved_path == saved_path

    # 5. Delete
    deleted = backend.delete("resumes", filename)
    assert deleted is True
    assert backend.exists("resumes", filename) is False

    # 6. Second delete returns False
    deleted_again = backend.delete("resumes", filename)
    assert deleted_again is False


def test_storage_read_nonexistent_raises_filenotfound(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        backend.read("resumes", "non_existent_file.pdf")


def test_storage_path_traversal_prevention(tmp_path):
    backend = LocalStorageBackend(base_dir=str(tmp_path))
    traversal_filenames = [
        "../secret.txt",
        "../../etc/passwd",
        "sub/folder/file.pdf",
        "..\\windows\\system32",
        "/absolute/path/file.pdf",
    ]

    for bad_name in traversal_filenames:
        with pytest.raises(ValueError, match="(Path traversal|Invalid filename)"):
            backend.save("resumes", bad_name, b"evil content")

        with pytest.raises(ValueError, match="(Path traversal|Invalid filename)"):
            backend.get_path("resumes", bad_name)


def test_default_storage_singleton():
    assert storage_backend is not None
    assert isinstance(storage_backend, LocalStorageBackend)
