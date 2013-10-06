/*
 * SpiderMonkey implementation of the non-portable parts of the LDA standard library.
 */

/*
if ('ç'.length !== 1) {
	print("Poor Unicode support! The unit tests require SpiderMonkey 27 or later!");
}
*/

LDA.prompt = function(message) {
	putstr(message);
	return readline();
};

LDA.print = print;

