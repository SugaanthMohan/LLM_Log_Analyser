// Tab Switching Logic
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(btn => 
            btn.classList.remove('active'));
        button.classList.add('active');
    });
});

// Form Submission Handler
document.getElementById('logConfigForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading state
    const logOutput = document.getElementById('logOutput');
    logOutput.textContent = "Analyzing logs...";
    
    // Simulated API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Update with sample response
    logOutput.textContent = 
        `[SIMULATED RESPONSE]\nFound 12 errors in specified timeframe\n` +
        `Matching happy path logs detected in 3 instances\n` +
        `Recommended resolution: Check database connection pool settings`;
});

// Add hover effect to buttons
document.querySelectorAll('.btn-primary').forEach(button => {
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-2px)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
    });
});