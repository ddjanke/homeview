// Main application JavaScript
let mainContent; // Global variable for main content area

// Cache system for tabs
const tabCache = {
    calendar: { data: null, lastLoaded: null, autoRefreshInterval: null },
    chores: { data: null, lastLoaded: null, autoRefreshInterval: null },
    todos: { data: null, lastLoaded: null, autoRefreshInterval: null },
    weather: { data: null, lastLoaded: null, autoRefreshInterval: null }
};

// Auto-refresh interval (5 minutes)
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes in milliseconds

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Get main content element
    mainContent = document.querySelector('.app-main');
    
    initializeNavigation();
    initializeTimeDisplay();
    initializeWeatherWidget();
    initializeSystemStatus();
    initializeDashboard();
    initializeThemeToggle();
    
    // Initialize the current tab content if it's already loaded
    const currentTab = getCurrentTab();
    if (currentTab) {
        initializeTabContent(currentTab);
    }
}

function getCurrentTab() {
    // Check which tab content is currently loaded
    if (mainContent.querySelector('.weather-container')) {
        return 'weather';
    } else if (mainContent.querySelector('.chores-container')) {
        return 'chores';
    } else if (mainContent.querySelector('.todos-container')) {
        return 'todos';
    } else if (mainContent.querySelector('.calendar-container')) {
        return 'calendar';
    }
    return null;
}

// Global function for switching tabs
function switchToTab(tabName) {
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked tab
    const targetBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
    
    // Ensure loading overlay is hidden before switching
    hideLoading();
    
    // Load tab content
    loadTabContent(tabName);
    hideLoading();
}

function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    
    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.dataset.tab;
            switchToTab(tabName);
        });
    });
}

function initializeDashboard() {
    // Set up dashboard card click handlers
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    if (dashboardCards.length > 0) {
        dashboardCards.forEach(card => {
            card.addEventListener('click', function() {
                const tab = this.dataset.tab;
                switchToTab(tab);
            });
        });
    }
}
    
function loadTabContent(tabName) {
    
    if (!mainContent) {
        console.error('mainContent element not found!');
        hideLoading();
        return;
    }
    
    showLoading();
    
    fetch(`/${tabName}/`)
        .then(response => {
            return response.text();
        })
        .then(html => {
            mainContent.innerHTML = html;
            // Initialize tab-specific functionality after a brief delay
            // to ensure the DOM is ready
            setTimeout(() => {
                initializeTabContent(tabName);
            }, 100);
        })
        .catch(error => {
            console.error('Error loading tab content:', error);
            showError('Error loading content');
            // Hide loading overlay on error
            hideLoading();
        });
}

function initializeTabContent(tabName) {
    // Initialize tab-specific JavaScript
    console.log('initializeTabContent called for:', tabName);
    
    // Check if we have cached data and it's recent (less than 5 minutes old)
    const cache = tabCache[tabName];
    const now = Date.now();
    const isDataFresh = cache.data && cache.lastLoaded && (now - cache.lastLoaded) < AUTO_REFRESH_INTERVAL;
    
    switch(tabName) {
        case 'calendar':
            console.log('Initializing calendar');
            if (isDataFresh) {
                console.log('Using cached calendar data');
                displayCalendar();
                setupCalendarRefresh();
            } else {
                initializeCalendar();
            }
            break;
        case 'chores':
            console.log('Initializing chores');
            if (isDataFresh) {
                console.log('Using cached chores data');
                displayChores();
                setupChoresRefresh();
            } else {
                initializeChores();
            }
            break;
        case 'todos':
            console.log('Initializing todos');
            if (isDataFresh) {
                console.log('Using cached todos data');
                displayTodos();
                setupTodosRefresh();
            } else {
                initializeTodos();
            }
            break;
        case 'weather':
            console.log('Initializing weather');
            console.log('Weather cache data:', tabCache.weather.data);
            console.log('Weather cache lastLoaded:', tabCache.weather.lastLoaded);
            console.log('isDataFresh:', isDataFresh);
            if (isDataFresh && tabCache.weather.data) {
                console.log('Using cached weather data');
                displayWeatherData(tabCache.weather.data);
                setupWeatherRefresh();
            } else {
                console.log('Loading fresh weather data');
                initializeWeather();
            }
            break;
    }
}
    

function initializeTimeDisplay() {
    let lastTimeStr = '';
    let lastDateStr = '';
    
    function updateTime() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const dateStr = now.toLocaleDateString([], {weekday: 'long', month: 'short', day: 'numeric'});
        
        // Only update DOM if time or date actually changed
        if (timeStr !== lastTimeStr) {
            const timeElement = document.getElementById('current-time');
            if (timeElement) {
                timeElement.textContent = timeStr;
            }
            lastTimeStr = timeStr;
        }
        
        if (dateStr !== lastDateStr) {
            const dateElement = document.getElementById('current-date');
            if (dateElement) {
                dateElement.textContent = dateStr;
            }
            lastDateStr = dateStr;
        }
    }
    
    // Update time every second
    setInterval(updateTime, 1000);
    updateTime();
}

function initializeWeatherWidget() {
    function updateWeatherWidget() {
        fetch('/weather/api/current')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.weather) {
                    const weather = data.weather;
                    const tempElement = document.querySelector('.weather-temp');
                    const descElement = document.querySelector('.weather-desc');
                    const iconElement = document.querySelector('.weather-icon i');
                    
                    if (tempElement) {
                        tempElement.textContent = `${Math.round(weather.temp)}°`;
                    }
                    if (descElement) {
                        descElement.textContent = weather.description || 'Clear';
                    }
                    if (iconElement) {
                        // Map custom weather icon names to Font Awesome icons
                        const iconMap = {
                            'sunny': 'fas fa-sun',
                            'clear-night': 'fas fa-moon',
                            'partly-cloudy': 'fas fa-cloud-sun',
                            'partly-cloudy-night': 'fas fa-cloud-moon',
                            'cloudy': 'fas fa-cloud',
                            'rainy': 'fas fa-cloud-rain',
                            'thunderstorm': 'fas fa-bolt',
                            'snowy': 'fas fa-snowflake',
                            'foggy': 'fas fa-smog'
                        };
                        const iconName = weather.icon || 'sunny';
                        const iconClass = iconMap[iconName] || 'fas fa-cloud-sun';
                        iconElement.className = iconClass;
                    }
                }
            })
            .catch(error => {
                console.log('Weather widget update failed:', error);
                // Keep default values on error
            });
    }
    
    // Update weather every 10 minutes
    setInterval(updateWeatherWidget, 600000);
    updateWeatherWidget();
}

function initializeSystemStatus() {
    // Check system status periodically
    function checkSystemStatus() {
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('system-status');
                if (statusElement) {
                    statusElement.textContent = data.status || 'Online';
                    statusElement.className = data.status === 'Online' ? 'online' : 'offline';
                }
            })
            .catch(error => {
                console.error('Error checking system status:', error);
                const statusElement = document.getElementById('system-status');
                if (statusElement) {
                    statusElement.textContent = 'Offline';
                    statusElement.className = 'offline';
                }
            });
    }
    
    // Check status every 30 seconds
    setInterval(checkSystemStatus, 30000);
    checkSystemStatus();
}

function showLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.add('hidden');
    }
}

function showError(message) {
    // Simple error display - could be enhanced with a proper modal
    alert('Error: ' + message);
}

function showMessage(message) {
    // Simple message display - could be enhanced with a proper notification
    alert(message);
}

// Global function to force hide loading overlay
window.forceHideLoading = function() {
    console.log('Force hiding loading overlay');
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.add('hidden');
    }
};

// Force hide loading overlay immediately on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - force hiding loading overlay');
    hideLoading();
});

// Auto-hide loading overlay after 3 seconds as a safety measure
setInterval(() => {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay && !loadingOverlay.classList.contains('hidden')) {
        console.log('Auto-hiding loading overlay after 3 seconds');
        loadingOverlay.classList.add('hidden');
    }
}, 3000);

// Tab-specific initialization functions
function initializeCalendar() {
    // Calendar-specific initialization
    console.log('Initializing calendar');
    loadCalendarData();
    setupCalendarRefresh();
}

function setupCalendarRefresh() {
    // Set up manual refresh button
    const refreshBtn = document.getElementById('refresh-calendar');
    if (refreshBtn) {
        refreshBtn.removeEventListener('click', loadCalendarData); // Remove existing listener
        refreshBtn.addEventListener('click', () => {
            console.log('Manual calendar refresh triggered');
            loadCalendarData(true); // Force refresh
        });
    }
    
    // Set up auto-refresh interval
    if (tabCache.calendar.autoRefreshInterval) {
        clearInterval(tabCache.calendar.autoRefreshInterval);
    }
    
    tabCache.calendar.autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing calendar data');
        loadCalendarData(true);
    }, AUTO_REFRESH_INTERVAL);
}

function initializeChores() {
    // Chores-specific initialization
    console.log('Initializing chores');
    loadChoresData();
    setupChoresRefresh();
}

function setupChoresRefresh() {
    // Set up manual refresh button
    const refreshBtn = document.getElementById('refresh-chores');
    if (refreshBtn) {
        refreshBtn.removeEventListener('click', loadChoresData);
        refreshBtn.addEventListener('click', () => {
            console.log('Manual chores refresh triggered');
            loadChoresData(true);
        });
    }
    
    // Set up sync button
    const syncBtn = document.getElementById('sync-chores');
    if (syncBtn) {
        syncBtn.addEventListener('click', syncChores);
    }
    
    // Set up reset button
    const resetBtn = document.getElementById('reset-chores');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetChores);
    }
    
    // Setup toggle switch for showing all chores vs today only
    const showAllToggle = document.getElementById('show-all-chores');
    const toggleLabel = document.getElementById('toggle-label');
    if (showAllToggle && toggleLabel) {
        showAllToggle.addEventListener('change', function() {
            // Update label text
            toggleLabel.textContent = this.checked ? 'Show All' : 'Show Today Only';
            // Refresh the display
            displayChores();
        });
    }
    
    // Set up hold-to-complete functionality
    initializeChoresHoldToComplete();
    
    // Set up auto-refresh interval
    if (tabCache.chores.autoRefreshInterval) {
        clearInterval(tabCache.chores.autoRefreshInterval);
    }
    
    tabCache.chores.autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing chores data');
        loadChoresData(true);
    }, AUTO_REFRESH_INTERVAL);
}

function initializeTodos() {
    // Todos-specific initialization
    console.log('Initializing todos');
    loadTodosData();
    setupTodosRefresh();
}

function setupTodosRefresh() {
    // Set up manual refresh button
    const refreshBtn = document.getElementById('refresh-todos');
    if (refreshBtn) {
        refreshBtn.removeEventListener('click', loadTodosData);
        refreshBtn.addEventListener('click', () => {
            console.log('Manual todos refresh triggered');
            loadTodosData(true);
        });
    }
    
    // Set up sync button
    const syncBtn = document.getElementById('sync-todos');
    if (syncBtn) {
        syncBtn.addEventListener('click', syncTodos);
    }
    
    // Set up add button
    const addBtn = document.getElementById('add-todo');
    if (addBtn) {
        addBtn.addEventListener('click', addTodo);
    }
    
    // Set up hold-to-complete functionality
    initializeTodosHoldToComplete();
    
    // Set up auto-refresh interval
    if (tabCache.todos.autoRefreshInterval) {
        clearInterval(tabCache.todos.autoRefreshInterval);
    }
    
    tabCache.todos.autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing todos data');
        loadTodosData(true);
    }, AUTO_REFRESH_INTERVAL);
}

// Weather refresh button is set up directly in buildWeatherContent()

function initializeWeather() {
    // Weather-specific initialization
    console.log('Initializing weather');
    loadWeatherData();
    setupWeatherRefresh();
}

function setupWeatherRefresh() {
    // Set up manual refresh button
    const refreshBtn = document.getElementById('refresh-weather');
    if (refreshBtn) {
        refreshBtn.removeEventListener('click', loadWeatherData);
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loadWeatherData(true);
        });
    }
    
    // Set up auto-refresh interval
    if (tabCache.weather.autoRefreshInterval) {
        clearInterval(tabCache.weather.autoRefreshInterval);
    }
    
    tabCache.weather.autoRefreshInterval = setInterval(() => {
        console.log('Auto-refreshing weather data');
        loadWeatherData(true);
    }, AUTO_REFRESH_INTERVAL);
}


function loadWeatherData(forceRefresh = false) {
    console.log('loadWeatherData called from main app.js', forceRefresh ? '(forced refresh)' : '');
    
    // Check cache first unless forcing refresh
    if (!forceRefresh && tabCache.weather.data) {
        console.log('Using cached weather data');
        displayWeatherData(tabCache.weather.data);
        return;
    }
    
    showLoading();
    
    fetch('/weather/api/all')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                
                // Update cache
                tabCache.weather.data = data.weather;
                tabCache.weather.lastLoaded = Date.now();
                
                displayWeatherData(data.weather);
            } else {
                console.error('API error:', data.error);
                showError('Failed to load weather: ' + (data.error || 'Unknown error'));
                displayWeatherData(null);
            }
        })
        .catch(error => {
            console.error('Error loading weather:', error);
            showError('Error loading weather: ' + error.message);
            displayWeatherData(null);
        })
        .finally(() => {
            console.log('Weather loading complete, hiding loading overlay');
            hideLoading();
        });
}

function displayWeatherData(weatherData) {
    console.log('displayWeatherData called with:', weatherData);
    if (!weatherData) {
        console.log('No weather data, showing empty state');
        // Show empty state
        const tempElement = document.getElementById('weather-temp');
        const conditionElement = document.getElementById('weather-condition');
        const humidityElement = document.getElementById('humidity');
        const windElement = document.getElementById('wind-speed');
        const forecastElement = document.getElementById('forecast-grid');
        const alertsElement = document.getElementById('weather-alerts');
        
        if (tempElement) tempElement.textContent = '--°F';
        if (conditionElement) conditionElement.textContent = 'Click "Refresh" to load weather data';
        if (humidityElement) humidityElement.textContent = '--%';
        if (windElement) windElement.textContent = '-- mph';
        if (forecastElement) forecastElement.innerHTML = '<div class="no-weather">No weather data available. Click "Refresh" to load weather information.</div>';
        if (alertsElement) alertsElement.style.display = 'none';
        return;
    }
    
    // Display current weather
    console.log('weatherData.current:', weatherData.current);
    if (weatherData.current) {
        const current = weatherData.current;
        console.log('Updating current weather with:', current);
        
        const tempElement = document.getElementById('weather-temp');
        const conditionElement = document.getElementById('weather-condition');
        const humidityElement = document.getElementById('humidity');
        const windElement = document.getElementById('wind-speed');
        const iconElement = document.getElementById('weather-icon');
        
        if (tempElement) tempElement.textContent = `${Math.round(current.temperature)}°F`;
        if (conditionElement) conditionElement.textContent = current.description;
        if (humidityElement) humidityElement.textContent = `${current.humidity}%`;
        if (windElement) windElement.textContent = `${current.wind_speed} mph`;
        
        // Update weather icon
        if (iconElement) {
            const iconClass = getWeatherIcon(current.icon);
            iconElement.innerHTML = `<i class="fas ${iconClass}"></i>`;
        }
    } else {
        console.log('No current weather data found');
    }
    
    // Display forecast
    if (weatherData.forecast && weatherData.forecast.length > 0) {
        const forecastGrid = document.getElementById('forecast-grid');
        if (forecastGrid) {
            forecastGrid.innerHTML = '';
            
            weatherData.forecast.forEach(day => {
                const forecastItem = createForecastItem(day);
                forecastGrid.appendChild(forecastItem);
            });
        }
    }
    
    // Display alerts
    if (weatherData.alerts && weatherData.alerts.length > 0) {
        const alertsContainer = document.getElementById('weather-alerts');
        const alertsList = document.getElementById('alerts-list');
        if (alertsContainer && alertsList) {
            alertsContainer.style.display = 'block';
            alertsList.innerHTML = '';
            
            weatherData.alerts.forEach(alert => {
                const alertItem = createAlertItem(alert);
                alertsList.appendChild(alertItem);
            });
        }
    } else {
        const alertsContainer = document.getElementById('weather-alerts');
        if (alertsContainer) {
            alertsContainer.style.display = 'none';
        }
    }
    
    // Update last updated time
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement && weatherData.current) {
        const lastUpdated = new Date(weatherData.current.last_updated);
        lastUpdatedElement.textContent = `Last updated: ${lastUpdated.toLocaleString()}`;
    }
}

function getWeatherIcon(iconName) {
    // Map custom weather icon names to Font Awesome icons
    const iconMap = {
        'sunny': 'fa-sun',
        'clear-night': 'fa-moon',
        'partly-cloudy': 'fa-cloud-sun',
        'partly-cloudy-night': 'fa-cloud-moon',
        'cloudy': 'fa-cloud',
        'rainy': 'fa-cloud-rain',
        'thunderstorm': 'fa-bolt',
        'snowy': 'fa-snowflake',
        'foggy': 'fa-smog'
    };
    return iconMap[iconName] || 'fa-cloud-sun';
}

function createForecastItem(day) {
    const item = document.createElement('div');
    item.className = 'forecast-item';
    
    const dayName = new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' });
    const iconClass = getWeatherIcon(day.icon);
    
    // Add safety checks for undefined values
    const highTemp = day.high !== undefined ? Math.round(day.high) : '--';
    const lowTemp = day.low !== undefined ? Math.round(day.low) : '--';
    const condition = day.condition || 'Unknown';
    
    console.log(`Processing day: ${dayName}, high: ${highTemp}, low: ${lowTemp}, condition: ${condition}, icon: ${day.icon}`);
    
    item.innerHTML = `
        <div class="forecast-day">${dayName}</div>
        <div class="forecast-icon">
            <i class="fas ${iconClass}"></i>
        </div>
        <div class="forecast-temp">
            <span class="forecast-high">${highTemp}°</span>
            <span class="forecast-low">${lowTemp}°</span>
        </div>
        <div class="forecast-desc">${condition}</div>
    `;
    
    return item;
}

function createAlertItem(alert) {
    const item = document.createElement('div');
    item.className = 'alert-item';
    
    item.innerHTML = `
        <div class="alert-header">
            <strong>${alert.event}</strong>
            <span class="alert-time">${formatAlertTime(alert.start)}</span>
        </div>
        <div class="alert-description">${alert.description}</div>
    `;
    
    return item;
}

function formatAlertTime(timeString) {
    const date = new Date(timeString);
    return date.toLocaleString();
}

// Global utility functions
function showError(message) {
    console.error('Error:', message);
    // You could show a toast notification or modal here
    alert(message);
}

function showMessage(message) {
    console.log('Message:', message);
    // You could show a toast notification here
    alert(message);
}

// Chores functions
let chores = [];
let isUpdateMode = false;

function loadChoresData(forceRefresh = false) {
    console.log('Loading chores data', forceRefresh ? '(forced refresh)' : '');
    
    // Check cache first unless forcing refresh
    if (!forceRefresh && tabCache.chores.data) {
        console.log('Using cached chores data');
        chores = tabCache.chores.data;
        displayChores();
        return;
    }
    
    showLoading();
    
    fetch('/chores/api/chores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                chores = data.chores || [];
                
                // Update cache
                tabCache.chores.data = chores;
                tabCache.chores.lastLoaded = Date.now();
                
                displayChores();
            } else {
                showError('Failed to load chores: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error loading chores:', error);
            showError('Error loading chores: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function loadChores() {
    showLoading();
    
    fetch('/chores/api/chores')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                chores = data.chores || [];
                displayChores();
            } else {
                showError('Failed to load chores: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error loading chores:', error);
            showError('Error loading chores: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function syncChores() {
    console.log('Syncing chores from Google Sheets');
    showLoading();
    
    // Show a more specific loading message
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        const loadingText = loadingOverlay.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = 'Syncing chores and downloading icons...';
        }
    }
    
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
    
    fetch('/chores/api/chores/sync', { 
        method: 'POST',
        signal: controller.signal,
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                chores = data.chores || [];
                displayChores();
                const count = chores.length;
                showMessage(`Successfully synced ${count} chores from Google Sheets!`);
            } else {
                showError('Failed to sync chores: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                console.error('Sync request timed out');
                showError('Sync request timed out. Please try again.');
            } else {
                console.error('Error syncing chores:', error);
                showError('Error syncing chores: ' + error.message);
            }
        })
        .finally(() => {
            hideLoading();
        });
}

function resetChores() {
    console.log('Resetting chores completion status');
    showLoading();
    
    fetch('/chores/api/chores/reset', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                chores = data.chores || [];
                displayChores();
                showMessage('Chores reset successfully!');
            } else {
                showError('Failed to reset chores: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error resetting chores:', error);
            showError('Error resetting chores: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

// Helper functions for chore filtering
function getTodayChores() {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const dayNames = ['Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa'];
    const todayName = dayNames[dayOfWeek];
    
    return chores.filter(chore => {
        // Show daily chores
        if (chore.frequency === 'daily') {
            return true;
        }
        // Show weekly chores for today's day of week
        if (chore.frequency === 'weekly' && chore.day_of_week === todayName) {
            return true;
        }
        return false;
    });
}

function getAllChoresSorted() {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const dayNames = ['Su', 'M', 'Tu', 'W', 'Th', 'F', 'Sa'];
    
    // Create a copy of chores and sort them
    const sortedChores = [...chores].sort((a, b) => {
        // First, sort by frequency (daily first, then weekly)
        if (a.frequency !== b.frequency) {
            if (a.frequency === 'daily') return -1;
            if (b.frequency === 'daily') return 1;
        }
        
        // For weekly chores, sort by day of week starting from today
        if (a.frequency === 'weekly' && b.frequency === 'weekly') {
            const aDayIndex = dayNames.indexOf(a.day_of_week);
            const bDayIndex = dayNames.indexOf(b.day_of_week);
            
            // Calculate relative position from today
            const aRelativePos = (aDayIndex - dayOfWeek + 7) % 7;
            const bRelativePos = (bDayIndex - dayOfWeek + 7) % 7;
            
            return aRelativePos - bRelativePos;
        }
        
        // If one is daily and one is weekly, daily comes first
        if (a.frequency === 'daily') return -1;
        if (b.frequency === 'daily') return 1;
        
        return 0;
    });
    
    return sortedChores;
}

function getPeopleOrder() {
    // Get the order of people based on their first appearance in all chores
    const peopleOrder = [];
    const seen = new Set();
    
    chores.forEach(chore => {
        const person = chore.assigned_to || 'Unassigned';
        if (!seen.has(person)) {
            seen.add(person);
            peopleOrder.push(person);
        }
    });
    
    return peopleOrder;
}

function displayChores() {
    const container = document.getElementById('chores-content');
    if (!container) return;
    
    if (chores.length === 0) {
        container.innerHTML = '<div class="no-chores">No chores available. Click "Sync from Sheets" to load chores.</div>';
        return;
    }
    
    // Get the consistent order of people based on first appearance in all chores
    const peopleOrder = getPeopleOrder();
    
    // Check if we should show all chores or filter by today
    const showAllToggle = document.getElementById('show-all-chores');
    const showAll = showAllToggle ? showAllToggle.checked : false;
    
    // Filter chores based on toggle state
    const filteredChores = showAll ? getAllChoresSorted() : getTodayChores();
    
    // Group chores by person
    const choresByPerson = {};
    filteredChores.forEach(chore => {
        const person = chore.assigned_to || 'Unassigned';
        if (!choresByPerson[person]) {
            choresByPerson[person] = [];
        }
        choresByPerson[person].push(chore);
    });
    
    // Create HTML - always show all people in consistent order
    let html = '<div class="chores-grid">';
    peopleOrder.forEach(person => {
        const personChores = choresByPerson[person] || [];
        html += createPersonRow(person, personChores);
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function createPersonRow(person, personChores) {
    let html = `<div class="person-row">
        <div class="person-header">
            <h3>${person}</h3>
        </div>
        <div class="chores-row">`;
    
    personChores.forEach(chore => {
        html += createChoreTile(chore);
    });
    
    html += '</div></div>';
    return html;
}

function createChoreTile(chore) {
    const completedClass = chore.completed ? 'completed' : '';
    
    // Use icon if available, otherwise show default icon
    let iconHtml = '';
    if (chore.icon_name) {
        iconHtml = `<div class="chore-icon">
            <img src="/static/icons/chores/${chore.icon_name}" alt="${chore.name}" 
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
            <div class="chore-icon-fallback" style="display: none;">
                <i class="fas fa-tasks"></i>
            </div>
        </div>`;
    } else {
        iconHtml = `<div class="chore-icon">
            <div class="chore-icon-fallback">
                <i class="fas fa-tasks"></i>
            </div>
        </div>`;
    }
    
    return `
        <div class="chore-tile ${completedClass}" data-chore-id="${chore.id}">
            ${iconHtml}
            <div class="chore-content">
                <div class="chore-name">${chore.name}</div>
            </div>
        </div>
    `;
}

function completeChore(choreId) {
    const chore = chores.find(c => c.id === choreId);
    if (!chore) return;
    
    showLoading();
    
    fetch(`/chores/api/chores/${choreId}/complete`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                chore.completed = !chore.completed;
                displayChores();
            } else {
                showError('Failed to update chore: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error updating chore:', error);
            showError('Error updating chore: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

// Todos functions
let todos = [];

function loadTodosData(forceRefresh = false) {
    console.log('Loading todos data', forceRefresh ? '(forced refresh)' : '');
    
    // Check cache first unless forcing refresh
    if (!forceRefresh && tabCache.todos.data) {
        console.log('Using cached todos data');
        todos = tabCache.todos.data;
        displayTodos();
        return;
    }
    
    showLoading();
    
    fetch('/todos/api/todos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                todos = data.todos || [];
                
                // Update cache
                tabCache.todos.data = todos;
                tabCache.todos.lastLoaded = Date.now();
                
                displayTodos();
            } else {
                showError('Failed to load todos: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error loading todos:', error);
            showError('Error loading todos: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function loadTodos() {
    showLoading();
    
    fetch('/todos/api/todos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                todos = data.todos || [];
                displayTodos();
            } else {
                showError('Failed to load todos: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error loading todos:', error);
            showError('Error loading todos: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function syncTodos() {
    console.log('Syncing todos from Google Sheets');
    showLoading();
    
    fetch('/todos/api/todos/sync', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                todos = data.todos || [];
                displayTodos();
                showMessage('Todos synced successfully!');
            } else {
                showError('Failed to sync todos: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error syncing todos:', error);
            showError('Error syncing todos: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function addTodo() {
    const title = prompt('Enter todo title:');
    if (!title) return;
    
    const priority = prompt('Enter priority (1-10):', '5');
    if (!priority) return;
    
    showLoading();
    
    fetch('/todos/api/todos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: title,
            priority: parseInt(priority),
            completed: false
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            todos.push(data.todo);
            displayTodos();
            showMessage('Todo added successfully!');
        } else {
            showError('Failed to add todo: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error adding todo:', error);
        showError('Error adding todo: ' + error.message);
    })
    .finally(() => {
        hideLoading();
    });
}

function displayTodos() {
    const container = document.getElementById('todos-content');
    if (!container) return;
    
    if (todos.length === 0) {
        container.innerHTML = '<div class="no-todos">No todos available. Click "Sync from Sheets" or "Add Todo" to get started.</div>';
        return;
    }
    
    // Group todos by assigned_to
    const todosByPerson = {};
    todos.forEach(todo => {
        const person = todo.assigned_to || 'Unassigned';
        if (!todosByPerson[person]) {
            todosByPerson[person] = [];
        }
        todosByPerson[person].push(todo);
    });
    
    // Sort todos within each person by priority (highest first)
    Object.keys(todosByPerson).forEach(person => {
        todosByPerson[person].sort((a, b) => b.priority - a.priority);
    });
    
    // Create HTML
    let html = '<div class="todos-grid">';
    Object.keys(todosByPerson).forEach(person => {
        html += createTodoRow(person, todosByPerson[person]);
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function createTodoItem(todo) {
    const completedClass = todo.completed ? 'completed' : '';
    const priorityClass = `priority-${todo.priority}`;
    
    return `
        <div class="todo-item ${completedClass} ${priorityClass}" data-todo-id="${todo.id}">
            <div class="todo-content">
                <div class="todo-title">${todo.title}</div>
                <div class="todo-priority">${todo.priority}</div>
            </div>
        </div>
    `;
}

function createTodoRow(person, personTodos) {
    let html = `<div class="todo-row">
        <div class="todo-header">
            <h3>${person}</h3>
        </div>
        <div class="todos-row">`;
    
    personTodos.forEach(todo => {
        html += createTodoItem(todo);
    });
    
    html += '</div></div>';
    return html;
}

function completeTodo(todoId) {
    const todo = todos.find(t => t.id === todoId);
    if (!todo) return;
    
    showLoading();
    
    fetch(`/todos/api/todos/${todoId}/complete`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                todo.completed = !todo.completed;
                displayTodos();
            } else {
                showError('Failed to update todo: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error updating todo:', error);
            showError('Error updating todo: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

// Calendar functions
let calendarEvents = [];

function loadCalendarData(forceRefresh = false) {
    console.log('Loading calendar data', forceRefresh ? '(forced refresh)' : '');
    
    // Check cache first unless forcing refresh
    if (!forceRefresh && tabCache.calendar.data) {
        console.log('Using cached calendar data');
        calendarEvents = tabCache.calendar.data;
        displayCalendar();
        return;
    }
    
    showLoading();
    
    fetch('/calendar/api/events')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                calendarEvents = data.events || [];
                
                // Update cache
                tabCache.calendar.data = calendarEvents;
                tabCache.calendar.lastLoaded = Date.now();
                
                displayCalendar();
            } else {
                showError('Failed to load calendar: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error loading calendar:', error);
            showError('Error loading calendar: ' + error.message);
        })
        .finally(() => {
            hideLoading();
        });
}

function displayCalendar() {
    const container = document.getElementById('calendar-week');
    if (!container) return;
    
    if (calendarEvents.length === 0) {
        container.innerHTML = '<div class="no-events">No events available. Click "Refresh Calendar" to load events.</div>';
        return;
    }
    
    console.log('Displaying calendar with events:', calendarEvents);
    
    // Group events by day
    const eventsByDay = {};
    calendarEvents.forEach(event => {
        // Handle the Google Calendar API format with start.dateTime
        const startTime = event.start?.dateTime || event.start_time;
        if (startTime) {
            const date = new Date(startTime).toDateString();
            if (!eventsByDay[date]) {
                eventsByDay[date] = [];
            }
            eventsByDay[date].push(event);
        }
    });
    
    console.log('Events grouped by day:', eventsByDay);
    
    // Create calendar HTML with time-based layout
    let html = '<div class="calendar-grid">';
    
    // Get current week dates
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());
    
    for (let i = 0; i < 7; i++) {
        const date = new Date(startOfWeek);
        date.setDate(startOfWeek.getDate() + i);
        const dateString = date.toDateString();
        const dayEvents = eventsByDay[dateString] || [];
        
        console.log(`Day ${dateString}: ${dayEvents.length} events`);
        
        // Sort events by start time for this day
        dayEvents.sort((a, b) => {
            const timeA = new Date(a.start?.dateTime || a.start_time);
            const timeB = new Date(b.start?.dateTime || b.start_time);
            return timeA - timeB;
        });
        
        html += `
            <div class="calendar-day">
                <div class="day-header">
                    <div class="day-name">${date.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                    <div class="day-date">${date.getDate()}</div>
                </div>
                <div class="day-events">
                    ${dayEvents.map(event => createEventItem(event)).join('')}
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function createEventItem(event) {
    // Handle Google Calendar API format
    const startTime = event.start?.dateTime || event.start_time;
    const endTime = event.end?.dateTime || event.end_time;
    const title = event.summary || event.title || 'Untitled Event';
    const description = event.description || '';
    const calendarName = event.calendar_name || 'Unknown Calendar';
    
    const startTimeStr = new Date(startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    const endTimeStr = new Date(endTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    // Calculate duration for better visual representation
    const start = new Date(startTime);
    const end = new Date(endTime);
    const duration = (end - start) / (1000 * 60); // duration in minutes
    
    // Add magenta styling for natalee's calendar
    const isNataleeCalendar = calendarName.toLowerCase().includes('natalee');
    const eventClass = isNataleeCalendar ? 'calendar-event natalee-event' : 'calendar-event';
    
    return `
        <div class="${eventClass}" data-duration="${duration}">
            <div class="event-time">${startTimeStr} - ${endTimeStr}</div>
            <div class="event-title">${title}</div>
            <div class="event-calendar">${calendarName}</div>
            ${description ? `<div class="event-description">${description}</div>` : ''}
        </div>
    `;
}

// Theme Toggle Functions
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Load saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Add click event listener
    themeToggle.addEventListener('click', toggleTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
    }
}

// Hold-to-complete functionality
class HoldToComplete {
    constructor(buttonSelector, targetSelector, options = {}) {
        this.button = document.querySelector(buttonSelector);
        this.targets = document.querySelectorAll(targetSelector);
        this.options = {
            activeColor: '#2196F3',
            ...options
        };
        
        this.isHolding = false;
        
        this.init();
    }
    
    init() {
        if (!this.button) return;
        
        // Add event listeners
        this.button.addEventListener('mousedown', this.startHold.bind(this));
        this.button.addEventListener('mouseup', this.endHold.bind(this));
        this.button.addEventListener('mouseleave', this.endHold.bind(this));
        
        // Touch events for mobile
        this.button.addEventListener('touchstart', this.startHold.bind(this));
        this.button.addEventListener('touchend', this.endHold.bind(this));
        this.button.addEventListener('touchcancel', this.endHold.bind(this));
        
        // Prevent context menu on long press
        this.button.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    startHold(e) {
        e.preventDefault();
        
        if (this.isHolding) return;
        
        this.isHolding = true;
        
        // Visual feedback - button becomes active
        this.button.classList.add('holding');
        this.button.style.backgroundColor = this.options.activeColor;
        
        // Enable targets for completion
        this.updateTargets(true);
        
        console.log('Hold mode activated - you can now tap items to complete them');
    }
    
    endHold(e) {
        e.preventDefault();
        
        if (!this.isHolding) return;
        
        this.isHolding = false;
        
        // Visual feedback - button returns to normal
        this.button.classList.remove('holding');
        this.button.style.backgroundColor = '';
        
        // Disable targets for completion
        this.updateTargets(false);
        
        console.log('Hold mode deactivated - tapping items will no longer complete them');
    }
    
    updateTargets(enable) {
        this.targets.forEach(target => {
            if (enable) {
                target.classList.add('update-mode');
                target.style.cursor = 'pointer';
                target.style.opacity = '0.8';
            } else {
                target.classList.remove('update-mode');
                target.style.cursor = '';
                target.style.opacity = '';
            }
        });
    }
    
    // Method to update targets when new content is loaded
    updateTargetList() {
        this.targets = document.querySelectorAll(this.options.targetSelector || '.chore-tile, .todo-item');
        this.updateTargets(this.isHolding);
    }
}

// Initialize hold-to-complete for chores
function initializeChoresHoldToComplete() {
    const choresHoldToComplete = new HoldToComplete(
        '#hold-button',
        '.chore-tile',
        {
            activeColor: '#4CAF50'
        }
    );
    
    // Handle completion
    document.addEventListener('holdComplete', function(e) {
        console.log('Hold to complete activated for chores');
    });
}

// Initialize hold-to-complete for todos
function initializeTodosHoldToComplete() {
    const todosHoldToComplete = new HoldToComplete(
        '#hold-button',
        '.todo-item',
        {
            activeColor: '#4CAF50'
        }
    );
    
    // Handle completion
    document.addEventListener('holdComplete', function(e) {
        console.log('Hold to complete activated for todos');
    });
}

