/*
 * Sequential, plain DOM implementation of the non-portable parts of the LDA
 * standard library.
 */

LDA.prompt = function(message) {
	return window.prompt(message);
};

LDA.print = function(message) {
	window.alert(message);
}

