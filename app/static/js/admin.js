/**
 * 后台管理脚本
 * 包含表格操作、批量删除、AJAX 请求等功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化确认删除
    initConfirmDeletes();

    // 自动高亮当前导航
    initActiveNav();
});


/**
 * ─── 删除确认 ───────────────────────────────────
 */
function initConfirmDeletes() {
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
}


/**
 * ─── 导航高亮 ───────────────────────────────────
 */
function initActiveNav() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/admin/') {
            link.classList.add('active');
        }
    });
}


/**
 * ─── 通用 AJAX 请求 ─────────────────────────────
 */
function ajaxRequest(url, method = 'POST', data = null) {
    const options = {
        method: method,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        }
    };

    if (data) {
        if (data instanceof FormData) {
            options.body = data;
        } else {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        }
    }

    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error('请求失败');
            }
            return response.json();
        })
        .catch(error => {
            console.error('AJAX Error:', error);
            throw error;
        });
}


/**
 * ─── 获取 CSRF Token ────────────────────────────
 */
function getCSRFToken() {
    const tokenElement = document.querySelector('input[name="csrf_token"]');
    if (tokenElement) {
        return tokenElement.value;
    }
    // 从 meta 标签获取
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    return metaToken ? metaToken.content : '';
}
