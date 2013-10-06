"""
Run JavaScript code easily.

`js` is the default JS interpreter command, but a custom path can be set in the
JSSHELL environment variable.

Requires a recent version of the SpiderMonkey shell (JavaScript-C27.0a1 was
used during development).
https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/
"""


import subprocess
import os

try:
	JSSHELL = os.environ['JSSHELL']
except KeyError:
	JSSHELL = 'js'

print("SpiderMonkey shell: {} "
		"(you can override this path with the JSSHELL environment variable)"
		.format(JSSHELL))


def run(jscode, inputstr='', shutup=False, extracode="P.main();"):
	code = ("load('jsruntime/lda.js');\n"
			"load('jsruntime/lda-spidermonkey.js');\n"
			"{}\n"
			"{}\n").format(jscode, extracode)
	process = subprocess.Popen([JSSHELL, "-w", "-s", "-e", code],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=shutup and subprocess.DEVNULL or None)
	stdout, stderr = process.communicate(inputstr.strip().encode('utf-8'))
	if 0 != process.returncode:
		raise subprocess.CalledProcessError(process.returncode, 'jsshell.run()')
	return stdout.decode("utf-8").replace("\r", "").strip()

