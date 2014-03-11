from unipath import Path


TESTDATA_PATH = Path(__file__).parent.child('testdata')

RAW_NOAGENDA_MEDIA_PATH = TESTDATA_PATH.child('raw').child(
    'NA-472-2012-12-23-Final-excerpt.mp3')

CONVERTED_NOAGENDA_MEDIA_PATH = TESTDATA_PATH.child('converted').child(
    'NA-472-2012-12-23-Final-excerpt-converted.mp3')
