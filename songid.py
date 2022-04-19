#!/usr/bin/python3
"""
call songrec on mp3s

1. check if songrec is available
2. take cmd line input (directory)
3. check if cmd line input is valid (directory exists)
4. for each mp3 file in directory:
   a. run songrec on file
   b. process json returned by songrec
   c. if json includes artist/title, rename mp3 with them
   d. find matching cdg file, rename to match
   e. update mp3 id3 info to include artist/title.

"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


class Songid:
    """
    take an mp3 file and call songrec on it
    """

    def check_for_songrec(self) -> bool:
        """
        Check if songrec is available.

        :returns: True if songrec found

        :raises FileNotFoundError: if songrec can't be located.
        """
        if not shutil.which("songrec"):
            raise FileNotFoundError("songrec not found in path")

        return True

    def run_songrec_on_file(self, directory: str, filename: str) -> Optional[Tuple[str, str]]:
        """
        Run songrec on an individual mp3 file.

        :param directory: directory where file is located
        :param filename: filename to check

        :returns: tuple of artist, songname, or None if no match found
        """
        filepath = Path(directory, filename)
        songrec_args = "audio-file-to-recognized-song"
        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} not found")
        songrec_result = subprocess.run(["songrec", songrec_args, str(filepath)], capture_output=True, check=True)
        songrec_json = json.loads(songrec_result.stdout)

        try:
            songtitle = songrec_json["track"]["title"]
            artist = songrec_json["track"]["subtitle"]
        except Exception:
            return

        return (artist, songtitle)

    def rename_files(self, directory: str, filename: str, newname: str, rename_cdg: bool = True) -> bool:
        """
        Rename a file.

        The idea is that a directory contains mp3 files and cdg files
        with the same basenames.  If rename_cdg is True, attempt to
        rename the matching cdg file as well.

        :param directory: directory to look in
        :param filename: original file to rename
        :param newname: new name for file
        :param rename_cdg: look for and rename cdg file as well.
        """

        filepath = Path(directory, filename)
        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} not found")
        try:
            filepath.replace(Path(directory, f"{newname}.mp3"))
        except Exception:
            raise

        if rename_cdg:
            cdgpath = Path(directory, f"{filepath.stem}.CDG")
            try:
                cdgpath.replace(Path(directory, f"{newname}.cdg"))
            except Exception:
                raise

        return True


if __name__ == "__main__":
    songid = Songid()
    directory = sys.argv[1]
    filename = sys.argv[2]

    id_results = songid.run_songrec_on_file(directory, filename)
    if id_results:
        newname = f"{id_results[0]} - {id_results[1]}"
        print(f"renaming {filename} to {newname}")
        songid.rename_files(directory, filename, newname, rename_cdg=True)
    else:
        print(f"failed to id {filename}, skipping")
