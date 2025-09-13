        document.addEventListener('DOMContentLoaded', function() {
            // Category selection
            const categoryOptions = document.querySelectorAll('.category-option');
            categoryOptions.forEach(option => {
                option.addEventListener('click', function() {
                    categoryOptions.forEach(opt => opt.classList.remove('selected'));
                    this.classList.add('selected');
                });
            });
            
            // Image upload preview
            const imageUpload = document.getElementById('imageUpload');
            const imagePreviews = document.querySelectorAll('.image-preview');
            
            imageUpload.addEventListener('change', function() {
                const files = this.files;
                
                for (let i = 0; i < Math.min(files.length, imagePreviews.length); i++) {
                    const reader = new FileReader();
                    const preview = imagePreviews[i];
                    
                    reader.onload = function(e) {
                        preview.innerHTML = '';
                        const img = document.createElement('img');
                        img.src = e.target.result;
                        
                        const removeBtn = document.createElement('div');
                        removeBtn.className = 'remove-image';
                        removeBtn.innerHTML = '&times;';
                        removeBtn.addEventListener('click', function(event) {
                            event.stopPropagation();
                            preview.innerHTML = '<span>No image</span>';
                            // Note: In a real app, you would need to handle the file removal from the form data
                        });
                        
                        preview.appendChild(img);
                        preview.appendChild(removeBtn);
                    };
                    
                    reader.readAsDataURL(files[i]);
                }
            });
            
            // Tag input functionality
            const tagsInput = document.querySelector('.tags-input input');
            const tagsContainer = document.querySelector('.tags-input');
            
            tagsInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && this.value.trim() !== '') {
                    e.preventDefault();
                    
                    const tag = document.createElement('div');
                    tag.className = 'tag';
                    tag.innerHTML = `${this.value.trim()} <span class="remove-tag">&times;</span>`;
                    
                    tagsContainer.insertBefore(tag, this);
                    
                    // Add remove functionality
                    tag.querySelector('.remove-tag').addEventListener('click', function() {
                        tag.remove();
                    });
                    
                    this.value = '';
                }
            });
            
            // Remove tag functionality for existing tags
            document.querySelectorAll('.remove-tag').forEach(btn => {
                btn.addEventListener('click', function() {
                    this.parentElement.remove();
                });
            });
            
            // Form validation and submission
            const projectForm = document.getElementById('create-project-form');
            
            projectForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Basic validation
                const title = document.getElementById('projectTitle').value;
                const details = document.getElementById('projectDetails').value;
                const target = document.getElementById('fundingTarget').value;
                const startDate = document.getElementById('startDate').value;
                const endDate = document.getElementById('endDate').value;
                const selectedCategory = document.querySelector('.category-option.selected');
                
                if (!title || !details || !target || !startDate || !endDate || !selectedCategory) {
                    alert('Please fill in all required fields');
                    return;
                }
                
                // Check if at least one image is uploaded
                const hasImages = Array.from(imagePreviews).some(preview => {
                    return preview.querySelector('img') !== null;
                });
                
                if (!hasImages) {
                    alert('Please upload at least one image for your project');
                    return;
                }
                
                // In a real application, you would submit the form data to the server here
                alert('Project created successfully! This is a demo. In a real application, the data would be sent to the server.');
                
                // Reset form
                projectForm.reset();
                document.querySelectorAll('.category-option').forEach(opt => opt.classList.remove('selected'));
                imagePreviews.forEach(preview => preview.innerHTML = '<span>No image</span>');
                document.querySelectorAll('.tag').forEach(tag => {
                    if (tag !== tagsInput) tag.remove();
                });
            });
            
            // Set minimum date for start and end dates to today
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('startDate').min = today;
            document.getElementById('endDate').min = today;
        });