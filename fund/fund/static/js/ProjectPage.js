        document.addEventListener('DOMContentLoaded', function() {
            // Rating functionality
            const customRatingInput = document.getElementById('custom-rating');
            const ratingSlider = document.getElementById('rating-slider');
            const submitRatingBtn = document.getElementById('submit-rating');
            const ratingMessage = document.getElementById('rating-message');
            const visualStarsContainer = document.getElementById('visual-stars');
            
            // Initialize rating from localStorage if available
            const savedRating = localStorage.getItem('projectRating');
            if (savedRating) {
                const ratingValue = parseFloat(savedRating);
                customRatingInput.value = ratingValue;
                ratingSlider.value = ratingValue;
                updateVisualStars(ratingValue);
            } else {
                updateVisualStars(parseFloat(customRatingInput.value));
            }
            
            // Sync input and slider
            customRatingInput.addEventListener('input', function() {
                let value = parseFloat(this.value);
                
                // Validate input
                if (isNaN(value)) value = 0;
                if (value < 0) value = 0;
                if (value > 10) value = 10;
                
                this.value = value;
                ratingSlider.value = value;
                updateVisualStars(value);
            });
            
            ratingSlider.addEventListener('input', function() {
                customRatingInput.value = this.value;
                updateVisualStars(parseFloat(this.value));
            });
            
            // Submit rating
            submitRatingBtn.addEventListener('click', function() {
                const ratingValue = parseFloat(customRatingInput.value);
                
                if (ratingValue >= 0 && ratingValue <= 10) {
                    localStorage.setItem('projectRating', ratingValue);
                    
                    ratingMessage.style.display = 'block';
                    ratingMessage.textContent = `Thank you for your ${ratingValue}/10 rating!`;
                    
                    setTimeout(() => {
                        ratingMessage.style.display = 'none';
                    }, 3000);
                    
                    // In a real application, you would send the rating to the server here
                    console.log(`User rated the project: ${ratingValue}/10`);
                } else {
                    alert('Please enter a valid rating between 0 and 10');
                }
            });
            
            // Function to update visual stars based on rating
            function updateVisualStars(rating) {
                visualStarsContainer.innerHTML = '';
                
                const fullStars = Math.floor(rating);
                const partialStar = rating - fullStars;
                
                // Add full stars
                for (let i = 0; i < fullStars; i++) {
                    const star = document.createElement('span');
                    star.className = 'visual-star';
                    star.innerHTML = '★';
                    visualStarsContainer.appendChild(star);
                }
                
                // Add partial star if needed
                if (partialStar > 0) {
                    const partialStarElement = document.createElement('span');
                    partialStarElement.className = 'partial-star';
                    partialStarElement.innerHTML = '★';
                    
                    const partialStarFill = document.createElement('span');
                    partialStarFill.className = 'partial-star-fill';
                    partialStarFill.style.width = `${partialStar * 100}%`;
                    partialStarFill.innerHTML = '★';
                    
                    partialStarElement.appendChild(partialStarFill);
                    visualStarsContainer.appendChild(partialStarElement);
                }
                
                // Add empty stars if needed
                const emptyStars = 10 - Math.ceil(rating);
                for (let i = 0; i < emptyStars; i++) {
                    const star = document.createElement('span');
                    star.className = 'visual-star';
                    star.style.color = '#ddd';
                    star.innerHTML = '★';
                    visualStarsContainer.appendChild(star);
                }
                
                // Add rating text
                const ratingText = document.createElement('span');
                ratingText.style.marginLeft = '10px';
                ratingText.style.fontWeight = '600';
                ratingText.textContent = `(${rating}/10)`;
                visualStarsContainer.appendChild(ratingText);
            }
            
            // Image slider functionality
            const sliderContainer = document.querySelector('.slider-container');
            const slides = document.querySelectorAll('.slide');
            const dots = document.querySelectorAll('.slider-dot');
            const prevArrow = document.querySelector('.slider-arrow.prev');
            const nextArrow = document.querySelector('.slider-arrow.next');
            let currentSlide = 0;
            
            function updateSlider() {
                sliderContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
                
                // Update dots
                dots.forEach((dot, index) => {
                    if (index === currentSlide) {
                        dot.classList.add('active');
                    } else {
                        dot.classList.remove('active');
                    }
                });
            }
            
            prevArrow.addEventListener('click', function() {
                currentSlide = (currentSlide === 0) ? slides.length - 1 : currentSlide - 1;
                updateSlider();
            });
            
            nextArrow.addEventListener('click', function() {
                currentSlide = (currentSlide === slides.length - 1) ? 0 : currentSlide + 1;
                updateSlider();
            });
            
            dots.forEach((dot, index) => {
                dot.addEventListener('click', function() {
                    currentSlide = index;
                    updateSlider();
                });
            });
            
            // Auto advance slides
            setInterval(() => {
                currentSlide = (currentSlide === slides.length - 1) ? 0 : currentSlide + 1;
                updateSlider();
            }, 5000);
            
            // Donation options
            const donationOptions = document.querySelectorAll('.donation-option');
            const customDonationInput = document.querySelector('.custom-donation input');
            
            donationOptions.forEach(option => {
                option.addEventListener('click', function() {
                    donationOptions.forEach(opt => opt.classList.remove('selected'));
                    this.classList.add('selected');
                    customDonationInput.value = '';
                });
            });
            
            customDonationInput.addEventListener('focus', function() {
                donationOptions.forEach(opt => opt.classList.remove('selected'));
            });
            
            // Report modal functionality
            const reportBtn = document.getElementById('report-btn');
            const reportModal = document.getElementById('report-modal');
            const cancelReportBtn = document.getElementById('cancel-report');
            const submitReportBtn = document.getElementById('submit-report');
            
            reportBtn.addEventListener('click', function() {
                reportModal.style.display = 'flex';
            });
            
            cancelReportBtn.addEventListener('click', function() {
                reportModal.style.display = 'none';
            });
            
            submitReportBtn.addEventListener('click', function() {
                const selectedReason = document.querySelector('input[name="report-reason"]:checked');
                if (selectedReason) {
                    alert('Thank you for your report. We will review it shortly.');
                    reportModal.style.display = 'none';
                } else {
                    alert('Please select a reason for reporting');
                }
            });
            
            // Close modal if clicked outside
            window.addEventListener('click', function(event) {
                if (event.target === reportModal) {
                    reportModal.style.display = 'none';
                }
            });
            
            // Comment reporting
            const reportCommentButtons = document.querySelectorAll('.report-comment');
            reportCommentButtons.forEach(button => {
                button.addEventListener('click', function() {
                    alert('Comment reported. Thank you for your feedback.');
                });
            });
        });