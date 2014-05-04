IMME Spectrum Analyzer Tap
by Travis Goodspeed
for use with Mike Ossmann's IMME Spectrum Analyzer,
which is included as specan.hex.

For more information, see these articles:
http://ossmann.blogspot.com/2010/03/16-pocket-spectrum-analyzer.html
http://travisgoodspeed.blogspot.com/2010/03/im-me-goodfet-wiring-tutorial.html

Files:
  README.txt
  specan.hex       -- Ossmann's spectrum analyzer firmware, unmodified.
  specantap.py     -- Tap data as time, freq, rssi.
  specantap_hex.py -- Early example, dumps table as hex.



Example:

  goodfet.cc erase
  goodfet.cc flash specan.hex
  ./specantap.py | tee spectrum.txt


Result:

time freq rssi
002 901.803 064
002 902.003 065
002 902.203 061
002 902.403 063
002 902.603 062
002 902.803 066
002 903.003 064
002 903.203 063
002 903.403 067
...

