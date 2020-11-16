from typer.testing import CliRunner
import shutil
import os

from nkit import __version__
from nkit.main import app
from nkit.storage.local import SessionLocal, Note as DbNote
from nkit.security.security import generate_rsa_key, encrypt, decrypt, encrypt_large, decrypt_large
from nkit.constants import APP_DIR

runner = CliRunner()


def test_version():
    assert __version__ == '0.1.2'

def teardown_module():
    # it's the test dir so we can remove it
    shutil.rmtree(APP_DIR)



def setup_function():
    db = SessionLocal()
    db.query(DbNote).delete()
    db.commit()
    db.close()

def test_environment():
    assert os.environ["TESTING"] == "1"

def test_save():
    output = runner.invoke(app, ["note", "__test some note"])
    assert output.exit_code == 0
    assert b"success" in output.stdout_bytes.lower()

    output = runner.invoke(app, ["notes", "show", "--limit", "1"])
    assert output.exit_code == 0
    assert b"__test some note" in output.stdout_bytes.lower()

    output = runner.invoke(app, ["notes", "show","--id", "--limit", "1"])
    note_id = output.stdout_bytes.split(b" ")[0].decode("utf-8")
    output = runner.invoke(app, ["notes", "remove", str(note_id)])
    assert output.exit_code == 0

    output = runner.invoke(app, ["notes", "show", "--id", "--limit", "1"])
    assert output.exit_code == 0
    assert note_id.encode("utf-8") != output.stdout_bytes.lower().split(b" ")[0]


def test_multiple_save():
    for _ in range(5):
        test_save()

def test_key_gen():
    # checks if there's any practically infeasible randomness in key generation
    # TODO: optimize generation in security.py

    prev_keys = [] # loose check to check if two phrases have the same private key
    for key_phrase in ["Hello", "bye", "something on eth ", "sdfu#@4jodsfjo324"]:
        # small key size makes the generation faster 
        # ideal for testing
        key1 = generate_rsa_key(key_phrase.encode("utf-8"), 512)
        key2 = generate_rsa_key(key_phrase.encode("utf-8"), 512)
        private_key1 = key1.export_key("PEM")
        private_key2 = key2.export_key("PEM")
        assert private_key1 == private_key2
        assert private_key1 not in prev_keys
        prev_keys.append(private_key1)

        # TODO: why the length is not exact? (That's why we're checking bytes not bits)
        assert key1._n.size_in_bytes() == 512//8 # type: ignore  pycryptodome: _n is set dynamically

def test_encryption_decryption():
    key_phrase = b"Hyy3"
    data = b"Some secure piece"
    key = generate_rsa_key(key_phrase, 512)
    encrypted = encrypt(key.publickey(), data)
    decrypted = decrypt(key, encrypted)
    assert data == decrypted

def test_encryption_decryption_large():
    key_phrase = b"Hyy3"
    data = b"Some secure piece"*10000
    key = generate_rsa_key(key_phrase, 512)
    encrypted = encrypt_large(key.publickey(), data)
    decrypted = decrypt_large(key, encrypted)
    assert data == decrypted

