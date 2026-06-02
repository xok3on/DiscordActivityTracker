const LOCAL_TRACKER_URL = 'http://127.0.0.1:53241/api/tab-update';

async function syncActiveTab() {
    try {
        let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab || !tab.url) return;
        
        if (tab.url.startsWith('chrome://') || tab.url.startsWith('about:')) return;

        let payload = {
            version: "1.0",
            action: "active_tab_sync",
            data: {
                browser: navigator.userAgentData ? navigator.userAgentData.brands[0].brand : "Chromium",
                url: tab.url,
                title: tab.title,
                has_audio: tab.audible || false
            },
            timestamp: Date.now()
        };

        await fetch(LOCAL_TRACKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (err) {}
}

chrome.tabs.onActivated.addListener(syncActiveTab);
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete') syncActiveTab();
});

setInterval(async () => {
    try {
        await fetch(LOCAL_TRACKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ version: "1.0", action: "ping" })
        });
    } catch(e){}
}, 30000);
