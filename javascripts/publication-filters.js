function applyPublicationFilters(root) {
  (root || document).querySelectorAll('.pub-filters').forEach(function(filters) {
    const scope = filters.closest('article') || document;
    const selectedTag = filters.dataset.selectedTag || '';
    const selectedVenue = filters.dataset.selectedVenue || '';
    const entries = Array.from(scope.querySelectorAll('[data-publication-entry="true"]'));
    const yearHeaders = Array.from(scope.querySelectorAll('[data-publication-year]'));

    entries.forEach(function(entry) {
      const tags = (entry.dataset.tags || '').split(/\s+/).filter(Boolean);
      const venue = entry.dataset.venue || '';
      const matchesTag = !selectedTag || tags.includes(selectedTag);
      const matchesVenue = !selectedVenue || venue === selectedVenue;
      entry.parentElement.hidden = !(matchesTag && matchesVenue);
    });

    yearHeaders.forEach(function(header) {
      const year = header.dataset.publicationYear;
      const hasVisibleEntries = entries.some(function(entry) {
        return entry.dataset.year === year && !entry.parentElement.hidden;
      });
      header.hidden = !hasVisibleEntries;
    });

    filters.querySelectorAll('.pub-filter-chip').forEach(function(chip) {
      const isTag = chip.dataset.filterGroup === 'tags';
      const activeValue = isTag ? selectedTag : selectedVenue;
      const isActive = chip.dataset.value === activeValue;
      chip.classList.toggle('is-active', isActive);
      chip.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
  });
}

function initializePublicationFilters(root) {
  (root || document).querySelectorAll('.pub-filters').forEach(function(filters) {
    if (filters.dataset.pubFiltersInitialized === 'true') {
      return;
    }
    filters.dataset.pubFiltersInitialized = 'true';

    filters.querySelectorAll('.pub-filter-chip').forEach(function(chip) {
      chip.addEventListener('click', function() {
        if (chip.dataset.filterGroup === 'tags') {
          filters.dataset.selectedTag = filters.dataset.selectedTag === chip.dataset.value ? '' : chip.dataset.value;
        } else {
          filters.dataset.selectedVenue = filters.dataset.selectedVenue === chip.dataset.value ? '' : chip.dataset.value;
        }
        applyPublicationFilters(root);
      });
    });

    const clearButton = filters.querySelector('.pub-filter-clear');
    if (clearButton) {
      clearButton.addEventListener('click', function() {
        filters.dataset.selectedTag = '';
        filters.dataset.selectedVenue = '';
        applyPublicationFilters(root);
      });
    }
  });

  applyPublicationFilters(root);
}

document.addEventListener('DOMContentLoaded', initializePublicationFilters);
if (typeof document$ !== 'undefined' && document$ && typeof document$.subscribe === 'function') {
  document$.subscribe(initializePublicationFilters);
}
