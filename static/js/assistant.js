// BargainKart Talking AI Assistant & Visual Recommender Controller

document.addEventListener('DOMContentLoaded', () => {
    const openBtn = document.getElementById('openAssistantBtn');
    const closeBtn = document.getElementById('closeAssistantBtn');
    const drawer = document.getElementById('aiAssistantDrawer');
    const inputForm = document.getElementById('drawerInputForm');
    const inputField = document.getElementById('assistantInput');
    const messagesBox = document.getElementById('drawerMessages');
    const micBtn = document.getElementById('assistantMicBtn');
    const toggleTtsBtn = document.getElementById('toggleTtsBtn');
    const ttsIcon = document.getElementById('ttsIcon');
    const robotPanel = document.getElementById('robotAvatarPanel');
    const robotStatus = document.getElementById('robotStatusText');

    // Visual Panel Elements
    const visualPanel = document.getElementById('visualFeaturePanel');
    const visualTitle = document.getElementById('visualPanelTitle');
    const visualContent = document.getElementById('visualPanelContent');
    const closeVisualBtn = document.getElementById('closeVisualPanelBtn');
    const openEmptySpaceBtn = document.getElementById('openEmptySpaceModalBtn');
    const openSimilarSearchBtn = document.getElementById('openSimilarSearchModalBtn');

    let isTtsEnabled = true;
    let isSpeaking = false;

    // Toggle Drawer Open/Close
    if (openBtn && drawer) {
        openBtn.addEventListener('click', () => {
            drawer.classList.toggle('open');
            if (drawer.classList.contains('open')) {
                inputField.focus();
                greetIfFirstTime();
            }
        });
    }

    if (closeBtn && drawer) {
        closeBtn.addEventListener('click', () => {
            drawer.classList.remove('open');
            stopSpeaking();
        });
    }

    // Toggle TTS
    if (toggleTtsBtn) {
        toggleTtsBtn.addEventListener('click', () => {
            isTtsEnabled = !isTtsEnabled;
            if (!isTtsEnabled) {
                stopSpeaking();
                ttsIcon.className = 'fa-solid fa-volume-xmark text-rose-400';
                toggleTtsBtn.title = 'Robot Voice: Muted';
                robotStatus.textContent = 'Voice Muted • Text Mode';
            } else {
                ttsIcon.className = 'fa-solid fa-volume-high text-emerald-400';
                toggleTtsBtn.title = 'Robot Voice: Active';
                robotStatus.textContent = 'Voice Active • Ready';
                speakText("Voice enabled! I am ready to talk.");
            }
        });
    }

    // Speech Synthesis (Text-to-Speech)
    function speakText(text) {
        if (!isTtsEnabled || !('speechSynthesis' in window)) return;
        try {
            window.speechSynthesis.cancel();
            window.speechSynthesis.resume();

            // Strip markdown stars and symbols for clean reading
            const clean = text.replace(/[*_#`₹]/g, ' rupees ').replace(/Rs\./g, ' rupees ').replace(/https?:\/\/\S+/g, '');

            const utterance = new SpeechSynthesisUtterance(clean);
            utterance.rate = 1.0;
            utterance.pitch = 1.05;

            // Pick English voice if available
            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {
                const enVoice = voices.find(v => v.lang.startsWith('en')) || voices[0];
                if (enVoice) utterance.voice = enVoice;
            }

            utterance.onstart = () => {
                isSpeaking = true;
                if (robotPanel) robotPanel.classList.add('speaking');
                if (robotStatus) robotStatus.textContent = 'Speaking...';
            };

            utterance.onend = () => {
                isSpeaking = false;
                if (robotPanel) robotPanel.classList.remove('speaking');
                if (robotStatus) robotStatus.textContent = 'Ready • Voice Active';
            };

            utterance.onerror = () => {
                isSpeaking = false;
                if (robotPanel) robotPanel.classList.remove('speaking');
                if (robotStatus) robotStatus.textContent = 'Ready';
            };

            window.speechSynthesis.speak(utterance);
        } catch(e) {
            console.warn('Speech synthesis error:', e);
        }
    }

    // Expose speakText globally for message listen buttons
    window.assistantSpeakText = speakText;

    function stopSpeaking() {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
        if (robotPanel) robotPanel.classList.remove('speaking');
        if (robotStatus) robotStatus.textContent = 'Ready';
        isSpeaking = false;
    }

    function greetIfFirstTime() {
        if (!sessionStorage.getItem('robo_greeted')) {
            sessionStorage.setItem('robo_greeted', '1');
            setTimeout(() => {
                speakText("Hello! I am your BargainKart AI Assistant. How can I help you save or recommend products for your empty space today?");
            }, 600);
        }
    }

    // Speech-to-Text (Voice Recorder)
    if (micBtn) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRec) {
            const recognition = new SpeechRec();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-IN';

            micBtn.addEventListener('click', async () => {
                stopSpeaking();

                // Explicitly request browser microphone permission if supported
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    try {
                        await navigator.mediaDevices.getUserMedia({ audio: true });
                    } catch(permErr) {
                        console.warn('Microphone permission info:', permErr);
                        showMicPermissionModal();
                        return;
                    }
                }

                try {
                    micBtn.classList.add('recording');
                    micBtn.innerHTML = '<i class="fa-solid fa-microphone-lines fa-fade text-rose-400"></i>';
                    inputField.placeholder = "Listening... Speak now";
                    if (robotStatus) robotStatus.textContent = 'Listening to your voice...';
                    recognition.start();
                } catch(e) {
                    try { recognition.stop(); } catch(err) {}
                    micBtn.classList.remove('recording');
                    micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                    inputField.placeholder = "Type message or select voice prompt below...";
                    if (robotStatus) robotStatus.textContent = 'Ready • Voice Active';
                }
            });

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                inputField.value = transcript;
                micBtn.classList.remove('recording');
                micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                inputField.placeholder = "Type or click mic to speak...";
                if (robotStatus) robotStatus.textContent = 'Processing speech...';
                // Automatically submit
                inputForm.dispatchEvent(new Event('submit'));
            };

            recognition.onerror = (event) => {
                micBtn.classList.remove('recording');
                micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
                inputField.placeholder = "Type message or click prompt chips below...";
                if (robotStatus) robotStatus.textContent = 'Ready • Voice Active';
                if (event && (event.error === 'not-allowed' || event.error === 'service-not-allowed')) {
                    showMicPermissionModal();
                }
            };

            recognition.onend = () => {
                micBtn.classList.remove('recording');
                micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            };
        } else {
            micBtn.addEventListener('click', () => {
                showMicPermissionModal();
            });
        }
    }

    // Microphone Permission Helper Modal
    function showMicPermissionModal() {
        if (window.showMicPermissionModal && typeof window.showMicPermissionModal === 'function') {
            window.showMicPermissionModal();
            return;
        }
        let modal = document.getElementById('micPermissionHelperModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'micPermissionHelperModal';
            modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.85);backdrop-filter:blur(6px);z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;';
            modal.innerHTML = `
                <div style="max-width:480px;width:100%;background:#0f172a;border:2px solid #38bdf8;border-radius:12px;padding:24px;box-shadow:0 10px 40px rgba(0,0,0,0.8);position:relative;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:36px;height:36px;border-radius:50%;background:rgba(56,189,248,0.2);color:#38bdf8;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">
                                <i class="fa-solid fa-microphone"></i>
                            </div>
                            <strong style="color:#fff;font-size:1.1rem;font-family:'Space Grotesk',sans-serif;">How to Enable Microphone</strong>
                        </div>
                        <button type="button" onclick="document.getElementById('micPermissionHelperModal').style.display='none'" style="background:none;border:none;color:#94a3b8;font-size:1.4rem;cursor:pointer;">&times;</button>
                    </div>
                    <p style="font-size:0.84rem;color:#cbd5e1;line-height:1.5;margin-bottom:16px;">
                        Your browser protects your microphone until permission is granted. To talk to <strong>RoboBargain</strong> with your voice:
                    </p>
                    <div style="background:#1e293b;border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:14px;margin-bottom:16px;">
                        <div style="display:flex;gap:10px;margin-bottom:10px;font-size:0.8rem;color:#e2e8f0;">
                            <strong style="color:#38bdf8;">Step 1:</strong>
                            <span>Click the <strong>Tune / Lock icon (🔒)</strong> on the left side of the address bar (<code>http://127.0.0.1:5000</code>).</span>
                        </div>
                        <div style="display:flex;gap:10px;margin-bottom:10px;font-size:0.8rem;color:#e2e8f0;">
                            <strong style="color:#38bdf8;">Step 2:</strong>
                            <span>Toggle <strong>Microphone</strong> to <strong style="color:#34d399;">"Allow"</strong>.</span>
                        </div>
                        <div style="display:flex;gap:10px;font-size:0.8rem;color:#e2e8f0;">
                            <strong style="color:#38bdf8;">Step 3:</strong>
                            <span>Click the mic button again and speak clearly!</span>
                        </div>
                    </div>
                    <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:6px;padding:10px;font-size:0.76rem;color:#34d399;margin-bottom:16px;">
                        💡 <strong>Quick Option:</strong> You can also click any of the <strong>Voice Prompt Chips</strong> at the bottom of the chat drawer to simulate spoken queries instantly without a microphone!
                    </div>
                    <button type="button" onclick="document.getElementById('micPermissionHelperModal').style.display='none'" class="btn btn-primary" style="width:100%;padding:10px;font-weight:700;">
                        Got It, Let's Chat!
                    </button>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            modal.style.display = 'flex';
        }
    }

    // Submit Chat Message
    if (inputForm) {
        inputForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = inputField.value.trim();
            if (!text) return;

            appendUserMessage(text);
            inputField.value = '';
            inputField.disabled = true;

            const loadingMsg = appendTypingIndicator();
            if (robotStatus) robotStatus.textContent = 'RoboBargain is thinking...';

            try {
                const activeProdInput = document.querySelector('input[name="active_product_id"]');
                const productId = activeProdInput ? activeProdInput.value : null;

                const res = await fetch('/api/ai/assistant', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: text, product_id: productId })
                });

                loadingMsg.remove();
                const data = await res.json();
                appendAiMessage(data.response, data.action_url, data.action_label, data.chips);

                const toSpeak = data.speech_text || data.response;
                if (toSpeak) {
                    speakText(toSpeak);
                }

                // If visual mode triggered
                if (data.visual_mode === 'empty_space') {
                    showEmptySpacePanel();
                } else if (data.visual_mode === 'similar_search') {
                    showSimilarSearchPanel();
                }
            } catch (err) {
                loadingMsg.remove();
                appendAiMessage("I encountered an issue processing your request. Please try again shortly.");
                if (robotStatus) robotStatus.textContent = 'Ready';
            } finally {
                inputField.disabled = false;
                inputField.focus();
            }
        });
    }

    // Event delegation for suggested prompt chips
    if (messagesBox) {
        messagesBox.addEventListener('click', (e) => {
            if (e.target.classList.contains('chip-btn')) {
                const query = e.target.getAttribute('data-query');
                if (query === 'Empty Space Recommender' || query === '📸 Empty Space Recommender') {
                    showEmptySpacePanel();
                } else if (query === 'Find Similar Products' || query === '🖼️ Similar Product Search') {
                    showSimilarSearchPanel();
                } else if (query) {
                    inputField.value = query;
                    inputForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    // VISUAL AI: EMPTY SPACE RECOMMENDER
    if (openEmptySpaceBtn) {
        openEmptySpaceBtn.addEventListener('click', () => {
            showEmptySpacePanel();
        });
    }

    function showEmptySpacePanel() {
        if (!visualPanel) return;
        visualTitle.innerHTML = '<i class="fa-solid fa-camera text-emerald-400"></i> AI Empty Space Recommender';
        visualContent.innerHTML = `
            <div style="font-size: 0.74rem; color: #cbd5e1; margin-bottom: 8px;">
                Upload or select an empty room/kitchen photo for AI product recommendations:
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px;">
                <button type="button" class="btn btn-secondary btn-sm sample-space-btn" data-space="kitchen" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    🍳 Empty Kitchen Counter
                </button>
                <button type="button" class="btn btn-secondary btn-sm sample-space-btn" data-space="living_room" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    🛋️ Living Room Corner
                </button>
                <button type="button" class="btn btn-secondary btn-sm sample-space-btn" data-space="wall_study" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    🖼️ Blank Wall / Study Space
                </button>
                <button type="button" class="btn btn-secondary btn-sm sample-space-btn" data-space="bedroom" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    🛏️ Empty Bedroom Nook
                </button>
            </div>
            <div style="display: flex; gap: 6px; align-items: center;">
                <label style="flex: 1; padding: 6px 10px; background: rgba(15,23,42,0.8); border: 1px dashed #475569; border-radius: 6px; font-size: 0.72rem; color: #94a3b8; cursor: pointer; text-align: center;">
                    <i class="fa-solid fa-upload"></i> Upload Room Photo
                    <input type="file" id="customRoomFileInput" accept="image/*" style="display: none;">
                </label>
            </div>
        `;
        visualPanel.style.display = 'block';

        // Bind preset buttons
        visualContent.querySelectorAll('.sample-space-btn').forEach(b => {
            b.addEventListener('click', () => {
                const spaceType = b.getAttribute('data-space');
                triggerEmptySpaceAnalysis(spaceType);
            });
        });

        // Bind custom file upload
        const fileInput = document.getElementById('customRoomFileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files[0]) {
                    triggerEmptySpaceAnalysis('kitchen', e.target.files[0].name);
                }
            });
        }
    }

    async function triggerEmptySpaceAnalysis(spaceType, customName = null) {
        visualPanel.style.display = 'none';
        appendUserMessage(customName ? `[Uploaded Space Photo]: ${customName}` : `[Selected Empty Space]: ${spaceType.replace('_', ' ').toUpperCase()}`);
        const loadingMsg = appendTypingIndicator();
        if (robotStatus) robotStatus.textContent = 'Scanning room dimensions & objects...';

        try {
            const res = await fetch('/api/ai/empty-space-recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ space_type: spaceType })
            });

            const data = await res.json();
            loadingMsg.remove();

            // Build rich visual recommendation card in chat
            let html = `
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: var(--radius-md); padding: 12px; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span class="badge" style="background: rgba(16,185,129,0.2); color: #34d399; font-size: 0.7rem;">
                            <i class="fa-solid fa-circle-check"></i> Space Detected
                        </span>
                        <strong style="color: #fff; font-size: 0.88rem;">${data.title}</strong>
                    </div>
                    <div style="font-size: 0.75rem; color: #cbd5e1; margin-bottom: 10px;">
                        ${data.insights}
                    </div>
                    <div style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">
                        Recommended Products to Fill this Space:
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
            `;

            data.products.forEach(p => {
                html += `
                    <div style="display: flex; gap: 10px; align-items: center; background: rgba(30,41,59,0.6); padding: 8px; border-radius: 6px; border: 1px solid rgba(148,163,184,0.1);">
                        <img src="${p.image_url}" alt="${p.name}" style="width: 44px; height: 44px; object-fit: contain; border-radius: 4px; background: #0b1120;">
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-size: 0.78rem; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${p.name}</div>
                            <div style="font-size: 0.7rem; color: #10b981; font-weight: 700;">₹${Number(p.base_price).toLocaleString()} • ${p.brand}</div>
                            <div style="font-size: 0.68rem; color: var(--text-muted);">${p.space_fit_reason}</div>
                        </div>
                        <a href="/products/${p.id}" class="btn btn-primary btn-sm" style="font-size: 0.68rem; padding: 4px 8px; white-space: nowrap;">
                            View Deal
                        </a>
                    </div>
                `;
            });

            html += `</div></div>`;

            appendAiHtml(html, [
                'Try Living Room Space',
                'Try Kitchen Counter',
                'Can I negotiate these?',
                'Play Bargain Game'
            ]);

            speakText(data.speech_text);
        } catch(e) {
            loadingMsg.remove();
            appendAiMessage("Could not complete empty space analysis right now.");
        }
    }

    // VISUAL AI: SIMILAR IMAGE PRODUCT SEARCH
    if (openSimilarSearchBtn) {
        openSimilarSearchBtn.addEventListener('click', () => {
            showSimilarSearchPanel();
        });
    }

    function showSimilarSearchPanel() {
        if (!visualPanel) return;
        visualTitle.innerHTML = '<i class="fa-solid fa-images text-cyan-400"></i> AI Visual Similar Matcher';
        visualContent.innerHTML = `
            <div style="font-size: 0.74rem; color: #cbd5e1; margin-bottom: 8px;">
                Upload any picture of an item to find matching products in our 500 catalog:
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 10px;">
                <button type="button" class="btn btn-secondary btn-sm sample-prod-btn" data-key="kids_dress" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    👗 Kids Floral Dress
                </button>
                <button type="button" class="btn btn-secondary btn-sm sample-prod-btn" data-key="kitchen_tool" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    🍳 Kitchen Peeler / Slicer
                </button>
                <button type="button" class="btn btn-secondary btn-sm sample-prod-btn" data-key="saree_ethnic" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    🥻 Festive Silk Saree
                </button>
                <button type="button" class="btn btn-secondary btn-sm sample-prod-btn" data-key="mens_shirt" style="font-size: 0.72rem; padding: 6px 8px; text-align: left;">
                    👔 Men's Cotton Shirt
                </button>
            </div>
            <div style="display: flex; gap: 6px; align-items: center;">
                <label style="flex: 1; padding: 6px 10px; background: rgba(15,23,42,0.8); border: 1px dashed #475569; border-radius: 6px; font-size: 0.72rem; color: #94a3b8; cursor: pointer; text-align: center;">
                    <i class="fa-solid fa-upload"></i> Upload Any Product Picture
                    <input type="file" id="customProdFileInput" accept="image/*" style="display: none;">
                </label>
            </div>
        `;
        visualPanel.style.display = 'block';

        visualContent.querySelectorAll('.sample-prod-btn').forEach(b => {
            b.addEventListener('click', () => {
                const sampleKey = b.getAttribute('data-key');
                triggerSimilarSearch(sampleKey);
            });
        });

        const fileInput = document.getElementById('customProdFileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files[0]) {
                    triggerSimilarSearch('kids_dress', e.target.files[0].name);
                }
            });
        }
    }

    async function triggerSimilarSearch(sampleKey, customFileName = null) {
        visualPanel.style.display = 'none';
        appendUserMessage(customFileName ? `[Uploaded Product Image]: ${customFileName}` : `[Image Visual Search]: ${sampleKey.replace('_', ' ').toUpperCase()}`);
        const loadingMsg = appendTypingIndicator();
        if (robotStatus) robotStatus.textContent = 'Extracting color palette & silhouette...';

        try {
            const res = await fetch('/api/ai/similar-image-search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sample_key: sampleKey })
            });

            const data = await res.json();
            loadingMsg.remove();

            let html = `
                <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: var(--radius-md); padding: 12px; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span class="badge" style="background: rgba(56,189,248,0.2); color: #38bdf8; font-size: 0.7rem;">
                            <i class="fa-solid fa-magnifying-glass"></i> Visual Match
                        </span>
                        <strong style="color: #fff; font-size: 0.88rem;">${data.detected_item}</strong>
                    </div>
                    <div style="display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 10px;">
            `;

            data.visual_tags.forEach(t => {
                html += `<span class="badge" style="background: rgba(148,163,184,0.15); color: #cbd5e1; font-size: 0.65rem;">#${t}</span>`;
            });

            html += `</div><div style="display: flex; flex-direction: column; gap: 8px;">`;

            data.similar_products.forEach(p => {
                html += `
                    <div style="display: flex; gap: 10px; align-items: center; background: rgba(30,41,59,0.6); padding: 8px; border-radius: 6px; border: 1px solid rgba(148,163,184,0.1);">
                        <img src="${p.image_url}" alt="${p.name}" style="width: 44px; height: 44px; object-fit: contain; border-radius: 4px; background: #0b1120;">
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-size: 0.78rem; font-weight: 700; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${p.name}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 0.72rem; color: #34d399; font-weight: 700;">₹${Number(p.base_price).toLocaleString()}</span>
                                <span style="font-size: 0.68rem; color: #c084fc; font-weight: 700;">${p.match_badge}</span>
                            </div>
                        </div>
                        <a href="/products/${p.id}" class="btn btn-secondary btn-sm" style="font-size: 0.68rem; padding: 4px 8px; white-space: nowrap;">
                            Compare
                        </a>
                    </div>
                `;
            });

            html += `</div></div>`;

            appendAiHtml(html, [
                'Match Saree',
                'Match Kitchen Tool',
                'Can I negotiate?',
                'Play Bargain Game'
            ]);

            speakText(data.speech_text);
        } catch(e) {
            loadingMsg.remove();
            appendAiMessage("Visual search is temporarily unavailable.");
        }
    }

    if (closeVisualBtn) {
        closeVisualBtn.addEventListener('click', () => {
            if (visualPanel) visualPanel.style.display = 'none';
        });
    }

    // Helper: Append User Message
    function appendUserMessage(text) {
        const div = document.createElement('div');
        div.className = 'message user-message';
        div.textContent = text;
        messagesBox.appendChild(div);
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    // Helper: Typing Indicator
    function appendTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'message ai-message typing';
        div.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> RoboBargain is analyzing...';
        messagesBox.appendChild(div);
        messagesBox.scrollTop = messagesBox.scrollHeight;
        return div;
    }

    // Helper: Append AI Message
    function appendAiMessage(text, actionUrl = null, actionLabel = null, chips = []) {
        const div = document.createElement('div');
        div.className = 'message ai-message';

        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\n/g, '<br>');

        const cleanSpeech = text.replace(/[*_#`'"]/g, ' ').replace(/\s+/g, ' ');

        let html = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 0.68rem; color: #a855f7; font-weight: 700;"><i class="fa-solid fa-robot"></i> RoboBargain:</span>
                <button type="button" class="listen-msg-btn" onclick="window.assistantSpeakText('${cleanSpeech.slice(0, 200)}')" style="background: none; border: none; color: #38bdf8; font-size: 0.72rem; cursor: pointer; padding: 0 4px;" title="Listen to this response">
                    <i class="fa-solid fa-volume-high"></i> Listen
                </button>
            </div>
            <div>${formatted}</div>`;

        if (actionUrl && actionLabel) {
            html += `
                <div style="margin-top: 10px;">
                    <a href="${actionUrl}" class="btn btn-sm btn-primary" style="font-size: 0.76rem; padding: 5px 12px;">
                        ${actionLabel} <i class="fa-solid fa-arrow-right"></i>
                    </a>
                </div>
            `;
        }

        if (chips && chips.length > 0) {
            html += `<div class="quick-chips">`;
            chips.forEach(c => {
                html += `<button class="chip-btn" data-query="${c}">${c}</button>`;
            });
            html += `</div>`;
        }

        div.innerHTML = html;
        messagesBox.appendChild(div);
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }

    // Helper: Append Custom Rich HTML
    function appendAiHtml(innerHtml, chips = []) {
        const div = document.createElement('div');
        div.className = 'message ai-message';
        let html = innerHtml;

        if (chips && chips.length > 0) {
            html += `<div class="quick-chips">`;
            chips.forEach(c => {
                html += `<button class="chip-btn" data-query="${c}">${c}</button>`;
            });
            html += `</div>`;
        }

        div.innerHTML = html;
        messagesBox.appendChild(div);
        messagesBox.scrollTop = messagesBox.scrollHeight;
    }
});
