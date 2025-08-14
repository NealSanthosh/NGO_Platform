// Theme switching functionality
(function() {
    'use strict';

    const THEME_KEY = 'donation-platform-theme';
    const LIGHT_THEME = 'light';
    const DARK_THEME = 'dark';

    // Get theme preference from localStorage or default to light
    function getStoredTheme() {
        return localStorage.getItem(THEME_KEY) || LIGHT_THEME;
    }

    // Store theme preference in localStorage
    function setStoredTheme(theme) {
        localStorage.setItem(THEME_KEY, theme);
    }

    // Apply theme to document
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        const darkThemeCSS = document.getElementById('dark-theme-css');
        if (darkThemeCSS) {
            darkThemeCSS.disabled = theme !== DARK_THEME;
        }

        // Update theme toggle button
        updateThemeToggleButton(theme);

        // Update theme-dependent elements
        updateThemeElements(theme);
    }

    // Update theme toggle button appearance
    function updateThemeToggleButton(theme) {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                if (theme === DARK_THEME) {
                    icon.className = 'fas fa-sun';
                    themeToggle.setAttribute('title', 'Switch to Light Mode');
                } else {
                    icon.className = 'fas fa-moon';
                    themeToggle.setAttribute('title', 'Switch to Dark Mode');
                }
            }
        }
    }

    // Update elements that need theme-specific handling
    function updateThemeElements(theme) {
        // Update charts if they exist
        if (window.Chart && window.Chart.instances) {
            Object.values(window.Chart.instances).forEach(chart => {
                if (chart.options && chart.options.scales) {
                    const textColor = theme === DARK_THEME ? '#ffffff' : '#666';
                    const gridColor = theme === DARK_THEME ? '#404040' : '#e9ecef';

                    // Update text colors
                    if (chart.options.scales.x) {
                        chart.options.scales.x.ticks = chart.options.scales.x.ticks || {};
                        chart.options.scales.x.ticks.color = textColor;
                        chart.options.scales.x.grid = chart.options.scales.x.grid || {};
                        chart.options.scales.x.grid.color = gridColor;
                    }
                    if (chart.options.scales.y) {
                        chart.options.scales.y.ticks = chart.options.scales.y.ticks || {};
                        chart.options.scales.y.ticks.color = textColor;
                        chart.options.scales.y.grid = chart.options.scales.y.grid || {};
                        chart.options.scales.y.grid.color = gridColor;
                    }

                    // Update legend
                    if (chart.options.plugins && chart.options.plugins.legend) {
                        chart.options.plugins.legend.labels = chart.options.plugins.legend.labels || {};
                        chart.options.plugins.legend.labels.color = textColor;
                    }

                    chart.update();
                }
            });
        }

        // Update map themes if they exist
        if (window.mapInstance) {
            const mapStyle = theme === DARK_THEME ? 'dark' : 'light';
            window.mapInstance.setStyle(`mapbox://styles/mapbox/${mapStyle}-v10`);
        }

        // Trigger custom theme change event
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: theme } 
        }));
    }

    // Toggle between light and dark themes
    function toggleTheme() {
        const currentTheme = getStoredTheme();
        const newTheme = currentTheme === LIGHT_THEME ? DARK_THEME : LIGHT_THEME;
        
        setStoredTheme(newTheme);
        setTheme(newTheme);

        // Analytics event (if analytics is available)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'theme_change', {
                'theme': newTheme
            });
        }
    }

    // Auto-detect system theme preference
    function getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return DARK_THEME;
        }
        return LIGHT_THEME;
    }

    // Initialize theme on page load
    function initializeTheme() {
        let theme = getStoredTheme();
        
        // If no stored preference, use system preference
        if (!localStorage.getItem(THEME_KEY)) {
            theme = getSystemTheme();
            setStoredTheme(theme);
        }
        
        setTheme(theme);
    }

    // Listen for system theme changes
    function watchSystemTheme() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            
            mediaQuery.addEventListener('change', function(e) {
                // Only auto-switch if user hasn't manually set a preference recently
                const lastManualChange = localStorage.getItem(THEME_KEY + '-manual');
                const oneHourAgo = Date.now() - (60 * 60 * 1000);
                
                if (!lastManualChange || parseInt(lastManualChange) < oneHourAgo) {
                    const systemTheme = e.matches ? DARK_THEME : LIGHT_THEME;
                    setStoredTheme(systemTheme);
                    setTheme(systemTheme);
                }
            });
        }
    }

    // Mark manual theme change
    function markManualThemeChange() {
        localStorage.setItem(THEME_KEY + '-manual', Date.now().toString());
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeTheme);
    } else {
        initializeTheme();
    }

    // Watch for system theme changes
    watchSystemTheme();

    // Set up theme toggle button click handler
    document.addEventListener('DOMContentLoaded', function() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', function(e) {
                e.preventDefault();
                markManualThemeChange();
                toggleTheme();
            });
        }
    });

    // Expose theme functions globally
    window.ThemeManager = {
        toggle: toggleTheme,
        set: setTheme,
        get: getStoredTheme,
        getSystem: getSystemTheme,
        LIGHT: LIGHT_THEME,
        DARK: DARK_THEME
    };

    // Handle theme transitions smoothly
    document.addEventListener('DOMContentLoaded', function() {
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    });

})();
