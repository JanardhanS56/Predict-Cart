const API_BASE = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', async () => {
    const userSelect = document.getElementById('user-select');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const recsContainer = document.getElementById('recommendations-container');
    const productsGrid = document.getElementById('products-grid');
    const greeting = document.getElementById('greeting');
    const subtitle = document.getElementById('subtitle');
    const statsBadge = document.getElementById('stats-badge');

    // Fetch users
    try {
        const response = await fetch(`${API_BASE}/users`);
        if (!response.ok) throw new Error('Failed to fetch users');
        const users = await response.json();
        
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.user_id;
            option.textContent = `User ${user.user_id} - Age ${user.age} (${user.gender}) - ${user.country}`;
            option.dataset.user = JSON.stringify(user);
            userSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching users:', error);
        subtitle.textContent = "Error loading users. Is the backend running?";
        subtitle.classList.add('text-red-500');
    }

    // Handle user selection
    userSelect.addEventListener('change', async (e) => {
        const userId = e.target.value;
        const selectedOption = e.target.options[e.target.selectedIndex];
        
        if (!userId) {
            // Reset to empty state
            emptyState.classList.remove('hidden');
            recsContainer.classList.add('hidden');
            loadingState.classList.add('hidden');
            statsBadge.classList.add('hidden');
            greeting.textContent = 'Welcome to PredictCart';
            subtitle.textContent = 'Select a user profile above to see personalized Next Best Offers.';
            return;
        }

        const user = JSON.parse(selectedOption.dataset.user);
        
        // Show loading state
        emptyState.classList.add('hidden');
        recsContainer.classList.add('hidden');
        statsBadge.classList.add('hidden');
        loadingState.classList.remove('hidden');
        
        greeting.textContent = `Hello, User ${user.user_id}`;
        subtitle.textContent = `Generating tailored offers based on their historical behavior...`;

        try {
            const response = await fetch(`${API_BASE}/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId })
            });
            
            if (!response.ok) throw new Error('Failed to fetch recommendations');
            const data = await response.json();
            
            renderRecommendations(data.recommendations);
            
            // Hide loading, show results
            loadingState.classList.add('hidden');
            recsContainer.classList.remove('hidden');
            statsBadge.classList.remove('hidden');
            subtitle.textContent = `Here are the top personalized offers for this profile.`;
            
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
            subtitle.textContent = "Error loading recommendations.";
            subtitle.classList.add('text-red-500');
        }
    });

    function renderRecommendations(recommendations) {
        productsGrid.innerHTML = '';
        
        if (!recommendations || recommendations.length === 0) {
            productsGrid.innerHTML = `<div class="col-span-full text-center py-10 text-gray-500">No recommendations available for this user in the mock payload.</div>`;
            return;
        }

        // Only show top 8
        const topRecs = recommendations.slice(0, 8);

        topRecs.forEach((product, index) => {
            const score = (product.recommendation_score * 100).toFixed(1);
            
            // Color coding based on confidence
            let scoreColor = 'bg-nvidia';
            let bgLight = 'bg-green-50';
            let borderLight = 'border-green-100';
            if (product.recommendation_score < 0.2) {
                scoreColor = 'bg-yellow-500';
                bgLight = 'bg-yellow-50';
                borderLight = 'border-yellow-100';
            }
            if (product.recommendation_score < 0.1) {
                scoreColor = 'bg-gray-400';
                bgLight = 'bg-gray-50';
                borderLight = 'border-gray-100';
            }

            const card = document.createElement('div');
            card.className = `glass-panel rounded-2xl overflow-hidden transition-all duration-300 card-hover flex flex-col h-full opacity-0 translate-y-4`;
            
            // Add staggered animation
            setTimeout(() => {
                card.classList.remove('opacity-0', 'translate-y-4');
            }, index * 100);

            card.innerHTML = `
                <div class="${bgLight} border-b ${borderLight} p-4 flex justify-between items-center relative overflow-hidden">
                    <!-- Subtle background logo/pattern could go here -->
                    <div>
                        <span class="text-xs font-bold text-gray-400 uppercase tracking-wider block mb-1">NVIDIA Kumo Score</span>
                        <div class="flex items-center space-x-2">
                            <span class="text-2xl font-black text-gray-900">${score}%</span>
                            <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                        </div>
                    </div>
                    <div class="h-12 w-12 rounded-full border-4 border-white shadow-sm flex items-center justify-center bg-white">
                        <svg class="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>
                    </div>
                </div>
                <div class="p-6 flex flex-col flex-grow">
                    <div class="flex justify-between items-start mb-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            ${product.category || 'Product'}
                        </span>
                        <span class="text-sm text-gray-500">${product.brand || ''}</span>
                    </div>
                    <h3 class="text-lg font-bold text-gray-900 leading-tight mb-2 flex-grow">${product.product_id}</h3>
                    
                    <div class="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                        <div>
                            <span class="text-xs text-gray-500 block">Price</span>
                            <span class="font-bold text-gray-900">$${product.price ? parseFloat(product.price).toFixed(2) : '0.00'}</span>
                        </div>
                        <button class="bg-gray-900 hover:bg-black text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900">
                            View Offer
                        </button>
                    </div>
                </div>
            `;
            productsGrid.appendChild(card);
        });
    }
});
