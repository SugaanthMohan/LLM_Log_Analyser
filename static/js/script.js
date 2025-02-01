// Get the forms and button elements
const splunkLoginForm = document.getElementById('SplunkLoginForm');
const logConfigForm = document.getElementById('logConfigForm');
const testConnectionButton = document.getElementById('testConnectionButton');
logConfigForm.classList.add('disabled-form');


// Add an event listener to the testConnectionButton
testConnectionButton.addEventListener('click', () => {
    // Simulate a connection test (replace with actual connection test code)
    const isConnected = true; // Replace with actual connection test result

    const promptElement = document.createElement('div');


    if (isConnected) {
         // Create a prompt element

        // Connection Successful
        promptElement.textContent = 'Connection successful!';
        promptElement.style.color = 'green';

        logConfigForm.classList.remove('disabled-form');

    } else {

        logConfigForm.classList.add('disabled-form');

        promptElement.textContent = 'Connection failed. Please try again.';
        promptElement.style.color = 'red';

    }

    promptElement.style.fontSize = '14px';
    promptElement.style.fontWeight = 'bold';
    promptElement.style.marginBottom = '10px';

    // Insert the prompt element above the test connection button
    testConnectionButton.parentNode.insertBefore(promptElement, testConnectionButton);

    // Make the prompt disappear after 3 seconds
    setTimeout(() => {
        promptElement.remove();
    }, 3000);


});


// Add an event listener to the testConnectionButton
testConnectionButton.addEventListener('click', () => {
    // Simulate a connection test (replace with actual connection test code)
    const isConnected = true; // Replace with actual connection test result

    if (isConnected) {
        // Enable the logConfigForm if the connection is successful
        logConfigForm.disabled = false;
    } else {
        // Keep the logConfigForm disabled if the connection fails
        logConfigForm.disabled = true;
    }
});

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