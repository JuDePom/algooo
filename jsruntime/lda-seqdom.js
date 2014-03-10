/*
 * Sequential, plain DOM implementation of the non-portable parts of the LDA
 * standard library.
 */

LDA.prompt = function(message) {
	var v = window.prompt(message);
	if (null === v) {
		throw new LDA.InterruptedException();
	}
	return v;
};

LDA.print = function(message) {
	if (!window.confirm(message)) {
		throw new LDA.InterruptedException();
	}
};

