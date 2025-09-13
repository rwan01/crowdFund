//  document.addEventListener('DOMContentLoaded', function() {
//             // Tab switching functionality
//             const menuItems = document.querySelectorAll('.menu-item');
//             const tabContents = document.querySelectorAll('.tab-content');
            
//             menuItems.forEach(item => {
//                 item.addEventListener('click', function() {
//                     const tabId = this.getAttribute('data-tab');
                    
//                     // Activate selected tab
//                     menuItems.forEach(i => i.classList.remove('active'));
//                     this.classList.add('active');
                    
//                     // Show selected content
//                     tabContents.forEach(content => content.classList.remove('active'));
//                     document.getElementById(tabId).classList.add('active');
//                 });
//             });
            
//             // Delete account modal functionality
//             const deleteAccountBtn = document.getElementById('delete-account-btn');
//             const deleteAccountModal = document.getElementById('delete-account-modal');
//             const cancelDeleteBtn = document.getElementById('cancel-delete');
//             const confirmDeleteBtn = document.getElementById('confirm-delete');
            
//             deleteAccountBtn.addEventListener('click', function() {
//                 deleteAccountModal.style.display = 'flex';
//             });
            
//             cancelDeleteBtn.addEventListener('click', function() {
//                 deleteAccountModal.style.display = 'none';
//             });
            
//             confirmDeleteBtn.addEventListener('click', function() {
//                 const password = document.getElementById('deletePassword').value;
//                 if (password) {
//                     alert('Account deletion process initiated. This is just a demo.');
//                     deleteAccountModal.style.display = 'none';
//                 } else {
//                     alert('Please enter your password to confirm deletion.');
//                 }
//             });
            
//             // Cancel project functionality
//             const cancelProjectBtns = document.querySelectorAll('.cancel-project-btn');
//             const cancelProjectModal = document.getElementById('cancel-project-modal');
//             const cancelCancellationBtn = document.getElementById('cancel-cancellation');
//             const confirmCancellationBtn = document.getElementById('confirm-cancellation');
//             const projectToCancelElement = document.getElementById('project-to-cancel');
            
//             let currentProjectId = null;
            
//             cancelProjectBtns.forEach(btn => {
//                 btn.addEventListener('click', function() {
//                     if (!this.disabled) {
//                         const projectId = this.getAttribute('data-id');
//                         const projectTitle = this.getAttribute('data-title');
                        
//                         currentProjectId = projectId;
//                         projectToCancelElement.textContent = projectTitle;
                        
//                         cancelProjectModal.style.display = 'flex';
//                     }
//                 });
//             });
            
//             cancelCancellationBtn.addEventListener('click', function() {
//                 cancelProjectModal.style.display = 'none';
//             });
            
//             confirmCancellationBtn.addEventListener('click', function() {
//                 const reason = document.getElementById('cancellation-reason').value;
                
//                 if (!reason) {
//                     alert('Please provide a reason for cancellation.');
//                     return;
//                 }
                
//                 // In a real application, this would send a request to the server
//                 // For this demo, we'll just update the UI
//                 const projectCard = document.querySelector(`.project-card[data-id="${currentProjectId}"]`);
//                 if (projectCard) {
//                     // Update status
//                     const statusElement = projectCard.querySelector('.project-status');
//                     statusElement.textContent = 'Cancelled';
//                     statusElement.className = 'project-status status-cancelled';
                    
//                     // Update button
//                     const cancelBtn = projectCard.querySelector('.cancel-project-btn');
//                     cancelBtn.textContent = 'Cancelled';
//                     cancelBtn.className = 'btn btn-secondary btn-small';
//                     cancelBtn.disabled = true;
                    
//                     // Show success message
//                     alert('Project has been successfully cancelled. All backers will be refunded.');
//                 }
                
//                 cancelProjectModal.style.display = 'none';
//             });
            
//             // Close modals if clicked outside
//             window.addEventListener('click', function(event) {
//                 if (event.target === deleteAccountModal) {
//                     deleteAccountModal.style.display = 'none';
//                 }
//                 if (event.target === cancelProjectModal) {
//                     cancelProjectModal.style.display = 'none';
//                 }
//             });
//         });




        document.addEventListener('DOMContentLoaded', function() {
            // Tab switching functionality
            const menuItems = document.querySelectorAll('.menu-item');
            const tabContents = document.querySelectorAll('.tab-content');
            
            menuItems.forEach(item => {
                item.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');
                    
                    // Activate selected tab
                    menuItems.forEach(i => i.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Show selected content
                    tabContents.forEach(content => content.classList.remove('active'));
                    document.getElementById(tabId).classList.add('active');
                });
            });
            
            // Delete account modal functionality
            const deleteAccountBtn = document.getElementById('delete-account-btn');
            const deleteAccountModal = document.getElementById('delete-account-modal');
            const cancelDeleteBtn = document.getElementById('cancel-delete');
            const confirmDeleteBtn = document.getElementById('confirm-delete');
            
            deleteAccountBtn.addEventListener('click', function() {
                deleteAccountModal.style.display = 'flex';
            });
            
            cancelDeleteBtn.addEventListener('click', function() {
                deleteAccountModal.style.display = 'none';
            });
            
            confirmDeleteBtn.addEventListener('click', function() {
                const password = document.getElementById('deletePassword').value;
                if (password) {
                    alert('Account deletion process initiated. This is just a demo.');
                    deleteAccountModal.style.display = 'none';
                } else {
                    alert('Please enter your password to confirm deletion.');
                }
            });
            
            // Cancel project functionality
            const cancelProjectBtns = document.querySelectorAll('.cancel-project-btn');
            const cancelProjectModal = document.getElementById('cancel-project-modal');
            const cancelCancellationBtn = document.getElementById('cancel-cancellation');
            const confirmCancellationBtn = document.getElementById('confirm-cancellation');
            const projectToCancelElement = document.getElementById('project-to-cancel');
            
            let currentProjectId = null;
            
            cancelProjectBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    if (!this.disabled) {
                        const projectId = this.getAttribute('data-id');
                        const projectTitle = this.getAttribute('data-title');
                        
                        currentProjectId = projectId;
                        projectToCancelElement.textContent = projectTitle;
                        
                        cancelProjectModal.style.display = 'flex';
                    }
                });
            });
            
            cancelCancellationBtn.addEventListener('click', function() {
                cancelProjectModal.style.display = 'none';
            });
            
            confirmCancellationBtn.addEventListener('click', function() {
                const reason = document.getElementById('cancellation-reason').value;
                
                if (!reason) {
                    alert('Please provide a reason for cancellation.');
                    return;
                }
                
                // In a real application, this would send a request to the server
                // For this demo, we'll just update the UI
                const projectCard = document.querySelector(`.project-card[data-id="${currentProjectId}"]`);
                if (projectCard) {
                    // Update status
                    const statusElement = projectCard.querySelector('.project-status');
                    statusElement.textContent = 'Cancelled';
                    statusElement.className = 'project-status status-cancelled';
                    
                    // Update button
                    const cancelBtn = projectCard.querySelector('.cancel-project-btn');
                    cancelBtn.textContent = 'Cancelled';
                    cancelBtn.className = 'btn btn-secondary btn-small';
                    cancelBtn.disabled = true;
                    
                    // Show success message
                    alert('Project has been successfully cancelled. All backers will be refunded.');
                }
                
                cancelProjectModal.style.display = 'none';
            });
            
            // Close modals if clicked outside
            window.addEventListener('click', function(event) {
                if (event.target === deleteAccountModal) {
                    deleteAccountModal.style.display = 'none';
                }
                if (event.target === cancelProjectModal) {
                    cancelProjectModal.style.display = 'none';
                }
            });
        });