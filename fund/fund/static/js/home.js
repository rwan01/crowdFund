        // Simple JavaScript for interactive elements
        document.addEventListener('DOMContentLoaded', function() {
            // Search functionality
            const searchButton = document.querySelector('.search-bar button');
            const searchInput = document.querySelector('.search-bar input');
            
            searchButton.addEventListener('click', function() {
                if (searchInput.value.trim() !== '') {
                    alert('Searching for: ' + searchInput.value);
                    searchInput.value = '';
                }
            });
            
            // Category selection
            const categories = document.querySelectorAll('.category');
            categories.forEach(category => {
                category.addEventListener('click', function() {
                    categories.forEach(c => c.style.background = 'white');
                    categories.forEach(c => c.style.color = 'inherit');
                    this.style.background = 'var(--primary)';
                    this.style.color = 'white';
                    alert('Filtering by: ' + this.textContent.trim());
                });
            });
            
            // Project card click
            const projectCards = document.querySelectorAll('.project-card');
            projectCards.forEach(card => {
                card.addEventListener('click', function() {
                    const title = this.querySelector('.project-title').textContent;
                    alert('Viewing project: ' + title);
                });
            });
            
            // Auth buttons
            const loginBtn = document.querySelector('.btn-outline');
            const registerBtn = document.querySelector('.btn-primary');
            
            loginBtn.addEventListener('click', function() {
                alert('Login form would appear here');
            });
            
            registerBtn.addEventListener('click', function() {
                alert('Registration form would appear here');
            });
        });