// Get the forms and button elements
const splunkLoginForm = document.getElementById('SplunkLoginForm');
const logConfigForm = document.getElementById('logConfigForm');

// Get Test Connection Button
const testConnectionButton = document.getElementById('testConnectionButton');

const analyzeLogsButton = document.getElementById('analyze-logs-button');

// Get the Analyze Logs button
logConfigForm.classList.add('disabled-form');


// Add an event listener to the Analyze Logs button
analyzeLogsButton.addEventListener('click', () => {

    // Get the values from the form elements
    const sourceType = document.getElementById('source-type').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
    const applicationName = document.getElementById('application-name').value;
    const logLevelFilter = document.getElementById('log-level-filter').value;

    // Create a JSON payload with the values
    const payload = {
        source_type: sourceType,
        start_time: startTime,
        end_time: endTime,
        application_name: applicationName,
        log_level_filter: logLevelFilter
    };

    // Send the payload to the Flask endpoint using the Fetch API
    fetch('/AnalyzeLogs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
});


// Add an event listener to the testConnectionButton
testConnectionButton.addEventListener('click', () => {

    // Simulate a connection test (replace with actual connection test code)
    const isConnected = true; // Replace with actual connection test result

    // Get the values from the form elements
    const host = document.getElementById('splunk-host').value;
    const port = document.getElementById('splunk-port').value;
    const user = document.getElementById('splunk-user').value;
    const token = document.getElementById('splunk-token').value;

    // Create a JSON payload with the values
    const payload = {
        host: host,
        port: port,
        user: user,
        token: token
    };

    // Send the payload to the Flask endpoint using the Fetch API
    fetch('/TestConnection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        // Check the status of the connection
        if (data.connection) {
            // Connection successful
            const promptElement = document.createElement('div');
            promptElement.textContent = 'Connection successful!';
            promptElement.style.color = 'green';
            promptElement.style.fontSize = '14px';
            promptElement.style.fontWeight = 'bold';
            promptElement.style.marginBottom = '10px';

            // Insert the prompt element above the test connection button
            testConnectionButton.parentNode.insertBefore(promptElement, testConnectionButton);

            // Disable the SplunkLoginForm
            testConnectionButton.disabled = true;
            document.getElementById('splunk-host').disabled = true;
            document.getElementById('splunk-port').disabled = true;
            document.getElementById('splunk-user').disabled = true;
            document.getElementById('splunk-token').disabled = true;


            // Enable the logConfigForm
            logConfigForm.classList.remove('disabled-form');

            // Make the prompt disappear after 3 seconds
            setTimeout(() => {
                promptElement.remove();
            }, 3000);

        } else {
            // Connection failed
            const promptElement = document.createElement('div');
            promptElement.textContent = 'Connection failed. Please try again.';
            promptElement.style.color = 'red';
            promptElement.style.fontSize = '14px';
            promptElement.style.fontWeight = 'bold';
            promptElement.style.marginBottom = '10px';

            // Insert the prompt element above the test connection button
            testConnectionButton.parentNode.insertBefore(promptElement, testConnectionButton);

            // Make the prompt disappear after 3 seconds
            setTimeout(() => {
                promptElement.remove();
            }, 3000);
        }
    }).catch(error => console.error(error));
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