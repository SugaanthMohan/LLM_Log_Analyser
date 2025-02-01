// Get the forms and button elements
const splunkLoginForm = document.getElementById('SplunkLoginForm');
const logConfigForm = document.getElementById('logConfigForm');
const logConfigForm_source_type = document.getElementById('source-type');
const logConfigForm_start_time = document.getElementById('start-time');
const logConfigForm_end_time = document.getElementById('end-time');
const logConfigForm_application_name = document.getElementById('application-name');
const logConfigForm_input_query = document.getElementById('input-query');


// Get Test Connection Button
const testConnectionButton = document.getElementById('testConnectionButton');

// Analyze Logs Button
const analyzeLogsButton = document.getElementById('analyze-logs-button');

// Get the tab buttons
const rawLogsTabButton = document.getElementById('rawLogs-tab-button');
const AiAnalysisTabButton = document.getElementById('AIAnalysis-tab-button');
const happyPathTabButton = document.getElementById('happyPath-tab-button');


// DISABLE LOG CONFIG FORM ELEMENTS
logConfigForm.classList.add('disabled-form');
logConfigForm_source_type.disabled = true;
logConfigForm_start_time.disabled = true;
logConfigForm_end_time.disabled = true;
logConfigForm_application_name.disabled = true;
logConfigForm_input_query.disabled = true;
analyzeLogsButton.disabled = true;
analyzeLogsButton.style.background = 'grey';
analyzeLogsButton.style.cursor = 'not-allowed';




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

    // DISABLE THE BUTTON AND ACTIONS
    analyzeLogsButton.disabled = true;
    analyzeLogsButton.style.cursor = 'not-allowed';
    analyzeLogsButton.style.background = 'grey';

    // Show loading state
    const logOutput = document.getElementById('logOutput');
    logOutput.textContent = "Analyzing logs...";

    // Get the values from the form elements
    const sourceType = logConfigForm_source_type.value;
    const startTime = logConfigForm_start_time.value;
    const endTime = logConfigForm_end_time.value;
    const applicationName = logConfigForm_application_name.value;
    const query = logConfigForm_input_query.value;

    // Create a JSON payload with the values
    const payload = {
        source_type: sourceType,
        start_time: startTime,
        end_time: endTime,
        application_name: applicationName,
        query: query
    };

    // Scroll down to the lower end of the page
    window.scrollTo(0, document.body.scrollHeight);

    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';
    spinner.style.position = 'absolute';
    spinner.style.top = '50%';
    spinner.style.left = '50%';
    spinner.style.transform = 'translate(-50%, -50%)';
    spinner.style.fontSize = '36px'; // Increase font size
    spinner.style.color = '#fff'; // Change color to white
    spinner.style.zIndex = '1000'; // Increase z-index
    analyzeLogsButton.appendChild(spinner);

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

    spinner.remove();

    // ENABLE THE BUTTON AND ACTIONS
    analyzeLogsButton.disabled = false;
    analyzeLogsButton.style.background = '#D32F2F';
    analyzeLogsButton.style.cursor = 'pointer';


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
            logConfigForm_source_type.disabled = false;
            logConfigForm_start_time.disabled = false;
            logConfigForm_end_time.disabled = false;
            logConfigForm_application_name.disabled = false;
            logConfigForm_input_query.disabled = false;
            analyzeLogsButton.disabled = false;
            analyzeLogsButton.style.background = '#D32F2F';
            analyzeLogsButton.style.cursor = 'pointer';


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