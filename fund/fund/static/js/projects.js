        document.addEventListener('DOMContentLoaded', function() {
            // Get DOM elements
            const searchInput = document.getElementById('search-input');
            const searchButton = document.getElementById('search-button');
            const categoryFilter = document.getElementById('category-filter');
            const statusFilter = document.getElementById('status-filter');
            const sortBy = document.getElementById('sort-by');
            const resultsSort = document.getElementById('results-sort');
            const filterTags = document.querySelectorAll('.filter-tag');
            const projectCards = document.querySelectorAll('.project-card');
            const projectsCount = document.getElementById('projects-count');
            
            // Search functionality
            function performSearch() {
                const searchTerm = searchInput.value.toLowerCase();
                const category = categoryFilter.value;
                const status = statusFilter.value;
                
                let visibleCount = 0;
                
                projectCards.forEach(card => {
                    const title = card.querySelector('.project-title').textContent.toLowerCase();
                    const tags = card.getAttribute('data-tags');
                    const cardCategory = card.getAttribute('data-category');
                    
                    const matchesSearch = searchTerm === '' || 
                                        title.includes(searchTerm) || 
                                        tags.includes(searchTerm);
                    
                    const matchesCategory = category === 'all' || cardCategory === category;
                    
                    // For demo purposes, we'll assume all projects are active
                    const matchesStatus = status === 'all' || status === 'active';
                    
                    if (matchesSearch && matchesCategory && matchesStatus) {
                        card.style.display = 'block';
                        visibleCount++;
                    } else {
                        card.style.display = 'none';
                    }
                });
                
                projectsCount.textContent = visibleCount;
                
                // Show message if no results
                if (visibleCount === 0) {
                    const noResults = document.createElement('div');
                    noResults.className = 'no-results';
                    noResults.innerHTML = `
                        <div style="text-align: center; padding: 40px;">
                            <i class="fas fa-search" style="font-size: 48px; color: var(--gray); margin-bottom: 20px;"></i>
                            <h3>No projects found</h3>
                            <p>Try adjusting your search or filters</p>
                        </div>
                    `;
                    
                    // Check if no-results message already exists
                    const existingNoResults = document.querySelector('.no-results');
                    if (existingNoResults) {
                        existingNoResults.remove();
                    }
                    
                    document.getElementById('projects-grid').appendChild(noResults);
                } else {
                    const existingNoResults = document.querySelector('.no-results');
                    if (existingNoResults) {
                        existingNoResults.remove();
                    }
                }
            }
            
            // Event listeners
            searchButton.addEventListener('click', performSearch);
            
            searchInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
            
            categoryFilter.addEventListener('change', performSearch);
            statusFilter.addEventListener('change', performSearch);
            sortBy.addEventListener('change', performSearch);
            resultsSort.addEventListener('change', performSearch);
            
            filterTags.forEach(tag => {
                tag.addEventListener('click', function() {
                    filterTags.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    
                    // For demo purposes, we'll simulate filtering by tag
                    const tagText = this.textContent.toLowerCase();
                    
                    if (tagText === 'all') {
                        performSearch();
                        return;
                    }
                    
                    let visibleCount = 0;
                    
                    projectCards.forEach(card => {
                        const tags = card.getAttribute('data-tags');
                        
                        if (tags.includes(tagText)) {
                            card.style.display = 'block';
                            visibleCount++;
                        } else {
                            card.style.display = 'none';
                        }
                    });
                    
                    projectsCount.textContent = visibleCount;
                });
            });
            
            // Project card click - redirect to project page
            projectCards.forEach(card => {
                card.addEventListener('click', function() {
                    const projectTitle = this.querySelector('.project-title').textContent;
                    // In a real application, this would redirect to the project details page
                    alert(`Opening project: ${projectTitle}`);
                    // window.location.href = `project-details.html?title=${encodeURIComponent(projectTitle)}`;
                });
            });
            
            // Initialize with all projects visible
            projectsCount.textContent = document.querySelectorAll('.project-card').length;
        });