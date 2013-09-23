/*********************************************************************
 * TEST ARRAYS
 *********************************************************************/

module("Misc. arrays");

test("unordered bounds must fail", function() {
	throws(function() { new LDA.Array([[5, 2]]); }, LDA.RuntimeError);
});


(function() {
	var array;

	module("1D array [[-2, 3]]", {
		setup: function() {
			array = new LDA.Array([[-2, 3]]);
		}
	});

	test("bounds set by constructor", function() {
		strictEqual(array.low, -2);
		strictEqual(array.high, 3);
	});

	test("set value within bounds", function() {
		for (var i = -2; i <= 3; i++) {
			array.set([i], 1234);
			strictEqual(array[i], 1234);
		}
	});

	test("set then get value within bounds", function() {
		for (var i = -2; i <= 3; i++) {
			array.set([i], 1234);
			strictEqual(array.get([i]), 1234);
		}
	});

	test("set value out of bounds", function() {
		throws(function() { array.set([-100], 1234); }, LDA.RuntimeError);
	});

	test("get value out of bounds", function() {
		throws(function() { array.get([-100]); }, LDA.RuntimeError);
	});

	test("get unitialized value within bounds", function() {
		for (var i = -2; i <= 3; i++) {
			throws(function() { array.get([i]); }, LDA.RuntimeError);
		}
	});
})();


(function() {
	var array;

	module("2D array [[0, 2], [4, 6]]", {
		setup: function() {
			array = new LDA.Array([[0, 2], [4, 6]]);
		}
	});

	test("bounds set by constructor", function() {
		strictEqual(array.low, 0);
		strictEqual(array.high, 2);
	});

	test("constructor initializes empty sub-arrays with correct bounds", function() {
		for (var i = 0; i <= 2; i++) {
			ok(array[i] !== undefined, "sub-array #" + i + " must be defined");
			strictEqual(array[i].low, 4, "low bound of sub-array #" + i);
			strictEqual(array[i].high, 6, "high bound of sub-array #" + i);
			for (var j = 4; j <= 6; j++) {
				strictEqual(array[i][j], undefined, "undefined element in innermost array");
			}
		}
	});

	test("set value within bounds", function() {
		for (var i = 0; i <= 2; i++) {
			for (var j = 4; j <= 6; j++) {
				array.set([i,j], 1234);
				strictEqual(array[i][j], 1234);
			}
		}
	});

	test("set then get value within bounds", function() {
		for (var i = 0; i <= 2; i++) {
			for (var j = 4; j <= 6; j++) {
				array.set([i,j], 1234);
				strictEqual(array.get([i,j]), 1234);
			}
		}
	});

	test("set value out of bounds of innermost array", function() {
		for (var i = 0; i <= 2; i++) {
			throws(function() { array.set([i,-100], 1234); }, LDA.RuntimeError);
		}
	});

	test("set value out of bounds of first array", function() {
		for (var j = 4; j <= 6; j++) {
			throws(function() { array.set([-100,j], 1234); }, LDA.RuntimeError);
		}
	});

	test("get value out of bounds of innermost array", function() {
		for (var i = 0; i <= 2; i++) {
			throws(function() { array.get([i,-100]); }, LDA.RuntimeError);
		}
	});

	test("set value out of bounds of first array", function() {
		for (var j = 4; j <= 6; j++) {
			throws(function() { array.get([-100,j]); }, LDA.RuntimeError);
		}
	});

})();

