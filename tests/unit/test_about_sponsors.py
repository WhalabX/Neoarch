"""Sponsor roll in the About → Community tab.

The first sponsor is honoured explicitly (role "First Sponsor"), so the
ordering of `_SPONSORS` is part of the contract, not an implementation
detail. The copy is resolved through the i18n layer, so every bundled
catalog must carry the sponsor strings.
"""

import re

import pytest

from PyQt6.QtWidgets import QApplication, QLabel

from neoarch.backend.services import i18n
from neoarch.frontend.components import about_tab


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_sponsors_list_is_not_empty():
    assert about_tab._SPONSORS, "at least one sponsor must be listed"


def test_first_sponsor_is_ferreol():
    first = about_tab._SPONSORS[0]
    assert first["name"] == "Ferreol"
    assert first["handle"] == "ferreol"
    assert first["url"] == "https://github.com/ferreol"


def test_every_sponsor_has_the_fields_the_card_needs():
    for sponsor in about_tab._SPONSORS:
        assert sponsor["name"].strip()
        assert sponsor["handle"].strip()
        assert re.match(r"^https://github\.com/[\w-]+$", sponsor["url"])
        assert sponsor["copy"]


def test_sponsor_copy_marks_the_first_sponsor():
    first = about_tab._SPONSORS[0]
    copy = about_tab._sponsor_copy(first["copy"])
    assert copy["role"] == "First Sponsor"
    assert copy["note"].strip()
    assert "NeoArch" in copy["note"]


def test_unknown_sponsor_key_falls_back_to_plain_sponsor():
    copy = about_tab._sponsor_copy("nobody")
    assert copy["role"] == "Sponsor"
    assert copy["note"] == ""


@pytest.mark.parametrize("lang", sorted(i18n.available_languages()))
def test_bundled_catalogs_translate_the_sponsor_strings(lang):
    cat = i18n.load_catalog(lang)
    assert cat.get("Sponsors")
    assert cat.get("First Sponsor")
    assert cat.get("Sponsor")
    note = [k for k in cat if k.startswith("His early backing")]
    assert note, f"{lang} catalog is missing the sponsor note"


def test_community_tab_renders_the_sponsor_row(qapp):
    tab = about_tab._CommunityTab()
    labels = [lbl.text() for lbl in tab.findChildren(QLabel)]
    first = about_tab._SPONSORS[0]
    assert "Sponsors" in labels
    assert first["name"] in labels
    assert f"@{first['handle']}" in labels
    assert "First Sponsor" in labels
    assert any(text.startswith("His early backing") for text in labels)
