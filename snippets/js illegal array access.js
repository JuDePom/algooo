LDA.print("loaded auxiliary JS!");

function mustThrow(f) {
	try {
		f();
		throw new Error("an LDA.RuntimeError should have been raised here!");
	} catch (e) {
		if (!(e instanceof LDA.RuntimeError)) {
			throw e;
		}
	}
}

mustThrow(P.$staticfail);
mustThrow(P.$dynamicfail);

LDA.print("auxiliary JS test passed!");

