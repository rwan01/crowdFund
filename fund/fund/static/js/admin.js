document.addEventListener('DOMContentLoaded', function() {
            // Tab switching functionality
            const menuItems = document.querySelectorAll('.menu-item');
            const tabContents = document.querySelectorAll('.tab-content');
            
            menuItems.forEach(item => {
                if (item.id !== 'logout-btn') {
                    item.addEventListener('click', function() {
                        const tabId = this.getAttribute('data-tab');
                        
                        // Activate selected tab
                        menuItems.forEach(i => i.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Show selected content
                        tabContents.forEach(content => content.classList.remove('active'));
                        document.getElementById(tabId).classList.add('active');
                    });
                }
            });
            
            // Inner tabs functionality
            const innerTabs = document.querySelectorAll('.tab');
            const innerTabContents = document.querySelectorAll('.tab-content[id]');
            
            innerTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const contentId = this.getAttribute('data-content');
                    
                    // Activate selected tab
                    innerTabs.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Show selected content
                    innerTabContents.forEach(content => content.classList.remove('active'));
                    document.getElementById(contentId).classList.add('active');
                });
            });
            
            // Add category modal functionality
            const addCategoryBtn = document.getElementById('add-category-btn');
            const addCategoryModal = document.getElementById('add-category-modal');
            const cancelCategoryBtn = document.getElementById('cancel-category');
            const saveCategoryBtn = document.getElementById('save-category');
            
            addCategoryBtn.addEventListener('click', function() {
                addCategoryModal.style.display = 'flex';
            });
            
            cancelCategoryBtn.addEventListener('click', function() {
                addCategoryModal.style.display = 'none';
            });
            
            saveCategoryBtn.addEventListener('click', function() {
                const categoryName = document.getElementById('categoryName').value;
                const categoryDescription = document.getElementById('categoryDescription').value;
                
                if (categoryName && categoryDescription) {
                    // In a real application, you would send this data to the server
                    alert(`Category "${categoryName}" added successfully!`);
                    addCategoryModal.style.display = 'none';
                    document.getElementById('add-category-form').reset();
                } else {
                    alert('Please fill in all fields');
                }
            });
            
            // Logout functionality
            const logoutBtn = document.getElementById('logout-btn');
            logoutBtn.addEventListener('click', function() {
                if (confirm('Are you sure you want to logout?')) {
                    alert('Logged out successfully!');
                    // In a real application, this would redirect to the login page
                }
            });
            
            // Close modal if clicked outside
            window.addEventListener('click', function(event) {
                if (event.target === addCategoryModal) {
                    addCategoryModal.style.display = 'none';
                }
            });
        });