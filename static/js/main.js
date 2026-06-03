/**
 * Smart Car Dealership - Enhanced JavaScript
 * Handles UI interactions, AJAX, dark mode, toasts, modals, and skeletons
 */

/* ============================
   TOAST NOTIFICATIONS
   ============================ */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer') || createToastContainer();

    const iconMap = {
        success: 'bi-check-circle-fill',
        danger:  'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info:    'bi-info-circle-fill'
    };

    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;
    toast.innerHTML = `
        <i class="bi ${iconMap[type] || iconMap.info} toast-icon"></i>
        <span class="toast-msg">${message}</span>
        <button class="toast-close" onclick="dismissToast(this.parentElement)">
            <i class="bi bi-x"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto-dismiss after 4 seconds
    setTimeout(() => dismissToast(toast), 4000);
}

function dismissToast(toastEl) {
    if (!toastEl || toastEl.classList.contains('removing')) return;
    toastEl.classList.add('removing');
    setTimeout(() => toastEl.remove(), 380);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

/* ============================
   DARK MODE TOGGLE
   ============================ */
function initDarkMode() {
    const stored = localStorage.getItem('darkMode');
    if (stored === 'true') {
        document.body.classList.add('dark-mode');
        updateDarkModeToggle(true);
    }

    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', isDark);
            updateDarkModeToggle(isDark);
        });
    }
}

function updateDarkModeToggle(isDark) {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;
    toggle.innerHTML = isDark
        ? '<i class="bi bi-sun-fill"></i>'
        : '<i class="bi bi-moon-fill"></i>';
    toggle.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
}

/* ============================
   SKELETON LOADERS
   ============================ */
function showSkeletons(container) {
    const skeletonHTML = `
        <div class="skeleton-card">
            <div class="skeleton-img"></div>
            <div class="skeleton-body">
                <div class="skeleton-line long"></div>
                <div class="skeleton-line medium"></div>
                <div class="skeleton-line short"></div>
                <div class="skeleton-line price"></div>
            </div>
        </div>`;

    // Render 8 skeleton cards
    container.innerHTML = Array(8).fill(skeletonHTML).join('');
}

/* ============================
   LIVE SEARCH (with debounce)
   ============================ */
document.addEventListener('DOMContentLoaded', function () {

    // ---- Toast setup ----
    initDarkMode();

    const alerts = document.querySelectorAll('.alert[data-toast]');
    alerts.forEach(function (alert) {
        const msg    = alert.textContent.trim();
        const cat    = alert.className.match(/alert-(success|danger|warning|info)/);
        const type   = cat ? cat[1] : 'info';
        showToast(msg, type);
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 300);
        }, 500);
    });

    // ---- Live search debounce ----
    const searchInput = document.querySelector('input[name="search"]');
    let debounceTimer;
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                const form = searchInput.closest('form');
                if (form && searchInput.value.length > 2) {
                    showSkeletons(document.querySelector('.car-grid') || document.querySelector('.row-cols-1'));
                }
            }, 500);
        });
    }

    // ---- Toggle password visibility ----
    document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const target = document.querySelector(btn.dataset.target);
            if (!target) return;
            const isPassword = target.type === 'password';
            target.type = isPassword ? 'text' : 'password';
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
            }
        });
    });

    // ---- Modal confirmations ----
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            const message = el.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) e.preventDefault();
        });
    });

    // Confirm all "Reject" / "Cancel" / "Delete" buttons via modal
    document.querySelectorAll('button[value="reject"], button[data-action="reject"], button[data-action="delete"]').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const msg = btn.dataset.confirmMsg || 'This action cannot be undone. Continue?';
            if (!confirm(msg)) e.preventDefault();
        });
    });

    // ---- Test drive date minimum ----
    const dateInput = document.querySelector('input[type="datetime-local"]');
    if (dateInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.min = now.toISOString().slice(0, 16);
    }

    // ---- Active nav highlighting ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link, .admin-sidebar .nav-link').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && (href === currentPath || currentPath.startsWith(href)) && href !== '/') {
            link.classList.add('active');
        }
    });

    // ---- Scroll-to-top button ----
    const scrollBtn = document.getElementById('scrollTopBtn');
    if (scrollBtn) {
        window.addEventListener('scroll', function () {
            scrollBtn.classList.toggle('visible', window.scrollY > 300);
        });
        scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }
});

/* ============================
   FETCH API HELPER
   ============================ */
async function fetchCars(params) {
    try {
        const url = new URL('/cars/api/list', window.location.origin);
        Object.keys(params).forEach(key => {
            if (params[key]) url.searchParams.append(key, params[key]);
        });
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch cars');
        return await response.json();
    } catch (error) {
        console.error('Error fetching cars:', error);
        return [];
    }
}

/* ============================
   MODAL CONFIRM HELPERS
   ============================ */
function showConfirmModal(title, message, iconType, onConfirm) {
    // Remove existing modal if any
    const existing = document.getElementById('confirmModal');
    if (existing) existing.remove();

    const iconMap = {
        warning: 'bi-exclamation-triangle-fill text-warning',
        success: 'bi-check-circle-fill text-success',
        danger:  'bi-x-circle-fill text-danger',
        info:    'bi-info-circle-fill text-info'
    };

    const modalHTML = `
    <div class="modal fade" id="confirmModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-sm">
            <div class="modal-content text-center">
                <div class="modal-body py-4">
                    <i class="bi ${iconMap[iconType] || iconMap.info} modal-confirm-icon ${iconType}"></i>
                    <h5 class="mb-2">${title}</h5>
                    <p class="text-muted small mb-3">${message}</p>
                    <div class="d-flex gap-2 justify-content-center">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmModalYes">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modalEl = document.getElementById('confirmModal');
    const modal = new bootstrap.Modal(modalEl);

    document.getElementById('confirmModalYes').addEventListener('click', () => {
        modal.hide();
        if (onConfirm) onConfirm();
    });

    modalEl.addEventListener('hidden.bs.modal', () => modalEl.remove());
    modal.show();
}

/* ============================
   COUNT-UP ANIMATION
   ============================ */
function animateCountUp(element, target, duration = 1200) {
    let start = 0;
    const increment = target / (duration / 16);
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = target.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(start).toLocaleString();
        }
    }, 16);
}

document.querySelectorAll('[data-count-up]').forEach(el => {
    const target = parseInt(el.dataset.countUp, 10);
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCountUp(el, target);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    observer.observe(el);
});