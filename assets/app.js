/* Equal rent shares in whole cents. No network requests or persistent storage. */
(function () {
  'use strict';

  function moneyToCents(value) {
    const input = String(value).trim();
    if (input === '') throw new Error('Enter the monthly rent.');
    if (!/^(?:\d+(?:\.\d{0,2})?|\.\d{1,2})$/.test(input)) {
      throw new Error('Enter a non-negative amount with no more than two decimal places.');
    }
    const [whole, fraction = ''] = input.split('.');
    const cents = Number(whole || 0) * 100 + Number(fraction.padEnd(2, '0'));
    if (!Number.isSafeInteger(cents) || cents > 1000000000) {
      throw new Error('Enter an amount of 10,000,000 or less.');
    }
    return cents;
  }

  function calculateSplit({ rent, people }) {
    if (!Number.isInteger(people) || people < 2 || people > 8) {
      throw new Error('Choose between 2 and 8 roommates.');
    }
    if (!Number.isSafeInteger(rent) || rent < 0 || rent > 1000000000) {
      throw new Error('Enter a valid rent amount in whole cents.');
    }
    const base = Math.floor(rent / people);
    const extra = rent % people;
    return Array.from({ length: people }, (_, i) => base + (i < extra ? 1 : 0));
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { moneyToCents, calculateSplit };
  if (typeof document === 'undefined') return;

  const form = document.getElementById('rent-form');
  if (form) {
    const rentInput = document.getElementById('rent');
    const peopleInput = document.getElementById('people');
    const results = document.getElementById('calc-results');
    const error = document.getElementById('calc-error');
    const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
    const fmt = cents => formatter.format(cents / 100);

    function markStale() {
      error.hidden = true;
      if (!results.querySelector('.result-stale')) {
        const note = document.createElement('p');
        note.className = 'result-stale';
        note.textContent = 'Press Split rent to update the amount.';
        results.prepend(note);
      }
    }
    form.addEventListener('input', markStale);
    peopleInput.addEventListener('change', markStale);

    form.addEventListener('submit', event => {
      event.preventDefault();
      error.hidden = true;
      try {
        const rent = moneyToCents(rentInput.value);
        const people = Number(peopleInput.value);
        const shares = calculateSplit({ rent, people });
        const base = shares[shares.length - 1];
        const extra = rent % people;
        const [major, minor] = fmt(base).split('.');
        // All interpolated amounts come from validated numbers and fixed USD formatting.
        results.innerHTML = '<div class="result-eyebrow">' + (extra ? 'PER PERSON · ROUNDED' : 'PER PERSON') + '</div><div class="result-amount' + (major.length > 10 ? ' is-long' : '') + '">' + major + '<span>.' + minor + ' <small>/ month</small></span></div><p class="result-detail">' + fmt(rent) + ' ÷ ' + people + ' roommates</p>';
        if (extra) {
          const note = document.createElement('p');
          note.className = 'result-footnote';
          note.textContent = extra + (extra === 1 ? ' roommate pays ' : ' roommates pay ') + fmt(base + 1) + '; ' + (people - extra) + (people - extra === 1 ? ' pays ' : ' pay ') + fmt(base) + ' to cover the last ' + (extra === 1 ? 'cent.' : 'cents.');
          results.append(note);
        }
      } catch (issue) {
        error.textContent = issue.message;
        error.hidden = false;
      }
    });
  }

  const controls = document.getElementById('resource-controls');
  if (controls) {
    controls.hidden = false;
    const search = document.getElementById('resource-search');
    const rows = Array.from(document.querySelectorAll('[data-resource]'));
    const buttons = Array.from(document.querySelectorAll('[data-filter]'));
    let category = 'all';
    const initialHash = { '#rent-resources': 'rent', '#bill-resources': 'bills', '#profile-resources': 'profiles', '#more-resources': 'other' };
    function applyFilter() {
      const query = search.value.trim().toLowerCase();
      let count = 0;
      rows.forEach(row => {
        const match = (category === 'all' || row.dataset.category === category) && row.textContent.toLowerCase().includes(query);
        row.hidden = !match;
        if (match) count++;
      });
      document.querySelectorAll('[data-resource-group]').forEach(group => {
        group.hidden = !Array.from(group.querySelectorAll('[data-resource]')).some(row => !row.hidden);
      });
      buttons.forEach(button => {
        const selected = button.dataset.filter === category;
        button.classList.toggle('is-active', selected);
        button.setAttribute('aria-pressed', String(selected));
      });
      document.getElementById('resource-count').textContent = count + ' of ' + rows.length + ' resources' + (query ? ' matching “' + search.value.trim() + '”' : '');
      document.getElementById('no-resources').hidden = count > 0;
    }
    buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.filter; applyFilter(); }));
    search.addEventListener('input', applyFilter);
    function followHash() {
      if (initialHash[window.location.hash]) {
        category = initialHash[window.location.hash];
        search.value = '';
        applyFilter();
      }
    }
    window.addEventListener('hashchange', followHash);
    followHash();
  }
})();
