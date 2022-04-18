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

import shutil
from typing import Optional, Tuple
from pathlib import Path
import subprocess
import json
import sys

class Songid():
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

    def run_songrec_on_file(self, dir: str, filename: str) -> Optional[Tuple[str,str]]:
        """
        Run songrec on an individual mp3 file.

        :param dir: directory where file is located
        :param filename: filename to check

        :returns: tuple of artist, songname, or None if no match found
        """
        filepath = Path(dir, filename)
        songrec_args = "audio-file-to-recognized-song"
        if not filepath.exists():
            raise FileNotFoundError(f"{filepath} not found")
        songrec_result = subprocess.run(
            ["songrec", songrec_args, str(filepath)], capture_output=True, check=True)
        songrec_json = json.loads(songrec_result.stdout)

        try:
            songtitle = songrec_json["track"]["title"]
            artist = songrec_json["track"]["subtitle"]
        except:
            return

        return(artist, songtitle)


if __name__=="__main__":
    songid = Songid()
    results = songid.run_songrec_on_file(sys.argv[1], sys.argv[2])
    print(results)
