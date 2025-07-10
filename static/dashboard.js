document.addEventListener('DOMContentLoaded', () => {
    const menuPanel = document.getElementById('menuPanel');
    const menuOverlay = document.getElementById('menuOverlay');
    const menuToggle = document.getElementById('menuToggle');
    const accountBtn = document.getElementById('accountBtn');
    const accountPanel = document.getElementById('accountPanel');
    const aiBtn = document.getElementById('ai-btn');
    const chatBox = document.getElementById('chat-box');
    const chatInput = chatBox.querySelector('.chat-input');
    const chatBody = document.getElementById('chat-body');
    const addDeviceBtn = document.getElementById('add-device-btn');
    const deviceModal = document.getElementById('deviceModal');
    const deviceOverlay = document.getElementById('deviceOverlay');
    const closeDeviceModal = document.getElementById('closeDeviceModal');
    const cancelDeviceBtn = document.getElementById('cancelDeviceBtn');
    const saveDeviceBtn = document.getElementById('saveDeviceBtn');
    const deviceInput = document.getElementById('deviceInput');
    const deviceList = document.getElementById('device-list');

    // Menu Panel Toggle
    menuToggle.onclick = () => {
        menuPanel.classList.toggle('active');
        menuOverlay.classList.toggle('active');
    };
    menuOverlay.onclick = () => {
        menuPanel.classList.remove('active');
        menuOverlay.classList.remove('active');
    };
    menuPanel.querySelectorAll('li').forEach(item => {
        item.onclick = () => {
            menuPanel.classList.remove('active');
            menuOverlay.classList.remove('active');
        };
    });

    // Account Panel Toggle
    accountBtn.onclick = () => {
        accountPanel.classList.toggle('active');
    };

    // AI Assistant Chatbox Toggle
    aiBtn.onclick = () => {
        chatBox.classList.toggle('active');
    };

    // Handle Chat Input
    window.handleChat = async e => {
        if (e.key === 'Enter') {
            const msg = chatInput.value.trim();
            if (msg) {
                chatBody.innerHTML += `<p><strong>You:</strong> ${msg}</p>`;
                chatBody.innerHTML += `<p><strong>AI:</strong> Sure! 🌱 ...</p>`;
                chatBody.scrollTop = chatBody.scrollHeight;
                chatInput.value = '';

            try {
                const response = await fetch('/chat_with_gemini', { // New endpoint
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: msg })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                chatBody.innerHTML += `<p><strong>AI:</strong> ${data.gemini_response}</p>`; // Display Gemini's response
                chatBody.scrollTop = chatBody.scrollHeight;

            } 
            catch (error) {
                console.error('Error communicating with AI:', error);
                chatBody.innerHTML += `<p><strong>AI:</strong> Sorry, I'm having trouble connecting right now. Please try again later.</p>`;
                chatBody.scrollTop = chatBody.scrollHeight;
            }
            }
        }
    };

    // Device Modal Functions
    const closeDModal = () => {
        deviceModal.classList.remove('active');
        deviceOverlay.classList.remove('active');
        deviceInput.value = ''; // Clear input on close
    };

    addDeviceBtn.onclick = () => {
        deviceModal.classList.add('active');
        deviceOverlay.classList.add('active');
    };
    closeDeviceModal.onclick = closeDModal;
    cancelDeviceBtn.onclick = closeDModal;
    deviceOverlay.onclick = closeDModal;

    // Add New Device
    saveDeviceBtn.onclick = () => {
        const name = deviceInput.value.trim();
        if (name) {
            const li = document.createElement('li');
            li.dataset.electric = "[5,5,5,5,5,5,5]"; // Default data for new devices
            li.dataset.water = "[5,5,5,5,5,5,5]";   // Default data for new devices
            li.innerHTML = `🔌 ${name} <button class="remove-btn">🗑️</button>`;
            deviceList.appendChild(li);
            closeDModal();
        } else {
            alert("Please enter a device name!");
        }
    };

    // Remove Device and Update Charts
    deviceList.addEventListener('click', e => {
        if (e.target.classList.contains('remove-btn')) {
            e.target.closest('li').remove();
        } else if (e.target.tagName === 'LI' || e.target.parentElement.tagName === 'LI') {
            const li = e.target.tagName === 'LI' ? e.target : e.target.parentElement;
            const eData = JSON.parse(li.dataset.electric);
            const wData = JSON.parse(li.dataset.water);
            electricChart.data.datasets[0].data = eData;
            waterChart.data.datasets[0].data = wData;
            electricChart.update();
            waterChart.update();
        }
    });

    // Chart Initialization
    const electricChart = new Chart(document.getElementById('electricChart'), {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'kWh',
                data: [0, 0, 0, 0, 0, 0, 0], // Initial data
                borderColor: '#388e3c',
                backgroundColor: 'rgba(56,142,60,0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true
        }
    });

    const waterChart = new Chart(document.getElementById('waterChart'), {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Liters',
                data: [0, 0, 0, 0, 0, 0, 0], // Initial data
                backgroundColor: '#66bb6a'
            }]
        },
        options: {
            responsive: true
        }
    });

    // You might want to load initial chart data here, e.g., by simulating a click
    // on the first device in the list or fetching data from the server.
});
