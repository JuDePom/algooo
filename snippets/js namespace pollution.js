LDA.print("loaded auxiliary JS!");

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
	var nd = notDefined[i];
	var undef;
	try {
		if (0 == nd.indexOf("P.")) {
			// avoid strict warning by not using eval with P
			undef = P[nd.slice("P.".length)];
		} else {
			undef = eval(nd);
		}
		if (typeof undef === 'undefined')
			continue;
		throw new Error(nd + " should *NOT* have been defined!");
	} catch (e) {
		if (!(e instanceof ReferenceError)) {
			throw e;
		}
	}
}

for (var i = 0; i < defined.length; i++) {
	if (typeof eval(defined[i]) === 'undefined')
		throw new Error(defined[i] + " *SHOULD* have been defined!");
}

LDA.print("auxiliary JS test passed!");

