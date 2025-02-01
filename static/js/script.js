// Get the forms and button elements
const splunkLoginForm = document.getElementById('SplunkLoginForm');
const logConfigForm = document.getElementById('logConfigForm');

// Get Test Connection Button
const testConnectionButton = document.getElementById('testConnectionButton');

// Analyze Logs Button
const analyzeLogsButton = document.getElementById('analyze-logs-button');

// Get the tab buttons
const rawLogsTabButton = document.getElementById('rawLogs-tab-button');
const AiAnalysisTabButton = document.getElementById('AIAnalysis-tab-button');
const happyPathTabButton = document.getElementById('happyPath-tab-button');


// Get the Analyze Logs button
logConfigForm.classList.add('disabled-form');



// Create an object to store the results-tab-data fetched data
const resultsTabData = {
    "RawLogs": "",
    "AIAnalysis": "",
    "HappyPath": ""
};


// Add an event listener to the Analyze Logs button
analyzeLogsButton.addEventListener('click', async() => {

    // PREVENT DOM RELOAD ACTION
    event.preventDefault()

    // Show loading state
    const logOutput = document.getElementById('logOutput');
    logOutput.textContent = "Analyzing logs...";

    // Get the values from the form elements
    const sourceType = document.getElementById('source-type').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
    const applicationName = document.getElementById('application-name').value;
    const query = document.getElementById('input-query').value;

    // Create a JSON payload with the values
    const payload = {
        source_type: sourceType,
        start_time: startTime,
        end_time: endTime,
        application_name: applicationName,
        query: query
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
    .then(data => {

        // Store the fetched data in the resultsData object
        resultsTabData.RawLogs = data.RawLogs;
        resultsTabData.AIAnalysis = data.AIAnalysis;
        resultsTabData.HappyPath = data.HappyPath;

        // Set Active & Load the RawLogs tab content by default
        rawLogsTabButton.classList.add('active');
        loadTabContent('RawLogs');

    })
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
            testConnectionButton.style.background = 'grey';
            testConnectionButton.style.color = 'white';
            testConnectionButton.style.cursor = 'not-allowed';
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


// Tab Switching Logic
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-button').forEach(btn => 
            btn.classList.remove('active'));
        button.classList.add('active');
    });
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


// Add event listeners to the tab buttons
rawLogsTabButton.addEventListener('click', () => {
    loadTabContent('RawLogs');
});

AiAnalysisTabButton.addEventListener('click', () => {
    loadTabContent('AIAnalysis');
});

happyPathTabButton.addEventListener('click', () => {
    loadTabContent('HappyPath');
});

// Function to load the tab content
function loadTabContent(tabName) {
    const tabContentElement = document.getElementById('logOutput');

    // Load the content from the resultsData object
    if (tabName === 'RawLogs') {
        tabContentElement.innerHTML = resultsTabData.RawLogs;
    } else if (tabName === 'AIAnalysis') {
        tabContentElement.innerHTML = resultsTabData.AIAnalysis;
    } else if (tabName === 'HappyPath') {
        tabContentElement.innerHTML = resultsTabData.HappyPath;
    }
}