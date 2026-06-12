/**
 * 个人博客 - 前端主脚本
 * 包含主题切换、代码高亮、平滑滚动等功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initSmoothScroll();
    initTooltips();
});


/**
 * ─── 主题切换 ───────────────────────────────────
 * 支持日间/夜间模式，保存偏好到 localStorage
 * 默认跟随系统偏好 (prefers-color-scheme)
 */
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    if (!themeToggle) return;

    // 获取当前主题
    function getCurrentTheme() {
        return html.getAttribute('data-theme') || 'light';
    }

    // 设置主题
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('blog-theme', theme);

        // 更新图标
        if (themeIcon) {
            themeIcon.className = theme === 'dark'
                ? 'bi bi-sun-fill'
                : 'bi bi-moon-stars';
        }
    }

    // 切换主题
    function toggleTheme() {
        const current = getCurrentTheme();
        setTheme(current === 'dark' ? 'light' : 'dark');
    }

    // 初始化主题
    const savedTheme = localStorage.getItem('blog-theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // 跟随系统偏好
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDark ? 'dark' : 'light');
    }

    // 监听系统主题变化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (!localStorage.getItem('blog-theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });

    // 绑定切换事件
    themeToggle.addEventListener('click', toggleTheme);
}


/**
 * ─── 平滑滚动 ───────────────────────────────────
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}


/**
 * ─── Bootstrap Tooltips ─────────────────────────
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) {
        return new bootstrap.Tooltip(el);
    });
}


/**
 * ─── 回到顶部按钮 ───────────────────────────────
 */
function initBackToTop() {
    const btn = document.createElement('button');
    btn.id = 'backToTop';
    btn.className = 'btn btn-primary btn-sm position-fixed';
    btn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    btn.style.cssText = 'bottom: 20px; right: 20px; display: none; z-index: 999; border-radius: 50%; width: 40px; height: 40px;';
    document.body.appendChild(btn);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            btn.style.display = 'block';
        } else {
            btn.style.display = 'none';
        }
    });

    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}


/**
 * ─── AJAX CSRF Token ────────────────────────────
 * 为所有 AJAX POST 请求自动添加 CSRF Token
 */
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

if (csrfToken) {
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        if (options.method && options.method.toUpperCase() !== 'GET') {
            options.headers = options.headers || {};
            options.headers['X-CSRFToken'] = csrfToken;
        }
        return originalFetch(url, options);
    };
}
