from pathlib import Path

from reel_studio.core.audio import extract_args


def test_extract_args_usa_lista_sem_shell():
    args = extract_args("ffmpeg", Path("in.mp4"), Path("out.wav"))
    assert isinstance(args, list)
    assert "-ac" in args and "1" in args
    assert "-ar" in args and "16000" in args
    assert str(Path("in.mp4")) in args
    assert all(";" not in a and "&&" not in a for a in args)
