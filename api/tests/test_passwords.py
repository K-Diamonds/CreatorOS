from app.core.passwords import hash_password, verify_password


def test_hash_and_verify_password_roundtrip() -> None:
    hashed = hash_password("demo1234")
    assert hashed.startswith("$2")
    assert verify_password("demo1234", hashed)
    assert not verify_password("wrong-password", hashed)


def test_verify_password_rejects_empty_hash() -> None:
    assert not verify_password("demo1234", "")
