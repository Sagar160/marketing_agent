// Mobile Menu Toggle
const menuBtn = document.querySelector('.menu-btn');
const navMenu = document.querySelector('nav ul');

if (menuBtn) {
  menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('active');
    menuBtn.classList.toggle('active');
  });
}

// Close menu when a link is clicked
const navLinks = document.querySelectorAll('nav ul li a');
navLinks.forEach(link => {
  link.addEventListener('click', () => {
    navMenu.classList.remove('active');
    menuBtn.classList.remove('active');
  });
});

// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Image Slider Functionality
class ImageSlider {
  constructor(sliderId) {
    this.slider = document.querySelector(sliderId);
    if (!this.slider) return;
    
    this.slides = this.slider.querySelectorAll('.slide');
    this.prevBtn = this.slider.querySelector('.prev');
    this.nextBtn = this.slider.querySelector('.next');
    this.currentSlide = 0;
    this.autoPlayInterval = null;
    
    this.init();
  }
  
  init() {
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', () => this.prevSlide());
    }
    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', () => this.nextSlide());
    }
    this.showSlide(0);
    this.autoPlay();
    
    // Pause on hover
    this.slider.addEventListener('mouseenter', () => this.stopAutoPlay());
    this.slider.addEventListener('mouseleave', () => this.autoPlay());
  }
  
  showSlide(n) {
    if (n >= this.slides.length) {
      this.currentSlide = 0;
    } else if (n < 0) {
      this.currentSlide = this.slides.length - 1;
    } else {
      this.currentSlide = n;
    }
    
    this.slides.forEach(slide => {
      slide.classList.remove('active');
      slide.style.opacity = '0';
      slide.style.transition = 'opacity 0.5s ease-in-out';
    });
    
    this.slides[this.currentSlide].classList.add('active');
    this.slides[this.currentSlide].style.opacity = '1';
  }
  
  nextSlide() {
    this.showSlide(this.currentSlide + 1);
  }
  
  prevSlide() {
    this.showSlide(this.currentSlide - 1);
  }
  
  autoPlay() {
    this.autoPlayInterval = setInterval(() => {
      this.nextSlide();
    }, 5000);
  }
  
  stopAutoPlay() {
    clearInterval(this.autoPlayInterval);
  }
}

// Initialize sliders
const gallerySlider = new ImageSlider('.gallery-slider');
const featuredSlider = new ImageSlider('.featured-slider');

// Breed Filter Functionality
class BreedFilter {
  constructor() {
    this.filterBtns = document.querySelectorAll('.filter-btn');
    this.breedCards = document.querySelectorAll('.breed-card');
    this.init();
  }
  
  init() {
    this.filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => this.filterBreeds(e));
    });
  }
  
  filterBreeds(e) {
    const category = e.target.getAttribute('data-filter');
    
    // Update active button
    this.filterBtns.forEach(btn => btn.classList.remove('active'));
    e.target.classList.add('active');
    
    // Filter cards
    this.breedCards.forEach(card => {
      const cardCategory = card.getAttribute('data-category');
      
      if (category === 'all' || cardCategory === category) {
        card.style.display = 'block';
        card.style.animation = 'fadeIn 0.5s ease-in';
      } else {
        card.style.display = 'none';
      }
    });
  }
}

const breedFilter = new BreedFilter();

// Fade-in animation
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(style);

// Lazy Loading Images
if ('IntersectionObserver' in window) {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src || img.src;
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  });
  
  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
}

// Form Validation
class FormValidator {
  constructor(formId) {
    this.form = document.querySelector(formId);
    if (!this.form) return;
    this.init();
  }
  
  init() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  handleSubmit(e) {
    e.preventDefault();
    
    if (this.validateForm()) {
      this.showMessage('Thank you! Your message has been sent successfully.', 'success');
      this.form.reset();
    } else {
      this.showMessage('Please fill in all required fields correctly.', 'error');
    }
  }
  
  validateForm() {
    const inputs = this.form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
      if (!input.value.trim()) {
        isValid = false;
        input.classList.add('error');
      } else {
        input.classList.remove('error');
      }
    });
    
    const emailInput = this.form.querySelector('input[type="email"]');
    if (emailInput && !this.validateEmail(emailInput.value)) {
      isValid = false;
      emailInput.classList.add('error');
    }
    
    return isValid;
  }
  
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  showMessage(message, type) {
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
      padding: 15px 20px;
      margin-bottom: 20px;
      border-radius: 8px;
      font-family: 'Roboto', sans-serif;
      animation: slideDown 0.3s ease-in;
      ${type === 'success' ? 'background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb;' : 'background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;'}
    `;
    
    this.form.insertBefore(messageEl, this.form.firstChild);
    
    setTimeout(() => {
      messageEl.remove();
    }, 5000);
  }
}

const contactForm = new FormValidator('#contact-form');

// Scroll to Top Button
const scrollTopBtn = document.querySelector('.scroll-top-btn');
if (scrollTopBtn) {
  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
      scrollTopBtn.classList.add('show');
    } else {
      scrollTopBtn.classList.remove('show');
    }
  });
  
  scrollTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

// Add animation on scroll for cards
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const cardObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      cardObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

document.querySelectorAll('.breed-card, .care-tip, .gallery-item').forEach(card => {
  cardObserver.observe(card);
});

// Tooltip functionality
const tooltips = document.querySelectorAll('[data-tooltip]');
tooltips.forEach(tooltip => {
  tooltip.addEventListener('mouseenter', function() {
    const tooltipText = this.getAttribute('data-tooltip');
    const tooltipEl = document.createElement('div');
    tooltipEl.className = 'tooltip';
    tooltipEl.textContent = tooltipText;
    tooltipEl.style.cssText = `
      position: absolute;
      background-color: #8B4513;
      color: #F5DEB3;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
      white-space: nowrap;
      z-index: 1000;
      font-family: 'Roboto', sans-serif;
    `;
    document.body.appendChild(tooltipEl);
    
    const rect = this.getBoundingClientRect();
    tooltipEl.style.top = (rect.top - tooltipEl.offsetHeight - 10) + 'px';
    tooltipEl.style.left = (rect.left + rect.width / 2 - tooltipEl.offsetWidth / 2) + 'px';
    
    this.tooltipEl = tooltipEl;
  });
  
  tooltip.addEventListener('mouseleave', function() {
    if (this.tooltipEl) {
      this.tooltipEl.remove();
    }
  });
});

// Keyboard Navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    navMenu.classList.remove('active');
    menuBtn.classList.remove('active');
  }
});

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  // Add animation class to elements
  const addAnimationClass = () => {
    document.querySelectorAll('.breed-card, .care-tip').forEach((el, index) => {
      el.style.animationDelay = `${index * 0.1}s`;
    });
  };
  addAnimationClass();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ImageSlider, BreedFilter, FormValidator };
}