// BargainKart Core UI & Cart/Wishlist Interactivity

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Sidebar Toggle
    const sidebar = document.getElementById('appSidebar');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const closeBtn = document.getElementById('sidebarCloseBtn');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.add('mobile-open');
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', () => {
            sidebar.classList.remove('mobile-open');
        });
    }

    // 2. Global Add to Cart AJAX
    document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.getAttribute('data-product-id');
            const qty = btn.getAttribute('data-qty') || 1;
            const negotiatedId = btn.getAttribute('data-negotiated-id') || null;

            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';

            try {
                const response = await fetch('/api/cart/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId, quantity: qty, negotiated_id: negotiatedId })
                });

                const data = await response.json();
                if (response.ok && data.success) {
                    showToast(data.message, 'success');
                    // Update badges
                    document.querySelectorAll('.badge-dot, .badge-count').forEach(badge => {
                        badge.textContent = data.total_cart_items;
                    });
                } else {
                    if (response.status === 401) {
                        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                        return;
                    }
                    showToast(data.error || 'Failed to add item to cart', 'danger');
                }
            } catch (err) {
                showToast('Network error while adding to cart.', 'danger');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-cart-plus"></i> Add to Cart';
            }
        });
    });

    // 3. Wishlist Heart Toggle AJAX
    document.querySelectorAll('.wishlist-toggle-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const productId = btn.getAttribute('data-product-id');

            try {
                const response = await fetch('/api/wishlist/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_id: productId })
                });

                if (response.status === 401) {
                    window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }

                const data = await response.json();
                if (data.success) {
                    if (data.in_wishlist) {
                        btn.classList.add('active');
                        btn.innerHTML = '<i class="fa-solid fa-heart text-rose-500"></i>';
                        showToast(data.message, 'success');
                    } else {
                        btn.classList.remove('active');
                        btn.innerHTML = '<i class="fa-regular fa-heart"></i>';
                        showToast(data.message, 'info');
                    }
                }
            } catch (err) {
                showToast('Failed to update wishlist.', 'danger');
            }
        });
    });
});

// Toast notification helper
function showToast(message, type = 'info') {
    const container = document.querySelector('.flash-container') || document.body;
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.left = '28px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';

    const icon = type === 'success' ? 'fa-circle-check' : (type === 'danger' ? 'fa-circle-xmark' : 'fa-circle-info');
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
        <button type="button" class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// Global Microphone Permission & Setup Modal Helper
window.showMicPermissionModal = function() {
    let modal = document.getElementById('globalMicPermissionModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'globalMicPermissionModal';
        modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);backdrop-filter:blur(8px);z-index:999999;display:flex;align-items:center;justify-content:center;padding:20px;';
        modal.innerHTML = `
            <div style="max-width:520px;width:100%;background:#0f172a;border:2px solid #10b981;border-radius:16px;padding:28px;box-shadow:0 20px 50px rgba(0,0,0,0.9);position:relative;animation:fadeIn 0.25s ease;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="width:42px;height:42px;border-radius:50%;background:rgba(16,185,129,0.2);color:#34d399;display:flex;align-items:center;justify-content:center;font-size:1.3rem;box-shadow:0 0 15px rgba(16,185,129,0.3);">
                            <i class="fa-solid fa-microphone"></i>
                        </div>
                        <div>
                            <strong style="color:#fff;font-size:1.2rem;font-family:'Space Grotesk',sans-serif;display:block;">Microphone Access Guide</strong>
                            <span style="font-size:0.75rem;color:#38bdf8;">Browser & Windows Permissions for Voice AI</span>
                        </div>
                    </div>
                    <button type="button" onclick="document.getElementById('globalMicPermissionModal').style.display='none'" style="background:none;border:none;color:#94a3b8;font-size:1.6rem;cursor:pointer;line-height:1;">&times;</button>
                </div>

                <p style="font-size:0.86rem;color:#cbd5e1;line-height:1.5;margin-bottom:18px;">
                    Modern browsers protect your microphone by default until permission is granted on <code>http://127.0.0.1:5000</code>. Follow these 3 easy steps:
                </p>

                <div style="background:#1e293b;border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:16px;margin-bottom:18px;">
                    <div style="display:flex;gap:12px;margin-bottom:12px;font-size:0.84rem;color:#e2e8f0;align-items:flex-start;">
                        <span style="background:#38bdf8;color:#0f172a;font-weight:800;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:0.75rem;">1</span>
                        <span>Look at your browser's address bar at the top: Click the <strong>Tune / Lock icon (🔒 / 🎛️)</strong> right next to <code>http://127.0.0.1:5000</code>.</span>
                    </div>
                    <div style="display:flex;gap:12px;margin-bottom:12px;font-size:0.84rem;color:#e2e8f0;align-items:flex-start;">
                        <span style="background:#34d399;color:#0f172a;font-weight:800;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:0.75rem;">2</span>
                        <span>Find <strong>Microphone</strong> in the popup permissions menu and toggle it to <strong style="color:#34d399;">"Allow"</strong>.</span>
                    </div>
                    <div style="display:flex;gap:12px;font-size:0.84rem;color:#e2e8f0;align-items:flex-start;">
                        <span style="background:#a855f7;color:#fff;font-weight:800;border-radius:50%;width:22px;height:22px;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:0.75rem;">3</span>
                        <span>Click the mic button and start speaking — RoboBargain will transcribe your voice in real time!</span>
                    </div>
                </div>

                <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:8px;padding:12px;font-size:0.78rem;color:#fbbf24;margin-bottom:16px;line-height:1.4;">
                    <i class="fa-solid fa-triangle-exclamation"></i> <strong>Windows Settings Check:</strong> If still blocked, open <em>Windows Settings &rarr; Privacy & Security &rarr; Microphone</em> and ensure <em>"Let desktop apps access your microphone"</em> is turned <strong>ON</strong>.
                </div>

                <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:12px;font-size:0.78rem;color:#34d399;margin-bottom:20px;">
                    ✨ <strong>No Mic Needed Alternative:</strong> You can click any of the <strong>Voice Prompt Chips</strong> (e.g. <em>"Offer ₹180"</em>, <em>"Recommend for kitchen"</em>) to simulate speaking with zero microphone setup!
                </div>

                <button type="button" onclick="document.getElementById('globalMicPermissionModal').style.display='none'" class="btn btn-primary" style="width:100%;padding:11px;font-weight:800;font-size:0.92rem;background:linear-gradient(135deg, #059669, #10b981);border:none;">
                    Got It, Ready to Speak!
                </button>
            </div>
        `;
        document.body.appendChild(modal);
    } else {
        modal.style.display = 'flex';
    }
};
