/**
 * Distinguished Key Clubber Landing Page - Vanilla JS Interactive Features
 * Handled: Scroll animations (reduced-motion aware), Real-Time Debounced FAQ Search & Highlighting.
 * Note: Accordion behavior and smooth scrolling are handled natively by HTML5 <details name="faq"> and CSS.
 */

document.addEventListener('DOMContentLoaded', () => {
    initScrollAnimations();
    initFAQSearch();
});

/**
 * 1. Intersection Observer for Scroll Fade-In Effects (Respects prefers-reduced-motion)
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in-up');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
        animatedElements.forEach(el => el.classList.add('visible'));
        return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    animatedElements.forEach(el => observer.observe(el));
}

/**
 * 2. Real-Time Debounced FAQ Search & Native Details/Summary Control
 */
function initFAQSearch() {
    const searchInput = document.getElementById('faq-search-input');
    const searchBtn = document.getElementById('faq-search-btn');
    const accordionItems = document.querySelectorAll('.accordion-item');
    const noResultsMsg = document.getElementById('faq-no-results');

    if (!searchInput || !accordionItems.length) return;

    if (searchBtn) {
        searchBtn.addEventListener('click', () => searchInput.focus());
    }

    // Cache original HTML and text content once
    const originalContent = new Map();
    accordionItems.forEach(item => {
        const questionEl = item.querySelector('.question-text');
        const answerEl = item.querySelector('.accordion-content');
        originalContent.set(item, {
            questionHtml: questionEl ? questionEl.innerHTML : '',
            questionText: questionEl ? questionEl.textContent.toLowerCase() : '',
            answerHtml: answerEl ? answerEl.innerHTML : '',
            answerText: answerEl ? answerEl.textContent.toLowerCase() : ''
        });
    });

    let debounceTimer = null;

    function executeSearch() {
        const query = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        accordionItems.forEach(item => {
            const data = originalContent.get(item);
            const questionEl = item.querySelector('.question-text');
            const answerEl = item.querySelector('.accordion-content');

            if (!query) {
                item.style.display = '';
                item.open = false;
                item.setAttribute('name', 'faq');
                if (questionEl) questionEl.innerHTML = data.questionHtml;
                if (answerEl) answerEl.innerHTML = data.answerHtml;
                visibleCount++;
                return;
            }

            const matchesQuestion = data.questionText.includes(query);
            const matchesAnswer = data.answerText.includes(query);

            if (matchesQuestion || matchesAnswer) {
                item.style.display = '';
                visibleCount++;

                // Allow multiple results to display open simultaneously during active search
                item.removeAttribute('name');
                item.open = true;

                if (questionEl) {
                    questionEl.innerHTML = highlightMatch(data.questionHtml, query);
                }
                if (answerEl) {
                    answerEl.innerHTML = highlightMatch(data.answerHtml, query);
                }
            } else {
                item.style.display = 'none';
                item.open = false;
            }
        });

        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(executeSearch, 150);
    });

    // Native clear button on <input type="search"> triggers "search" event in browsers
    searchInput.addEventListener('search', () => {
        clearTimeout(debounceTimer);
        executeSearch();
    });
}

/**
 * Utility: Safely highlight search term matches inside HTML text nodes
 */
function highlightMatch(html, query) {
    if (!query) return html;

    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    const walk = document.createTreeWalker(tempDiv, NodeFilter.SHOW_TEXT, null, false);
    const textNodes = [];
    let node;
    while ((node = walk.nextNode())) {
        textNodes.push(node);
    }

    textNodes.forEach(textNode => {
        if (textNode.nodeValue.toLowerCase().includes(query)) {
            const span = document.createElement('span');
            span.innerHTML = textNode.nodeValue.replace(regex, '<mark class="faq-highlight">$1</mark>');
            textNode.parentNode.replaceChild(span, textNode);
        }
    });

    return tempDiv.innerHTML;
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
