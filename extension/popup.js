document.getElementById('execute-btn').addEventListener('click', executeCommand);
document.getElementById('command-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeCommand();
});

async function executeCommand() {
    const command = document.getElementById('command-input').value;
    const statusDiv = document.getElementById('status');

    if (!command) return;

    // Show loading status
    statusDiv.textContent = 'Processing...';
    statusDiv.className = '';
    statusDiv.style.display = 'block';

    try {
        // Send command to your Python server
        const response = await fetch('http://localhost:3001/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command })
        });

        const result = await response.json();

        if (result.success) {
            statusDiv.textContent = result.message;
            statusDiv.className = 'success';
        } else {
            statusDiv.textContent = 'Error: ' + result.message;
            statusDiv.className = 'error';
        }
    } catch (error) {
        statusDiv.textContent = 'Failed to connect to agent server';
        statusDiv.className = 'error';
    }
}