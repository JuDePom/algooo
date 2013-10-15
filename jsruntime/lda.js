/**
 * LDA runtime library
 */

var LDA = {
	pedantic: true,
	browser: typeof(window) === undefined,
	booleanLiterals: {
		'vrai': true,
		'true': true,
		'oui': true,
		'yes': true,
		'faux': false,
		'false': false,
		'non': false,
		'no': false
	},
};

///////////////////////////////////////////////////////////////////////
//
// EXCEPTIONS
//
///////////////////////////////////////////////////////////////////////

/**
 * Thrown when an illegal operation occurs (e.g. accessing an array element
 * out of bounds).
 */
LDA.RuntimeError = function(message) {
	this.name = "LDARuntimeError";
	this.message = message;
};


///////////////////////////////////////////////////////////////////////
//
// ARGUMENT PASSING HELPERS
//
///////////////////////////////////////////////////////////////////////

/**
 * Make a fake pointer. Useful when passing `inout` parameters.
 *
 * The pointed-to value can be read and written through the `v` property of
 * the returned pointer object.
 *
 * - getter: a function that returns the pointed-to value
 * - setter: a function that assigns its sole argument to the pointed-to value
 */
LDA.ptr = function(getter, setter) {
	return Object.defineProperty({}, "v", {get: getter, set: setter});
};

/**
 * Clone an object. This is used to fake pass-by-copy.
 *
 * A clone of an object is an empty object with a prototype reference to the
 * original. As such, you can access the current properties of the original
 * through the clone. If you set a clone's property, it will override the
 * original's property, and not affect the original. You can use the delete
 * operator on the clone's overridden property to return to the earlier lookup
 * behavior.
 *
 * (From owl_util.js; see http://oranlooney.com/functional-javascript)
 */
LDA.clone = (function() {
	function Clone() {}
	return function(obj) {
		Clone.prototype = obj;
		return new Clone();
	};
}());


///////////////////////////////////////////////////////////////////////
//
// ARRAY
//
///////////////////////////////////////////////////////////////////////

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


///////////////////////////////////////////////////////////////////////
//
// TYPED INPUT FUNCTIONS
//
// The platform-specific implementations are only required to provide
// LDA.prompt, which must return a string. The functions below use
// LDA.prompt to prompt for specific types.
//
///////////////////////////////////////////////////////////////////////

(function() {
	function genericRead(promptMessage, convert) {
		return function() {
			var v = convert(LDA.prompt(promptMessage));
			while (typeof v === 'undefined' || (typeof v === 'number' && isNaN(v))) {
				LDA.print("Mauvais type ! Recommencez, SVP.");
				v = convert(LDA.prompt(promptMessage));
			}
			return v;
		};
	};

	LDA.readStr  = function(){return LDA.prompt('cha\u00EEne> ');};
	LDA.readInt  = genericRead('entier> ', parseInt);
	LDA.readReal = genericRead('r\u00E9el> ', parseFloat);
	LDA.readBool = genericRead('bool\u00E9en> ', function(line) {
		return LDA.booleanLiterals[line.toLowerCase()];
	});
	LDA.readChar = genericRead('caract\u00E8re> ', function(line) {
		return line.length === 1? line: undefined;
	});
})();

