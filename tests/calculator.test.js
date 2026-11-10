const { test } = require('node:test');
const assert = require('node:assert/strict');
const { moneyToCents, calculateSplit } = require('../assets/app.js');

test('rent input preserves cents and rejects missing or malformed amounts', () => {
  assert.equal(moneyToCents('2400.01'), 240001);
  assert.equal(moneyToCents('.09'), 9);
  assert.equal(moneyToCents('0.29'), 29);
  for (const invalid of ['', '-1', '1.001', '1e5', 'NaN', 'Infinity', '10000001']) {
    assert.throws(() => moneyToCents(invalid));
  }
});

test('$2,400 rent split by three roommates is $800 each', () => {
  assert.deepEqual(calculateSplit({ rent: 240000, people: 3 }), [80000, 80000, 80000]);
});

test('rounding cents are assigned without changing the total rent', () => {
  assert.deepEqual(calculateSplit({ rent: 100000, people: 3 }), [33334, 33333, 33333]);
  assert.deepEqual(calculateSplit({ rent: 100001, people: 3 }), [33334, 33334, 33333]);
});

test('zero and one-cent rent do not create money', () => {
  assert.deepEqual(calculateSplit({ rent: 0, people: 3 }), [0, 0, 0]);
  assert.deepEqual(calculateSplit({ rent: 1, people: 3 }), [1, 0, 0]);
});

test('invalid rent and roommate counts are rejected', () => {
  for (const change of [{ people: 0 }, { people: 9 }, { people: 2.5 }, { people: NaN }, { rent: -1 }, { rent: 1.1 }, { rent: NaN }, { rent: Infinity }, { rent: 1000000001 }]) {
    assert.throws(() => calculateSplit({ rent: 240000, people: 3, ...change }));
  }
});

test('all supported household sizes reconcile even at large amounts', () => {
  for (let people = 2; people <= 8; people++) {
    for (const rent of [1, 99, 100000, 279999, 1000000000]) {
      const shares = calculateSplit({ rent, people });
      assert.equal(shares.reduce((a, b) => a + b, 0), rent);
      assert.ok(shares.every(share => Number.isInteger(share) && share >= 0));
      assert.ok(Math.max(...shares) - Math.min(...shares) <= 1);
    }
  }
});
