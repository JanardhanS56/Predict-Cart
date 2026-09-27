const API_BASE = 'http://localhost:8000/api';

// ─── Category colour palette for modal header ───────────────────────────────
const CATEGORY_COLORS = {
    'Electronics':             'from-blue-600 to-indigo-700',
    'Clothing & Accessories':  'from-pink-500 to-rose-600',
    'Home & Kitchen':          'from-amber-500 to-orange-600',
    'Sports & Outdoors':       'from-emerald-500 to-green-600',
    'Books':                   'from-violet-500 to-purple-700',
    'Health & Beauty':         'from-fuchsia-500 to-pink-600',
    'Toys & Games':            'from-yellow-400 to-orange-500',
    'Food & Grocery':          'from-lime-500 to-green-600',
};
function categoryGradient(cat) {
    return CATEGORY_COLORS[cat] || 'from-gray-500 to-gray-700';
}

document.addEventListener('DOMContentLoaded', async () => {
    // ── DOM refs ─────────────────────────────────────────────────────────────
    const userSelect      = document.getElementById('user-select');
    const emptyState      = document.getElementById('empty-state');
    const loadingState    = document.getElementById('loading-state');
    const recsContainer   = document.getElementById('recommendations-container');
    const productsGrid    = document.getElementById('products-grid');
    const greeting        = document.getElementById('greeting');
    const subtitle        = document.getElementById('subtitle');
    const statsBadge      = document.getElementById('stats-badge');

    // ── Load users ───────────────────────────────────────────────────────────
    try {
        const res   = await fetch(`${API_BASE}/users`);
        if (!res.ok) throw new Error();
        const users = await res.json();

        const flags = { 'US':'🇺🇸','DE':'🇩🇪','GB':'🇬🇧','FR':'🇫🇷','JP':'🇯🇵',
                        'CA':'🇨🇦','AU':'🇦🇺','IN':'🇮🇳','BR':'🇧🇷','IT':'🇮🇹' };

        users.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.user_id;
            const flag = flags[u.country] || '🌐';
            opt.textContent = `Profile #${u.user_id} · ${u.age}y · ${u.gender} · ${flag} ${u.country}`;
            opt.dataset.user = JSON.stringify(u);
            userSelect.appendChild(opt);
        });
    } catch {
        subtitle.textContent = 'Error loading users. Is the backend running?';
        subtitle.classList.add('text-red-500');
    }

    // ── User selection → main recommendations ────────────────────────────────
    userSelect.addEventListener('change', async e => {
        const userId = e.target.value;
        if (!userId) {
            emptyState.classList.remove('hidden');
            recsContainer.classList.add('hidden');
            loadingState.classList.add('hidden');
            statsBadge.classList.add('hidden');
            greeting.textContent = 'Welcome to PredictCart';
            subtitle.textContent = 'Select a user profile above to generate personalized Next Best Offers.';
            return;
        }
        const user = JSON.parse(e.target.options[e.target.selectedIndex].dataset.user);

        emptyState.classList.add('hidden');
        recsContainer.classList.add('hidden');
        statsBadge.classList.add('hidden');
        loadingState.classList.remove('hidden');

        greeting.textContent = `Profile #${user.user_id} · ${user.age}y · ${user.gender}`;
        subtitle.textContent  = 'Traversing the relational graph, ranking next best offers...';

        try {
            await new Promise(r => setTimeout(r, 900));
            const res  = await fetch(`${API_BASE}/recommendations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            if (!res.ok) throw new Error();
            const data = await res.json();

            renderRecommendations(data.recommendations, productsGrid);
            loadingState.classList.add('hidden');
            recsContainer.classList.remove('hidden');
            statsBadge.classList.remove('hidden');
            subtitle.textContent = `Showing top ${Math.min(data.recommendations.length, 8)} AI-ranked offers for this profile.`;
        } catch {
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
            subtitle.textContent = 'Error loading recommendations.';
            subtitle.classList.add('text-red-500');
        }
    });

    // ── Live Simulation DOM refs ─────────────────────────────────────────────
    const productSelect   = document.getElementById('interactive-product-select');
    const btnView         = document.getElementById('btn-add-view');
    const btnCart         = document.getElementById('btn-add-cart');
    const interactionList = document.getElementById('interaction-list');
    const emptyMsg        = document.getElementById('empty-interaction-msg');
    const btnReset        = document.getElementById('btn-reset-session');
    const btnPredict      = document.getElementById('btn-predict-live');
    const liveLoading     = document.getElementById('live-loading-state');
    const loadingBar      = document.getElementById('loading-progress');
    const loadingText     = document.getElementById('live-loading-text');
    const liveContainer   = document.getElementById('live-recommendations-container');
    const liveGrid        = document.getElementById('live-products-grid');

    let allProducts = [];
    let sessionInteractions = [];

    // ── Load products ─────────────────────────────────────────────────────────
    try {
        const pr = await fetch(`${API_BASE}/products`);
        if (pr.ok) {
            allProducts = await pr.json();
            productSelect.innerHTML = '<option value="">Select a Product...</option>';
            allProducts.slice(0, 150).forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.product_id;
                const name = p.product_name || `Product ${p.product_id}`;
                opt.textContent = `${name.slice(0, 55)}${name.length > 55 ? '…' : ''} · $${parseFloat(p.price).toFixed(2)}`;
                opt.dataset.product = JSON.stringify(p);
                productSelect.appendChild(opt);
            });
        }
    } catch (err) {
        console.error('Failed to load products:', err);
    }

    // ── Add interaction helper ────────────────────────────────────────────────
    function addInteraction(type) {
        if (!productSelect.value) return;
        const sel     = productSelect.options[productSelect.selectedIndex];
        const product = JSON.parse(sel.dataset.product);
        sessionInteractions.push({ ...product, interactionType: type });

        if (sessionInteractions.length === 1) {
            emptyMsg.style.display = 'none';
            btnReset.classList.remove('hidden');
        }

        const li = document.createElement('li');
        li.className = 'flex items-center gap-2 bg-white p-2 rounded-lg shadow-sm border border-gray-100 text-sm';
        const badge = type === 'VIEW'
            ? '<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">VIEW</span>'
            : '<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-green-100 text-green-700">CART</span>';
        const name = product.product_name || `Product ${product.product_id}`;
        li.innerHTML = `${badge} <span class="text-gray-700 truncate">${name.slice(0,50)}</span> <span class="ml-auto text-gray-400 text-xs">$${parseFloat(product.price).toFixed(2)}</span>`;
        interactionList.appendChild(li);

        btnPredict.disabled = false;
        productSelect.value = '';
    }

    btnView.addEventListener('click',  () => addInteraction('VIEW'));
    btnCart.addEventListener('click',  () => addInteraction('CART'));

    // ── Reset session ─────────────────────────────────────────────────────────
    btnReset.addEventListener('click', () => {
        sessionInteractions = [];
        interactionList.innerHTML = '';
        interactionList.appendChild(emptyMsg);
        emptyMsg.style.display = '';
        btnPredict.disabled = true;
        btnReset.classList.add('hidden');
        liveContainer.classList.add('hidden');
        loadingText.textContent = 'Constructing Ego-Graph...';
        loadingText.classList.remove('text-red-500');
        loadingText.classList.add('animate-pulse');
    });

    // ── Live Prediction ───────────────────────────────────────────────────────
    btnPredict.addEventListener('click', async () => {
        liveContainer.classList.add('hidden');
        liveLoading.classList.replace('hidden', 'flex');
        loadingBar.style.width = '0%';
        loadingText.textContent = 'Constructing Ego-Graph...';

        const steps = [
            [600,  '40%',  'Querying NVIDIA Kumo Relational Endpoint...'],
            [1400, '75%',  'Evaluating Graph Topology...'],
            [2100, '92%',  'Decoding Softmax Probabilities...'],
        ];
        steps.forEach(([delay, pct, msg]) =>
            setTimeout(() => { loadingBar.style.width = pct; loadingText.textContent = msg; }, delay)
        );

        try {
            const res = await fetch(`${API_BASE}/predict_live`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_interactions: sessionInteractions.map(p => p.product_id) })
            });
            if (!res.ok) throw new Error();
            const data = await res.json();

            loadingBar.style.width = '100%';
            setTimeout(() => {
                liveLoading.classList.replace('flex', 'hidden');
                renderRecommendations(data.recommendations, liveGrid);
                liveContainer.classList.remove('hidden');
                liveContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 350);
        } catch {
            loadingText.textContent = 'Prediction failed. Check backend.';
            loadingText.classList.replace('animate-pulse', 'text-red-500');
        }
    });

    // ── Render cards ──────────────────────────────────────────────────────────
    function renderRecommendations(recs, container) {
        container.innerHTML = '';
        if (!recs || recs.length === 0) {
            container.innerHTML = `<div class="col-span-full text-center py-10 text-gray-400 text-sm">No recommendations available.</div>`;
            return;
        }

        const top = recs.slice(0, 8);

        // Update confidence meter (main grid only)
        if (container === productsGrid) {
            const avg     = top.reduce((s, r) => s + r.recommendation_score, 0) / top.length;
            const bar     = document.getElementById('confidence-bar');
            const txt     = document.getElementById('confidence-text');
            const pct     = Math.min(100, (avg / 0.05) * 100);
            bar.style.width = `${pct}%`;
            if (avg >= 0.04)      { bar.className = 'h-full bg-nvidia rounded-full transition-all duration-700';       txt.textContent = 'High'; }
            else if (avg >= 0.01) { bar.className = 'h-full bg-yellow-400 rounded-full transition-all duration-700';   txt.textContent = 'Medium'; }
            else                  { bar.className = 'h-full bg-gray-400 rounded-full transition-all duration-700';     txt.textContent = 'Low'; }
        }

        top.forEach((product, i) => {
            const score  = (product.recommendation_score * 100).toFixed(2);
            const grad   = categoryGradient(product.category);
            const name   = product.product_name || `Product ${product.product_id}`;
            const rating = product.rating_avg ? `${'★'.repeat(Math.round(product.rating_avg))}${'☆'.repeat(5 - Math.round(product.rating_avg))} ${parseFloat(product.rating_avg).toFixed(1)}` : '';

            let scoreLabel = 'High Match';
            let scoreBg    = 'bg-green-100 text-green-800';
            if (product.recommendation_score < 0.04 && product.recommendation_score >= 0.01) { scoreLabel = 'Good Match'; scoreBg = 'bg-yellow-100 text-yellow-800'; }
            if (product.recommendation_score < 0.01) { scoreLabel = 'Possible'; scoreBg = 'bg-gray-100 text-gray-600'; }

            const card = document.createElement('div');
            card.className = 'glass-panel rounded-2xl overflow-hidden card-hover flex flex-col opacity-0 translate-y-3 transition-all duration-300 cursor-pointer';
            card.dataset.product = JSON.stringify(product);

            setTimeout(() => card.classList.remove('opacity-0', 'translate-y-3'), i * 80);

            card.innerHTML = `
                <!-- Coloured header band -->
                <div class="bg-gradient-to-br ${grad} h-2 w-full"></div>
                <div class="p-5 flex flex-col flex-grow">
                    <div class="flex justify-between items-start mb-3">
                        <span class="text-[11px] font-bold px-2.5 py-1 rounded-full ${scoreBg}">${scoreLabel}</span>
                        <span class="text-[11px] font-black text-gray-500 bg-gray-100 px-2 py-1 rounded-lg">${score}%</span>
                    </div>
                    <div class="flex gap-2 mb-2 flex-wrap">
                        <span class="text-[11px] px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full font-medium">${product.category || ''}</span>
                        <span class="text-[11px] text-gray-400 font-medium mt-0.5">${product.brand || ''}</span>
                    </div>
                    <h3 class="font-display font-bold text-gray-900 text-base leading-snug mb-1 flex-grow">${name}</h3>
                    ${rating ? `<p class="text-[11px] text-yellow-500 mb-3">${rating}</p>` : '<div class="mb-3"></div>'}
                    <div class="pt-3 border-t border-gray-100 flex items-center justify-between mt-auto">
                        <div>
                            <p class="text-[10px] text-gray-400 uppercase tracking-wide">Price</p>
                            <p class="font-display font-black text-gray-900 text-lg">$${product.price ? parseFloat(product.price).toFixed(2) : '0.00'}</p>
                        </div>
                        <button class="view-offer-btn bg-gray-900 hover:bg-black text-white text-xs font-bold py-2 px-4 rounded-xl transition-colors shadow-sm">
                            View Offer
                        </button>
                    </div>
                </div>`;

            // "View Offer" button opens modal
            card.querySelector('.view-offer-btn').addEventListener('click', ev => {
                ev.stopPropagation();
                openModal(product);
            });
            // Clicking card also opens modal
            card.addEventListener('click', () => openModal(product));
            container.appendChild(card);
        });
    }

    // ── Product Detail Modal ──────────────────────────────────────────────────
    const modal       = document.getElementById('product-modal');
    const modalClose  = document.getElementById('modal-close');
    let   modalProduct = null;

    function openModal(product) {
        modalProduct = product;
        const name    = product.product_name || `Product ${product.product_id}`;
        const score   = (product.recommendation_score * 100).toFixed(2);
        const grad    = categoryGradient(product.category);
        const rating  = product.rating_avg ? `${'★'.repeat(Math.round(product.rating_avg))}${'☆'.repeat(5 - Math.round(product.rating_avg))} ${parseFloat(product.rating_avg).toFixed(1)} (${product.review_count || 0} reviews)` : 'No ratings yet';

        let scoreLabel = 'High Match'; let scoreBg = 'bg-green-100 text-green-800';
        if (product.recommendation_score < 0.04 && product.recommendation_score >= 0.01) { scoreLabel='Good Match'; scoreBg='bg-yellow-100 text-yellow-800'; }
        if (product.recommendation_score < 0.01) { scoreLabel='Possible'; scoreBg='bg-gray-100 text-gray-600'; }

        document.getElementById('modal-color-header').className = `h-48 flex items-center justify-center bg-gradient-to-br ${grad}`;
        document.getElementById('modal-score-badge').className  = `inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold mb-4 w-fit ${scoreBg}`;
        document.getElementById('modal-score-badge').textContent = `${scoreLabel} · ${score}% Kumo Score`;
        document.getElementById('modal-category').textContent   = product.category || '';
        document.getElementById('modal-subcategory').textContent= product.subcategory || '';
        document.getElementById('modal-brand').textContent      = product.brand || '';
        document.getElementById('modal-name').textContent       = name;
        document.getElementById('modal-rating').textContent     = rating;
        document.getElementById('modal-description').textContent= (product.product_description || 'No description available.').slice(0, 600);
        document.getElementById('modal-price').textContent      = `$${product.price ? parseFloat(product.price).toFixed(2) : '0.00'}`;

        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }

    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

    document.getElementById('modal-add-to-sim').addEventListener('click', () => {
        if (!modalProduct) return;
        // Inject product into live sim
        const prev = productSelect.value;
        // find the matching option or just push directly
        sessionInteractions.push({ ...modalProduct, interactionType: 'VIEW' });
        if (sessionInteractions.length === 1) {
            emptyMsg.style.display = 'none';
            btnReset.classList.remove('hidden');
        }
        const li = document.createElement('li');
        li.className = 'flex items-center gap-2 bg-white p-2 rounded-lg shadow-sm border border-gray-100 text-sm';
        const pname = modalProduct.product_name || `Product ${modalProduct.product_id}`;
        li.innerHTML = `<span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">VIEW</span> <span class="text-gray-700 truncate">${pname.slice(0,50)}</span> <span class="ml-auto text-gray-400 text-xs">$${parseFloat(modalProduct.price).toFixed(2)}</span>`;
        interactionList.appendChild(li);
        btnPredict.disabled = false;
        closeModal();
        document.getElementById('live-shopping-section')?.scrollIntoView({ behavior: 'smooth' });
    });
});
