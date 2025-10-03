// Hold-to-complete functionality - Mode Toggle Style
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

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize based on current page
    if (document.querySelector('.chores-container')) {
        initializeChoresHoldToComplete();
    }
    
    if (document.querySelector('.todos-container')) {
        initializeTodosHoldToComplete();
    }
});