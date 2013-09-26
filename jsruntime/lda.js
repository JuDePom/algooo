/**
 * LDA runtime library
 */

LDA = {
	pedantic: true
};

LDA.RuntimeError = function(message) {
	this.name = "LDARuntimeError";
	this.message = message;
};

/**
 * Construct an array and its sub-arrays recursively.
 *
 * - dimensions: array of integer ranges. An integer range is represented
 *   by an array of two integers. Range bounds are inclusive.
 * - filler: function that generates a value to fill the array with. If omitted, the
 *   array will be filled with `null`.
 * - n: recursion level, i.e. current position within the `dimensions` array.
 *   If null, `n` is set to 0.
 *
 * Runtime check: ordering of range bounds (low bound must be <= high bound).
 */
LDA.Array = function(dimensions, filler, n) {
	if (n === undefined) {
		n = 0;
	}

	this.low = dimensions[n][0];
	this.high = dimensions[n][1];

	// Range bounds must be ordered.
	if (LDA.pedantic && this.low > this.high) {
		throw new LDA.RuntimeError("array dimension: bad range (low > high)");
	}

	// Initialize sub-arrays recursively until we've reached the innermost
	// dimension.
	if (n < dimensions.length - 1) {
		for (var i = this.low; i <= this.high; i++) {
			this[i] = new LDA.Array(dimensions, filler, n+1);
		}
	} else if (filler === undefined) {
		for (var i = this.low; i <= this.high; i++) {
			this[i] = null;
		}
	} else {
		for (var i = this.low; i <= this.high; i++) {
			this[i] = filler();
		}
	}
};

/**
 * Recursive implementation of the array subscript operator in an expression.
 *
 * - indices: array of integer indices.
 * - n: recursion level, i.e. current position within the `indices` array. If
 *   omitted, `n` is set to 0.
 *
 * Runtime checks:
 * - ensure the given indices lie within the bounds of the dimensions;
 * - ensure the value is not null.
 *
 * Note: This function does not check whether the number of indices
 * matches the number of dimensions, because this is done at compile time.
 */
LDA.Array.prototype.get = function(indices, n) {
	if (n === undefined) {
		n = 0;
	}

	var i = indices[n];

	if (LDA.pedantic && (i < this.low || i > this.high)) {
		throw new LDA.RuntimeError("index out of bounds");
	}

	if (n < indices.length - 1) {
		return this[i].get(indices, n+1);
	} else {
		var value = this[i];
		if (LDA.pedantic && value === null) {
			throw new LDA.RuntimeError("accessing null array element");
		}
		return value;
	}
};

/**
 * Recursive implementation of the array subscript operator in the lefthand
 * side of an assignment.
 *
 * Runtime check: ensure the given indices lie within the bounds of the
 * dimensions.
 */
LDA.Array.prototype.set = function(indices, value, n) {
	if (n === undefined) {
		n = 0;
	}

	var i = indices[n];

	if (LDA.pedantic && (i < this.low || i > this.high)) {
		throw new LDA.RuntimeError("index out of bounds");
	}

	if (n < indices.length - 1) {
		this[i].set(indices, value, n+1);
	} else {
		this[i] = value;
	}
};

