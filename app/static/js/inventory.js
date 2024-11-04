class InventorySearch {
    constructor() {
        this.searchTimeout = null;
        this.currentSort = { column: 'name', direction: 'asc' };
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.serialInput = document.getElementById('serial-search');
        this.searchInput = document.getElementById('main-search');
        this.sectionSelect = document.getElementById('section-filter');
        this.inventoryList = document.getElementById('inventoryList');
        this.emptyState = document.getElementById('empty-state');
        this.tableHeaders = document.querySelectorAll('[data-sort]');
        this.searchHelp = document.getElementById('search-help');
    }

    attachEventListeners() {
        // Search input listeners with debouncing
        ['input', 'change'].forEach(event => {
            this.serialInput?.addEventListener(event, () => this.debounceSearch());
            this.searchInput?.addEventListener(event, () => this.debounceSearch());
            this.sectionSelect?.addEventListener(event, () => this.debounceSearch());
        });

        // Sort header listeners
        this.tableHeaders.forEach(header => {
            header.addEventListener('click', () => this.handleSort(header));
        });

        // Search help tooltip
        this.searchHelp?.addEventListener('click', () => this.showSearchHelp());
    }

    showSearchHelp() {
        const helpText = `
Search Tips:
- Use quotes for exact phrases: "blue widget"
- Use AND/OR for multiple terms: blue AND widget
- Use parentheses for grouping: (blue OR red) AND widget
- Serial number has a dedicated search field
- Click column headers to sort
`;
        alert(helpText); // Replace with your preferred tooltip/modal implementation
    }

    handleSort(header) {
        const column = header.dataset.sort;

        // Update sort direction
        if (this.currentSort.column === column) {
            this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            this.currentSort.column = column;
            this.currentSort.direction = 'asc';
        }

        // Update header icons
        this.updateSortIcons();

        // Perform search with new sort
        this.performSearch();
    }

    updateSortIcons() {
        this.tableHeaders.forEach(header => {
            const isCurrentSort = header.dataset.sort === this.currentSort.column;

            // Get all sort icons in this header
            const defaultIcon = header.querySelector('.sort-default');
            const ascIcon = header.querySelector('.sort-asc');
            const descIcon = header.querySelector('.sort-desc');

            // Hide all icons first
            defaultIcon?.classList.add('hidden');
            ascIcon?.classList.add('hidden');
            descIcon?.classList.add('hidden');

            if (isCurrentSort) {
                // Show appropriate sort direction icon
                if (this.currentSort.direction === 'asc') {
                    ascIcon?.classList.remove('hidden');
                } else {
                    descIcon?.classList.remove('hidden');
                }
            } else {
                // Show default icon for non-sorted columns
                defaultIcon?.classList.remove('hidden');
            }
        });
    }

    debounceSearch() {
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        this.searchTimeout = setTimeout(() => this.performSearch(), 300);
    }

    async performSearch() {
        try {
            const params = new URLSearchParams({
                serial: this.serialInput?.value || '',
                q: this.searchInput?.value || '',
                section: this.sectionSelect?.value || '',
                sort: this.currentSort.column,
                direction: this.currentSort.direction
            });

            const response = await fetch(`/inventory/data?${params.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.updateTable(data);
        } catch (error) {
            console.error('Search failed:', error);
            this.showError('Search failed. Please try again.');
        }
    }

    updateTable(items) {
        if (!this.inventoryList) return;

        // Clear existing content
        this.inventoryList.innerHTML = '';

        // Show/hide empty state
        if (this.emptyState) {
            this.emptyState.classList.toggle('hidden', items.length > 0);
        }

        // If no items, return early
        if (items.length === 0) return;

        // Create and append new rows
        items.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50';

            row.innerHTML = `
                <td class="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900 truncate" style="max-width: 300px;">
                    ${this.escapeHtml(item.name)}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500 truncate" style="max-width: 150px;">
                    ${this.escapeHtml(item.location.section || '-')}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500" style="max-width: 75px;">
                    ${this.escapeHtml(item.location.shelf || '-')}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500" style="max-width: 75px;">
                    ${this.escapeHtml(item.location.box || '-')}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500" style="max-width: 90px;">
                    ${this.escapeHtml(item.serial_number || '-')}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-sm text-gray-500" style="max-width: 90px;">
                    ${item.quantity || 0}
                </td>
                <td class="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center justify-end space-x-3">
                        <a href="/inventory/${item.id}" class="text-blue-600 hover:text-blue-900" title="View Details">
                            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                            </svg>
                        </a>
                        <a href="/inventory/${item.id}/edit" class="text-indigo-600 hover:text-indigo-900" title="Edit Item">
                            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                        </a>
                    </div>
                </td>
            `;

            this.inventoryList.appendChild(row);
        });
    }

    escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    showError(message) {
        // You could implement this with a toast notification or alert
        console.error(message);
        alert(message);
    }
}

// Initialize search when document is ready
document.addEventListener('DOMContentLoaded', () => {
    new InventorySearch();
});