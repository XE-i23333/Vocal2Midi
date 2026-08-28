import math
import xml.etree.ElementTree as ET

from inference.API.vsqx_api import save_vsqx
from inference.io.note_io import NoteInfo


def test_vsqx_export_writes_notes_and_skips_invalid(tmp_path):
    path = tmp_path / "notes.vsqx"
    save_vsqx([NoteInfo(0, 0.5, 60, "la"), NoteInfo(0.6, 0.4, 60, "bad"), NoteInfo(1, 2, math.nan, "bad")], path)
    root = ET.parse(path).getroot()
    ns = {"v": "http://www.yamaha.co.jp/vocaloid/schema/vsq3/"}
    notes = root.findall(".//v:note", ns)
    assert len(notes) == 1
    assert notes[0].findtext("v:noteNum", namespaces=ns) == "60"
    assert notes[0].findtext("v:lyric", namespaces=ns) == "la"
    assert root.find(".//v:mixer/v:masterTrack", ns) is not None
