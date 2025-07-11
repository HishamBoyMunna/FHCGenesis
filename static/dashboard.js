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
    
    // CORRECTED: The ID in the HTML is 'deviceName', not 'deviceInput'
    const deviceNameInput = document.getElementById('deviceName');
    const resourceTypeSelect = document.getElementById('resourceType');
    const deviceList = document.getElementById('device-list');

    // Usage Edit Modal Elements
    const usageModal = document.getElementById('usageModal');
    const usageOverlay = document.getElementById('usageOverlay');
    const closeUsageModal = document.getElementById('closeUsageModal');
    const cancelUsageBtn = document.getElementById('cancelUsageBtn');
    const saveUsageBtn = document.getElementById('saveUsageBtn');
    const editDeviceName = document.getElementById('editDeviceName');
    const editDeviceType = document.getElementById('editDeviceType');
    const editDeviceRating = document.getElementById('editDeviceRating');
    const editDeviceUnit = document.getElementById('editDeviceUnit');
    const usageDateInput = document.getElementById('usage-date');
    const usageHoursInput = document.getElementById('usage-hours');
    const usageHistoryDiv = document.getElementById('usageHistory');
    const deviceRatingInput = document.getElementById('deviceRating');
    const ratingUnitSpan = document.getElementById('ratingUnit');
    const insightsBtn = document.getElementById('insightsBtn');
    const closeChatBtn = document.getElementById('closeChat');
    let currentEditDeviceId = null;

    const electricChart = new Chart(document.getElementById('electricChart'), {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'kWh',
                data: [0, 0, 0, 0, 0, 0, 0],
                borderColor: '#388e3c',
                backgroundColor: 'rgba(56,142,60,0.2)',
                fill: true,
                tension: 0.3
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Electricity Usage (kWh)'
                }
            }
        }
    });

    const waterChart = new Chart(document.getElementById('waterChart'), {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Liters',
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: '#66bb6a'
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Water Usage (L)'
                }
            }
        }
    });

    const wasteChart = new Chart(document.getElementById('wasteChart'), {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Kilograms',
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: '#b08d57'
            }]
        },
        options: { 
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Waste Production (Kg)'
                }
            }
        }
    });

    function renderDeviceToUI(device) {
        const li = document.createElement('li');
        li.dataset.deviceId = device.id; // Store database ID
        li.dataset.type = device.type;
        li.dataset.rating = device.rating;
        li.dataset.unit = device.unit;

        let icon = '';
        switch (device.type) {
            case 'electric': icon = '🔌'; break;
            case 'water': icon = '💧'; break;
            case 'waste': icon = '🗑️'; break;
            default: icon = '❓';
        }

        li.innerHTML = `${icon} <span class="device-name">${device.name} (${device.rating} ${device.unit})</span> <button class="remove-btn">🗑️</button>`;
        deviceList.appendChild(li);
    }

    async function loadUserDevices() {
        try {
            const response = await fetch('/api/devices', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to load devices.');
            }

            const devices = await response.json();
            deviceList.innerHTML = ''; // Clear existing devices before rendering
            devices.forEach(renderDeviceToUI);
        } catch (error) {
            console.error('Error loading user devices:', error);
            deviceList.innerHTML = '<li><p>Failed to load devices. Please try again.</p></li>';
        }
    }

    // Load devices when the page loads
    loadUserDevices();

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
        accountBtn.classList.toggle('active');
    };

    // AI Assistant Chatbox Toggle
    aiBtn.onclick = () => {
        chatBox.classList.toggle('active');
        // Remove expanded class for regular chat
        chatBox.classList.remove('expanded');
        if (chatBox.classList.contains('active')) {
            chatInput.focus();
        }
    };

    // Close Chat Button
    closeChatBtn.onclick = () => {
        chatBox.classList.remove('active', 'expanded');
    };

    // Insights Button
    insightsBtn.onclick = async () => {
        insightsBtn.disabled = true;
        insightsBtn.textContent = '🤔 Analyzing...';
        
        try {
            const response = await fetch('/api/insights');
            const data = await response.json();
            
            if (data.success) {
                // Open the chatbot and expand it for insights
                chatBox.classList.add('active', 'expanded');
                chatInput.focus();
                
                // Add the insights as a system message
                const systemMsgElement = document.createElement('p');
                systemMsgElement.innerHTML = '<strong>System:</strong> Analyzing your device usage data...';
                chatBody.appendChild(systemMsgElement);
                
                // Add the insights as a buddy message
                const buddyMsgElement = document.createElement('p');
                buddyMsgElement.innerHTML = `<strong>Buddy:</strong> Here's my analysis of your resource usage:<br><br>${data.insights.replace(/\n/g, '<br>')}`;
                chatBody.appendChild(buddyMsgElement);
                chatBody.scrollTop = chatBody.scrollHeight;
                
                // Add a follow-up message
                const followUpElement = document.createElement('p');
                followUpElement.innerHTML = '<strong>Buddy:</strong> Would you like me to explain any of these recommendations in more detail or help you implement them?';
                chatBody.appendChild(followUpElement);
                chatBody.scrollTop = chatBody.scrollHeight;
                
            } else {
                alert('Failed to generate insights: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error getting insights:', error);
            alert('Failed to generate insights. Please try again.');
        } finally {
            insightsBtn.disabled = false;
            insightsBtn.textContent = '💡 Get Insights';
        }
    };

    // Handle Chat Input
    window.handleChat = async e => {
        if (e.key === 'Enter') {
            const msg = chatInput.value.trim();
            if (msg) {
                const userMsgElement = document.createElement('p');
                userMsgElement.innerHTML = `<strong>You:</strong> ${msg}`;
                chatBody.appendChild(userMsgElement);
                
                chatInput.value = '';
                
                const loadingMessage = document.createElement('p');
                loadingMessage.innerHTML = '<strong>Buddy:</strong> Typing...';
                chatBody.appendChild(loadingMessage);
                chatBody.scrollTop = chatBody.scrollHeight;

                try {
                    // Check if the message is asking for data analysis
                    const analysisKeywords = ['analyze', 'analysis', 'data', 'usage', 'devices', 'insights', 'recommendations'];
                    const isAnalysisRequest = analysisKeywords.some(keyword => 
                        msg.toLowerCase().includes(keyword)
                    );

                    let response;
                    if (isAnalysisRequest) {
                        // Get insights from our analysis system
                        const insightsResponse = await fetch('/api/insights');
                        const insightsData = await insightsResponse.json();
                        
                        if (insightsData.success) {
                            // Expand chat for analysis
                            chatBox.classList.add('expanded');
                            
                            loadingMessage.remove();
                            const buddyMsgElement = document.createElement('p');
                            buddyMsgElement.innerHTML = `<strong>Buddy:</strong> Here's my analysis of your device usage:<br><br>${insightsData.insights.replace(/\n/g, '<br>')}`;
                            chatBody.appendChild(buddyMsgElement);
                            chatBody.scrollTop = chatBody.scrollHeight;
                        } else {
                            throw new Error(insightsData.error || 'Failed to analyze data');
                        }
                    } else {
                        // Regular Gemini chat
                        response = await fetch('/chat_with_gemini', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: msg })
                        });
                        
                        loadingMessage.remove();

                        if (!response.ok) {
                            const errorData = await response.json();
                            throw new Error(errorData.gemini_response || `HTTP error! status: ${response.status}`);
                        }

                        const data = await response.json();
                        const buddyMsgElement = document.createElement('p');
                        buddyMsgElement.innerHTML = `<strong>Buddy:</strong> ${data.gemini_response}`;
                        chatBody.appendChild(buddyMsgElement);
                        chatBody.scrollTop = chatBody.scrollHeight;
                    }

                } catch (error) {
                    console.error('Error communicating with Buddy:', error);
                    if (loadingMessage) { loadingMessage.remove(); }
                    const errorMsgElement = document.createElement('p');
                    errorMsgElement.innerHTML = `<strong>Buddy:</strong> Sorry, I couldn't get a response. ${error.message || 'Please try again later.'}`;
                    chatBody.appendChild(errorMsgElement);
                    chatBody.scrollTop = chatBody.scrollHeight;
                }
            }
        }
    };

    // Device Modal Functions
    const closeDModal = () => {
        deviceModal.classList.remove('active');
        deviceOverlay.classList.remove('active');
        // Clear the correct input field.
        deviceNameInput.value = ''; 
        resourceTypeSelect.value = '';
        deviceRatingInput.value = '';
        ratingUnitSpan.textContent = 'Unit will be set based on resource type';
    };

    addDeviceBtn.onclick = () => {
        deviceModal.classList.add('active');
        deviceOverlay.classList.add('active');
    };
    closeDeviceModal.onclick = closeDModal;
    cancelDeviceBtn.onclick = closeDModal;
    deviceOverlay.onclick = closeDModal;

    // Usage Modal Functions
    const closeUsageModalFunc = () => {
        usageModal.classList.remove('active');
        usageOverlay.classList.remove('active');
        currentEditDeviceId = null;
        // Clear all usage inputs
        usageDateInput.value = '';
        usageHoursInput.value = '';
        usageHistoryDiv.innerHTML = ''; // Clear usage history
        deviceRatingInput.value = '';
        ratingUnitSpan.textContent = '';
    };

    const openUsageModal = async (device) => {
        currentEditDeviceId = device.id;
        editDeviceName.textContent = device.name;
        editDeviceType.textContent = device.type;
        editDeviceRating.textContent = device.rating;
        
        // Set unit based on device type
        let unit = '';
        switch (device.type) {
            case 'electric': unit = 'kWh'; break;
            case 'water': unit = 'L'; break;
            case 'waste': unit = 'Kg'; break;
            default: unit = 'units';
        }
        editDeviceUnit.textContent = unit;

        // Set today's date as default
        const today = new Date().toISOString().split('T')[0];
        usageDateInput.value = today;
        usageHoursInput.value = '';

        // Fetch usage history for this device
        try {
            const response = await fetch(`/api/devices/${device.id}/usage`);
            if (response.ok) {
                const data = await response.json();
                displayUsageHistory(data.usage_data, unit);
            }
        } catch (error) {
            console.error('Error fetching usage history:', error);
        }

        usageModal.classList.add('active');
        usageOverlay.classList.add('active');
    };

    const displayUsageHistory = (usageData, unit) => {
        usageHistoryDiv.innerHTML = '';
        
        // Convert usage data to array and sort by date
        const usageEntries = Object.entries(usageData)
            .map(([date, hours]) => ({ date, hours }))
            .sort((a, b) => new Date(b.date) - new Date(a.date));

        if (usageEntries.length === 0) {
            usageHistoryDiv.innerHTML = '<p>No usage data available</p>';
            return;
        }

        usageEntries.forEach(entry => {
            const usageEntryDiv = document.createElement('div');
            usageEntryDiv.classList.add('usage-entry');
            const usageValue = (parseFloat(entry.hours) * parseFloat(editDeviceRating.textContent)).toFixed(2);
            usageEntryDiv.innerHTML = `
                <div class="usage-entry-content">
                    <span><strong>${entry.date}</strong></span>
                    <span>${entry.hours} hours</span>
                    <span>${usageValue} ${unit}</span>
                </div>
            `;
            usageHistoryDiv.appendChild(usageEntryDiv);
        });
    };

    closeUsageModal.onclick = closeUsageModalFunc;
    cancelUsageBtn.onclick = closeUsageModalFunc;
    usageOverlay.onclick = closeUsageModalFunc;

    // Update rating unit when resource type changes
    resourceTypeSelect.addEventListener('change', () => {
        const selectedType = resourceTypeSelect.value;
        let unit = '';
        switch (selectedType) {
            case 'electric': unit = 'kW'; break;
            case 'water': unit = 'L/min'; break;
            case 'waste': unit = 'kg/day'; break;
            default: unit = 'units';
        }
        ratingUnitSpan.textContent = unit;
    });

    // Save usage data
    saveUsageBtn.onclick = async () => {
        if (!currentEditDeviceId) return;

        const usageDate = usageDateInput.value;
        const usageHours = parseFloat(usageHoursInput.value) || 0;

        if (!usageDate || usageHours === 0) {
            alert("Please enter a valid date and usage hours.");
            return;
        }

        try {
            const response = await fetch(`/api/devices/${currentEditDeviceId}/usage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: usageDate,
                    hours_used: usageHours
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to add usage data.');
            }

            const result = await response.json();
            
            // Refresh usage history
            const device = {
                id: currentEditDeviceId,
                name: editDeviceName.textContent,
                type: editDeviceType.textContent,
                rating: editDeviceRating.textContent
            };
            
            // Clear inputs
            usageDateInput.value = '';
            usageHoursInput.value = '';
            
            // Refresh the usage history display
            const historyResponse = await fetch(`/api/devices/${currentEditDeviceId}/usage`);
            if (historyResponse.ok) {
                const data = await historyResponse.json();
                const unit = editDeviceUnit.textContent;
                displayUsageHistory(data.usage_data, unit);
            }

            alert('Usage data added successfully!');

        } catch (error) {
            console.error('Error adding usage data:', error);
            alert(`Could not add usage data: ${error.message}`);
        }
    };

    // --- REVISED: Add New Device with Fetch to Backend ---
    saveDeviceBtn.onclick = async () => {
        const resourceType = resourceTypeSelect.value;
        const deviceName = deviceNameInput.value.trim();
        const deviceRating = parseFloat(deviceRatingInput.value) || 0;

        if (!resourceType) {
            alert("Please select a resource type!");
            return;
        }
        if (!deviceName) {
            alert("Please enter a device name!");
            return;
        }
        if (deviceRating <= 0) {
            alert("Please enter a valid device rating!");
            return;
        }

        // Set unit based on resource type
        let unit = '';
        switch (resourceType) {
            case 'electric': unit = 'kW'; break;
            case 'water': unit = 'L/min'; break;
            case 'waste': unit = 'kg/day'; break;
            default: unit = 'units';
        }

        try {
            const response = await fetch('/api/devices', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: deviceName,
                    type: resourceType,
                    rating: deviceRating,
                    unit: unit
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to save device.');
            }

            const result = await response.json();
            renderDeviceToUI(result.device); // Render the newly created device from the server response
            closeDModal(); // Close the modal after successful addition

        } catch (error) {
            console.error('Error adding device:', error);
            alert(`Could not add device: ${error.message}`);
        }
    };

    // --- REVISED: Handle Device Deletion and Chart Updates ---
    deviceList.addEventListener('click', async (e) => {
        const li = e.target.closest('li');
        if (!li) return; // Ignore clicks that are not on or inside an <li>

        // Handle edit button click
        if (e.target.classList.contains('edit-btn')) {
            const deviceId = li.dataset.deviceId;
            const deviceType = li.dataset.type;
            const deviceRating = li.dataset.rating;
            const deviceUnit = li.dataset.unit;
            const deviceName = li.textContent.split('(')[0].trim().split(' ').slice(1).join(' '); // Extract name without icon
            
            const device = {
                id: deviceId,
                name: deviceName,
                type: deviceType,
                rating: deviceRating,
                unit: deviceUnit
            };
            
            openUsageModal(device);
            return;
        }

        // Handle device name click for editing
        if (e.target.classList.contains('device-name')) {
            const deviceId = li.dataset.deviceId;
            const deviceType = li.dataset.type;
            const deviceRating = li.dataset.rating;
            const deviceUnit = li.dataset.unit;
            const deviceName = e.target.textContent.split('(')[0].trim(); // Extract name without rating
            
            const device = {
                id: deviceId,
                name: deviceName,
                type: deviceType,
                rating: deviceRating,
                unit: deviceUnit
            };
            
            openUsageModal(device);
            return;
        }

        // Handle device deletion
        if (e.target.classList.contains('remove-btn')) {
            const deviceId = li.dataset.deviceId;
            if (!deviceId || !confirm("Are you sure you want to delete this device?")) {
                return;
            }

            try {
                const response = await fetch(`/api/devices/${deviceId}`, {
                    method: 'DELETE',
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Failed to delete device.');
                }
                
                li.remove(); // Remove from UI on success
                // Reset charts to default state after deletion
                electricChart.data.datasets[0].data = [0,0,0,0,0,0,0];
                waterChart.data.datasets[0].data = [0,0,0,0,0,0,0];
                wasteChart.data.datasets[0].data = [0,0,0,0,0,0,0];
                electricChart.update();
                waterChart.update();
                wasteChart.update();

            } catch (error) {
                console.error('Error deleting device:', error);
                alert(`Could not delete device: ${error.message}`);
            }

        // Handle selecting a device to show its chart (only if not clicking on buttons or device name)
        } else if (!e.target.classList.contains('edit-btn') && !e.target.classList.contains('remove-btn') && !e.target.classList.contains('device-name')) {
            const deviceId = li.dataset.deviceId;
            const deviceType = li.dataset.type;
            const deviceRating = parseFloat(li.dataset.rating);

            // Fetch usage data for this device
            try {
                const response = await fetch(`/api/devices/${deviceId}/usage`);
                if (response.ok) {
                    const data = await response.json();
                    const usageData = Object.values(data.usage_data);
                    
                    // Calculate actual usage values (hours * rating)
                    const calculatedUsage = usageData.map(hours => (parseFloat(hours) * deviceRating).toFixed(2));

                    // Reset all charts first
                    electricChart.data.datasets[0].data = [0,0,0,0,0,0,0];
                    waterChart.data.datasets[0].data = [0,0,0,0,0,0,0];
                    wasteChart.data.datasets[0].data = [0,0,0,0,0,0,0];

                    // Update the specific chart based on device type
                    if (deviceType === 'electric') {
                        electricChart.data.datasets[0].data = calculatedUsage;
                    } else if (deviceType === 'water') {
                        waterChart.data.datasets[0].data = calculatedUsage;
                    } else if (deviceType === 'waste') {
                        wasteChart.data.datasets[0].data = calculatedUsage;
                    }

                    // Update all charts to reflect changes
                    electricChart.update();
                    waterChart.update();
                    wasteChart.update();
                }
            } catch (error) {
                console.error('Error fetching device usage:', error);
            }
        }
    });

    const currentYearSpan = document.getElementById('current-year');
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }
});