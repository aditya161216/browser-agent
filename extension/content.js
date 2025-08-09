// This runs on every page and can receive commands from the extension
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageInfo') {
        sendResponse({
            title: document.title,
            url: window.location.href,
            text: document.body.innerText.substring(0, 1000)
        });
    }
});