/*
 * Sequential, plain DOM implementation of the non-portable parts of the LDA
 * standard library.
 */

LDA.prompt = function(message) {
	if (null === window.prompt(message)) {
		throw new LDA.InterruptedException();
	}
};

LDA.print = function(message) {
	if (!window.confirm(message)) {
		throw new LDA.InterruptedException();
	}
};

