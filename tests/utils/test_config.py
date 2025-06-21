import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
import yaml

from mir_commander import errors
from mir_commander.utils.config import Config

BAD_KEYS = [1, None, ["a"], ("a",), "", ".", "b.", ".b", "b..c"]
DATA = {"a": 1, "b": {"c": 2, "e": {"f": 3}}, "none": None}


def mock_load(self):
    self._data = deepcopy(DATA)


@pytest.fixture
def config(monkeypatch) -> Config:
    monkeypatch.setattr(Config, "_load", mock_load)
    monkeypatch.setattr(Config, "dump", lambda x: None)

    return Config(Mock())


@pytest.fixture
def config_with_defaults(monkeypatch) -> Config:
    monkeypatch.setattr(Config, "_load", lambda x: {})
    monkeypatch.setattr(Config, "dump", lambda x: None)

    config = Config(Mock())
    config._data = {}

    defaults = Config(Mock())
    defaults._data = deepcopy(DATA)
    config.set_defaults(defaults)

    return config


def test__load():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write(yaml.dump(DATA, Dumper=yaml.CDumper, allow_unicode=True))
        fp.seek(0)
        config = Config(Path(fp.name))
        assert config._data == DATA


def test__load_empty_file():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        config = Config(Path(fp.name))
        assert config._data == {}


def test__load_bad_file():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write("bad: yaml: format")
        fp.seek(0)
        config = Config(Path(fp.name))
        assert config._data == {}


def test__load_directory():
    with tempfile.TemporaryDirectory() as tmpdirname:
        Config(Path(tmpdirname))


def test_dump(monkeypatch):
    monkeypatch.setattr(Config, "_load", mock_load)

    with tempfile.NamedTemporaryFile(mode="a+") as fp:
        Config(Path(fp.name)).dump()
        fp.seek(0)
        assert DATA == yaml.load(fp.read(), Loader=yaml.CLoader)


def test_dump_nested(monkeypatch):
    monkeypatch.setattr(Config, "_load", mock_load)

    with tempfile.NamedTemporaryFile(mode="a+") as fp:
        config = Config(Path(fp.name)).nested("b")
        config.dump()
        fp.seek(0)
        assert DATA == yaml.load(fp.read(), Loader=yaml.CLoader)


def test_dump_mkdir(monkeypatch):
    monkeypatch.setattr(Config, "_load", mock_load)

    with tempfile.TemporaryDirectory() as tmpdirname:
        fname = f"{tmpdirname}/test.yaml"
        Config(Path(fname)).dump()
        with open(fname, "r") as fp:
            assert DATA == yaml.load(fp.read(), Loader=yaml.CLoader)


@pytest.mark.parametrize("key,expected", [("a", ["a"]), ("a.b", ["a", "b"]), ("a.b.c", ["a", "b", "c"])])
def test__key(key: str, expected: str, config: Config):
    assert config._key(key) == expected


@pytest.mark.parametrize("key", BAD_KEYS)
def test__key_bad(key: Any, config: Config):
    with pytest.raises(errors.ConfigError):
        config._key(key)


@pytest.mark.parametrize("key", ["a", "b", "b.c", "none"])
def test_contains(key: str, config: Config):
    assert config.contains(key) is True


@pytest.mark.parametrize("key", ["a", "b", "b.c", "none"])
def test_with_defaults_contains(key: str, config_with_defaults: Config):
    assert config_with_defaults.contains(key) is True


@pytest.mark.parametrize("key", ["c", "e.f"])
def test_contains_nested(key: str, config: Config):
    assert config.nested("b").contains(key) is True


@pytest.mark.parametrize("key", ["b.c._unknown", "_unknown", "_unknown._unknown"])
def test_contains_non_existent_key(key: str, config: Config):
    assert config.contains(key) is False


@pytest.mark.parametrize("key", BAD_KEYS)
def test_contains_bad_key(key: Any, config: Config):
    with pytest.raises(errors.ConfigError):
        config.contains(key)


def test_set_defaults(config: Config):
    config.set_defaults(Mock())


def test_set_defaults_nested(config: Config):
    nested_b = config.nested("b")
    with pytest.raises(errors.ConfigError):
        nested_b.set_defaults(Mock())


def test_get(config: Config):
    assert config.get("a") == config["a"] == config._data["a"]
    assert config.get("b.c") == config["b.c"] == config._data["b"]["c"]


def test_get_default(config: Config):
    default_value = Mock()
    assert config.get("undefined_key", default_value) == default_value


def test_nested_get(config: Config):
    nested_b = config.nested("b")
    assert nested_b["c"] == nested_b.get("c") == config["b.c"] == config.get("b.c")


def test_nested_nested_get(config: Config):
    nested_e = config.nested("b").nested("e")
    assert nested_e.get("f") == nested_e["f"] == config.get("b.e.f") == config["b.e.f"] == config._data["b"]["e"]["f"]


def test_with_defaults_get(config_with_defaults: Config):
    config = config_with_defaults
    assert config.get("a") == config["a"]
    assert config.get("b.c") == config["b.c"]


def test_with_defaults_get_default(config_with_defaults: Config):
    default_value = Mock()
    assert config_with_defaults.get("undefined_key", default_value) == default_value


def test_set(config: Config):
    c_value = Mock()
    b_d_value = Mock()
    b_g_h_value = Mock()

    config.set("c", c_value)
    config.set("b.d", b_d_value)
    config.set("b.g.h", b_g_h_value)
    assert c_value == config.get("c") == config._data["c"]
    assert b_d_value == config.get("b.d") == config._data["b"]["d"]
    assert b_g_h_value == config.get("b.g.h") == config._data["b"]["g"]["h"]


def test_set_replace(config: Config):
    b_d_value = Mock()

    config.set("b.d", b_d_value)
    assert b_d_value == config.get("b.d") == config._data["b"]["d"]

    b_d_a_value = Mock()
    config["b.d.a"] = b_d_a_value
    assert b_d_a_value == config.get("b.d.a") == config._data["b"]["d"]["a"] == config["b.d.a"]

    assert config.get("b.d") == config._data["b"]["d"] == {"a": b_d_a_value}


def test_nested_set(config: Config):
    d_value = Mock()

    nested_b = config.nested("b")
    nested_b.set("d", d_value)
    assert d_value == nested_b.get("d") == config.get("b.d") == nested_b["d"] == config["b.d"]


def test_nested_nested_set(config: Config):
    g_value = Mock()

    nested_e = config.nested("b").nested("e")
    nested_e.set("g", g_value)
    assert g_value == nested_e.get("g") == config.get("b.e.g")


def test__repr(config: Config):
    assert repr(config).startswith("Config(")
    assert repr(config.nested("b")).startswith("Config(")
