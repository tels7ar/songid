"""
pytests for songid
"""


from songid import Songid

def test_songid():
    songid = Songid()
    assert songid.check_for_songrec() == True
