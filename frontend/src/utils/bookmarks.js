// 📑 BOOKMARKS ENGINE
(function() {
    let bookmarks = JSON.parse(localStorage.getItem('vidya-bookmarks') || '[]');

    window.toggleBookmark = function(event, type, id, data) {
        if (event) event.stopPropagation();
        
        const index = bookmarks.findIndex(b => b.id === id && b.type === type);
        if (index > -1) {
            bookmarks.splice(index, 1);
            showToast('Removed from bookmarks', 'info');
        } else {
            bookmarks.push({ type, id, data, timestamp: Date.now() });
            showToast('Saved to bookmarks!', 'success');
        }
        
        localStorage.setItem('vidya-bookmarks', JSON.stringify(bookmarks));
        updateBookmarkUI();
        return (index === -1); // returns true if added
    };

    window.removeBookmark = function(event, id) {
        if (event) event.stopPropagation();
        bookmarks = bookmarks.filter(b => b.id !== id);
        localStorage.setItem('vidya-bookmarks', JSON.stringify(bookmarks));
        updateBookmarkUI();
        renderProfileBookmarks();
    };

    window.getBookmarks = function() {
        return bookmarks;
    };

    function updateBookmarkUI() {
        // Toggle active state on all buttons with this ID
        const btns = document.querySelectorAll(`.bookmark-btn[data-id]`);
        btns.forEach(btn => {
            const id = btn.dataset.id;
            const type = btn.dataset.type;
            const active = bookmarks.some(b => b.id === id && b.type === type);
            btn.classList.toggle('active', active);
            
            // Update icon only, preserve other text/elements
            const icon = btn.querySelector('.material-symbols-outlined');
            if (icon) {
                icon.textContent = active ? 'bookmark' : 'bookmark_border';
                icon.style.fontVariationSettings = active ? "'FILL' 1" : "'FILL' 0";
                
                // Update text node if it exists
                const textNode = Array.from(btn.childNodes).find(node => node.nodeType === 3 && node.textContent.trim().length > 1);
                if (textNode) {
                    const baseText = type === 'roadmap' ? 'Roadmap' : 'Job';
                    textNode.textContent = active ? ` Unsave ${baseText}` : ` Save ${baseText}`;
                }
            }
        });
    }

    // Export for profile rendering
    window.renderProfileBookmarks = function() {
        const container = document.getElementById('profileBookmarks');
        if (!container) return;

        if (bookmarks.length === 0) {
            container.innerHTML = '<div style="color:var(--dim); font-size:13px; text-align:center; padding:20px;">No bookmarks yet. Save a job or roadmap to see it here!</div>';
            return;
        }

        const roadmaps = bookmarks.filter(b => b.type === 'roadmap');
        const jobs = bookmarks.filter(b => b.type === 'job');

        let html = '';

        if (roadmaps.length > 0) {
            html += '<div class="profile-section-title">Saved Roadmaps</div>';
            html += roadmaps.map(b => renderItem(b)).join('');
        }

        if (jobs.length > 0) {
            html += '<div class="profile-section-title" style="margin-top:24px;">Saved Jobs</div>';
            html += jobs.map(b => renderItem(b)).join('');
        }

        container.innerHTML = html;
    };

    function renderItem(b) {
        return `
            <div class="bookmark-item">
                <div class="bookmark-type">${b.type}</div>
                <div class="bookmark-title">${b.data.title || 'Untitled'}</div>
                <div class="bookmark-meta">${b.data.subtitle || ''}</div>
                <div class="bookmark-remove" onclick="removeBookmark(event, '${b.id}')">×</div>
                <a href="#" onclick="openBookmark('${b.type}', '${b.id}')" style="position:absolute; inset:0;"></a>
            </div>
        `;
    }

    window.openBookmark = function(type, id) {
        const b = bookmarks.find(x => x.id === id && x.type === type);
        if (!b) return;

        if (type === 'job') {
            showPage('jobs');
            // In a real app we'd scroll to it or highlights it
        } else if (type === 'roadmap') {
            showPage('roadmap');
            // Re-render roadmap from saved data if needed
            if (window.renderPath && b.data.fullPath) {
                window.renderPath(b.data.fullPath);
                document.getElementById('ljPath').classList.add('visible');
            }
        }
    };

    window.addEventListener('DOMContentLoaded', updateBookmarkUI);
})();
