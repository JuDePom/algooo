P.main();

var notDefined = [
	"$a",
	"$b",
	"$c",
	"$m",
	"$f",
	"$x",
	"$y",
	"$z",
	"$M",
	"P.$a",
	"P.$b",
	"P.$c",
	"P.$m",
	"$P.x",
	"$P.x",
	"$P.y",
	"$P.z"
];

var defined = [
	"P",
	"P.$f",
	"P.main",
	"P.$M",
	"P.$z"
];

for (var i = 0; i < notDefined.length; i++) {
	try {
		x = eval(notDefined[i]);
		if (typeof x === 'undefined')
			continue;
		throw new Error(notDefined[i] + " should *NOT* have been defined!");
	} catch (e) {
		if (!(e instanceof ReferenceError)) {
			throw e;
		}
	}
}

for (var i = 0; i < defined.length; i++) {
	x = eval(defined[i]);
	if (typeof x === 'undefined')
		throw new Error(defined[i] + " *SHOULD* have been defined!");
}

LDA.print("auxiliary JS test passed!");

