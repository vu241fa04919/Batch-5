/* ----------------------------------------------------
   HOSTELCARE - INTERACTIVE FRONT-END LOGIC (VANILLA JS)
   ---------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup modal opening listeners for "Raise Complaint"
    const openBtns = document.querySelectorAll('.open-raise-modal-btn');
    openBtns.forEach(btn => {
        btn.addEventListener('click', openRaiseModal);
    });

    // 2. Setup raise complaint form AJAX submission
    const raiseForm = document.getElementById('raise-complaint-form');
    if (raiseForm) {
        raiseForm.addEventListener('submit', handleRaiseComplaintSubmit);
    }
    
    // Close modal on overlay click
    const modalOverlay = document.getElementById('raise-modal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) {
                closeRaiseModal();
            }
        });
    }

    const wardenOverlay = document.getElementById('warden-modal');
    if (wardenOverlay) {
        wardenOverlay.addEventListener('click', (e) => {
            if (e.target === wardenOverlay) {
                closeWardenModal();
            }
        });
    }
});

/* Modal Controls */
function openRaiseModal() {
    const modal = document.getElementById('raise-modal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Lock background scroll
}

function closeRaiseModal() {
    const modal = document.getElementById('raise-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('raise-complaint-form').reset();
}

function openWardenModal() {
    const modal = document.getElementById('warden-modal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeWardenModal() {
    const modal = document.getElementById('warden-modal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

/* Remarks Collapsible Drawer Toggle */
function toggleRemarks(id) {
    const card = document.getElementById(`complaint-${id}`);
    if (!card) return;

    // Check if card is currently active
    const isActive = card.classList.contains('active');
    
    // Close other active drawers for accordion effect
    document.querySelectorAll('.complaint-card').forEach(c => {
        c.classList.remove('active');
    });

    if (!isActive) {
        card.classList.add('active');
    }
}

/* Interactive Front-end Stats Filtering */
function filterComplaints(status) {
    const list = document.getElementById('complaints-list');
    const items = list.querySelectorAll('.filter-item');
    let found = 0;

    items.forEach(item => {
        // Handle "In Progress" as a part of "Pending" for visual grouping in some stats
        const itemStatus = item.classList.contains('Resolved') ? 'Resolved' : 'Pending';
        
        if (itemStatus === status) {
            item.style.display = 'flex';
            found++;
        } else {
            item.style.display = 'none';
        }
    });

    // Handle empty state if filter shows nothing
    const emptyState = list.querySelector('.empty-state');
    if (found === 0) {
        if (!emptyState) {
            const div = document.createElement('div');
            div.className = 'empty-state temp-empty';
            div.innerHTML = `<i class="fa-solid fa-filter"></i><p>No ${status} complaints found.</p>`;
            list.appendChild(div);
        } else {
            emptyState.style.display = 'flex';
        }
    } else {
        const tempEmpty = list.querySelector('.temp-empty');
        if (tempEmpty) tempEmpty.remove();
        if (emptyState) emptyState.style.display = 'none';
    }
}

function resetFilters() {
    const list = document.getElementById('complaints-list');
    const items = list.querySelectorAll('.filter-item');
    
    items.forEach(item => {
        item.style.display = 'flex';
    });

    const tempEmpty = list.querySelector('.temp-empty');
    if (tempEmpty) tempEmpty.remove();

    const emptyState = list.querySelector('.empty-state');
    if (emptyState) {
        if (items.length > 0) {
            emptyState.style.display = 'none';
        } else {
            emptyState.style.display = 'flex';
        }
    }
}

/* Floating Notification Tray Toggle */
function toggleNotifications() {
    const tray = document.getElementById('notification-tray');
    tray.classList.toggle('active');
}

// Close trays and dropdowns when clicking outside
document.addEventListener('click', (e) => {
    const tray = document.getElementById('notification-tray');
    const bell = document.querySelector('.notification-bell');
    
    if (tray && tray.classList.contains('active')) {
        if (!tray.contains(e.target) && !bell.contains(e.target)) {
            tray.classList.remove('active');
        }
    }

    const dropdown = document.getElementById('mini-logout-dropdown');
    const pill = document.querySelector('.profile-pill');
    const chevron = document.querySelector('.profile-pill .dropdown-arrow-icon');

    if (dropdown && dropdown.classList.contains('active')) {
        if (!dropdown.contains(e.target) && !pill.contains(e.target)) {
            dropdown.classList.remove('active');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
        }
    }
});

/* AJAX API: Raise Complaint Form Handler */
async function handleRaiseComplaintSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('.btn-submit');
    const originalBtnHTML = submitBtn.innerHTML;
    
    // Disable submit button and show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `Submitting... <i class="fa-solid fa-spinner fa-spin"></i>`;
    
    const formData = new FormData(form);
    
    try {
        const response = await fetch('/api/complaints/raise/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // Success animation
            submitBtn.innerHTML = `Success! 🎉`;
            submitBtn.style.backgroundColor = 'var(--color-green-icon)';
            
            setTimeout(() => {
                closeRaiseModal();
                // Reset button styles
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnHTML;
                submitBtn.style.backgroundColor = '';
                
                // Dynamically insert new complaint into recent list
                addNewComplaintToDOM(result.complaint);
                
                // Increment stats numbers dynamically
                updateStatsCounters('total');
                updateStatsCounters('pending');
            }, 1000);
            
        } else {
            alert(result.error || 'Failed to raise complaint. Please try again.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnHTML;
        }
    } catch (err) {
        console.error('API Error:', err);
        alert('An unexpected network error occurred.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnHTML;
    }
}

/* Helper: Add New Complaint to DOM Dynamically */
function addNewComplaintToDOM(c) {
    const list = document.getElementById('complaints-list');
    
    // Remove empty state if present
    const emptyState = list.querySelector('.empty-state');
    if (emptyState) emptyState.style.display = 'none';

    // Map categories to FontAwesome icons
    let iconClass = 'fa-solid fa-circle-info';
    if (c.category === 'Electrical') iconClass = 'fa-regular fa-lightbulb';
    else if (c.category === 'Plumbing') iconClass = 'fa-solid fa-droplet';
    else if (c.category === 'Housekeeping') iconClass = 'fa-solid fa-broom';
    else if (c.category === 'Internet/Wi-Fi') iconClass = 'fa-solid fa-wifi';
    else if (c.category === 'Mess/Food') iconClass = 'fa-solid fa-utensils';

    const slugifiedCat = c.category.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');

    const cardHTML = `
        <div class="complaint-card filter-item ${c.status} animate-scale-up" id="complaint-${c.id}" onclick="toggleRemarks(${c.id})">
            <div class="complaint-left">
                <div class="category-icon icon-${slugifiedCat}">
                    <i class="${iconClass}"></i>
                </div>
                <div class="complaint-main">
                    <h3>${c.title}</h3>
                    <p class="complaint-date">${c.created_at}</p>
                </div>
            </div>
            <div class="complaint-right">
                <span class="badge badge-pending">${c.status}</span>
                <i class="fa-solid fa-chevron-down expand-indicator"></i>
            </div>
            
            <div class="remarks-drawer" id="remarks-${c.id}">
                <div class="drawer-content">
                    <strong>Description:</strong>
                    <p>Complaint has been raised. A hostel technician will be assigned shortly.</p>
                </div>
            </div>
        </div>
    `;

    // Insert at the top of the list
    list.insertAdjacentHTML('afterbegin', cardHTML);
}

/* Helper: Increment counter values */
function updateStatsCounters(type) {
    const counter = document.getElementById(`stat-${type}`);
    if (counter) {
        let val = parseInt(counter.textContent) || 0;
        counter.textContent = val + 1;
        
        // Quick scaling micro-animation on counter
        counter.style.transform = 'scale(1.2)';
        counter.style.transition = 'transform 0.1s ease';
        setTimeout(() => {
            counter.style.transform = 'scale(1)';
        }, 150);
    }
}

/* AJAX API: Clear notifications */
async function clearNotifications(e) {
    e.stopPropagation();
    try {
        const response = await fetch('/api/notifications/read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            }
        });
        if (response.ok) {
            // Remove the count badge
            const badge = document.getElementById('bell-badge-count');
            if (badge) badge.remove();
            
            // Mark all items as read in UI
            document.querySelectorAll('.tray-item').forEach(item => {
                item.classList.remove('unread');
            });
        }
    } catch (err) {
        console.error('Failed to clear notifications:', err);
    }
}

/* Floating Mini Logout Dropdown Toggle */
function toggleDropdownMenu(e) {
    e.stopPropagation();
    const dropdown = document.getElementById('mini-logout-dropdown');
    const chevron = document.querySelector('.profile-pill .dropdown-arrow-icon');
    
    if (!dropdown) return;
    
    // Toggle visibility
    const isActive = dropdown.classList.contains('active');
    
    // Close notification tray first
    const tray = document.getElementById('notification-tray');
    if (tray) tray.classList.remove('active');

    if (isActive) {
        dropdown.classList.remove('active');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    } else {
        dropdown.classList.add('active');
        if (chevron) chevron.style.transform = 'rotate(180deg)';
    }
}
