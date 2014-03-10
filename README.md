![](http://www.algooo.fr/algooo50_black.png "algooo")

Compiler for a programming language designed to introduce French budding
programmers to algorithmics. Meant to be integrated within a web app. 

## Live demo: http://www.algooo.fr

(may take a couple seconds to load at first, I use a very cheap hosting plan)


## Backstory

I attended a CS program at [IUT
Nancy-Charlemagne](http://iut-charlemagne.univ-lorraine.fr), France which uses
an in-house "pseudo-code" programming language to teach the basics of
algorithmics. It's a simplified form of Pascal with French keywords. For the
final year's "big" project, I presented a compiler for this programming
language.

Why bother writing a compiler from scratch when there are compiler compilers
these days? For fun! And to learn how compilers work. It's not meant to be a
super serious project. I learned a ton of stuff working on it -- both about
general computer science and about Python and JavaScript.

## Technical overview

- Compiler written in Python 3

- Compiles "LDA" to JavaScript (LDA stands for *Langage de Description
  d'Algorithmes*, i.e. *algorithm description language*. This was the 'working
  title' during development)

- Meant to be run as a web app: 

	1. enter your code in the browser
	
	2. the compiler does its thing on the server side and responds with
	   compiled JavaScript

	3. your browser can execute the JavaScript
	
- Also works just fine on the command line (read caveats below)

- The programming language is in French, but the source code is in English, and
  the keywords can be easily translated to pretty much any human language (see
  `kw.py`)


## Getting a taste of the language

As mentioned before, it's basically simplified Pascal with French keywords and
a few tweaks.

A couple runnable examples are available at www.algooo.fr (look for the pane
that says 'Exemples' on the left).

You can also have a look around the `snippets` directory, which contains
hundreds of small snippets of the language. The snippets are used as a compiler
torture test within the test suite (`test_snippets.py`). But, each snippet is
self-contained. Many snippets are correct LDA and may be compiled -- but many
other snippets explicitly test the compiler's proper response to syntax or
semantic errors.


## Standalone JavaScript shell (SpiderMonkey)

You will need a standalone JavaScript shell to run all the unit tests and
execute the resulting JS from the command line. During development, **Mozilla
SpiderMonkey** (aka `jsshell`) was used.

For best results, SpiderMonkey **27+**, is recommended. Versions earlier than
27 may work, albeit with poor Unicode support.

Download a binary for your architecture there (scroll down and look for
`jsshell`):
https://ftp.mozilla.org/pub/mozilla.org/firefox/nightly/latest-trunk/ 


## Command line usage

	usage: ldac.py [-h] [--format FORMAT] [--output-file OUTPUT_FILE]
				   [--no-output] [--ignore-case] [--execute] INPUT_FILE

Parameter         | Description
----------------- | -----------------------------------------------------------
`-h`              | Get help
`--format FORMAT` | Output format. Can be `js` (JavaScript, default) or `lda` (re-formatted LDA).
`--no-output`     | Only checks syntactic and semantic correctness, does not output any code.
`--ignore-case`   | Ignore case in identifiers and keywords.
`--execute`       | Attempt to run the program with a JS runtime if no errors are found

