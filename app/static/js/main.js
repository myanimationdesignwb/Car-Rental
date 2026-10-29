document.addEventListener('DOMContentLoaded', function () {
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  if (menuToggle && nav) {
    menuToggle.addEventListener('click', function () {
      nav.classList.toggle('mobile-open');
      nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
      nav.style.position = 'absolute';
      nav.style.top = '100%';
      nav.style.left = '1rem';
      nav.style.right = '1rem';
      nav.style.flexDirection = 'column';
      nav.style.background = '#0b1320';
      nav.style.padding = '1rem';
      nav.style.borderRadius = '16px';
    });
  }

  const tabButtons = document.querySelectorAll('[data-tabs] .tab-button');
  const vehicleCards = document.querySelectorAll('.vehicle-card');

  const applyCategoryFilter = function (category) {
    vehicleCards.forEach(function (card) {
      const matches = category === 'all' || card.dataset.category === category;
      card.style.display = matches ? '' : 'none';
    });
  };

  tabButtons.forEach(function (button) {
    button.addEventListener('click', function () {
      tabButtons.forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      applyCategoryFilter(button.dataset.category || 'all');
    });
  });

  if (tabButtons.length) {
    const activeTab = document.querySelector('[data-tabs] .tab-button.active');
    applyCategoryFilter((activeTab && activeTab.dataset.category) || 'all');
  }

  const bookingSteps = document.querySelectorAll('.booking-step');
  const stepper = document.querySelectorAll('.stepper .step');
  const nextBtn = document.querySelector('[data-next-step]');
  const prevBtn = document.querySelector('[data-prev-step]');
  const submitBtn = document.querySelector('[data-submit-step]');
  const form = document.querySelector('.booking-form');
  const ownerWhatsapp = document.body && document.body.dataset.ownerWhatsapp ? document.body.dataset.ownerWhatsapp : '9608576670';
  let currentStep = 0;

  const buildWhatsAppUrl = function () {
    const tripType = form ? form.querySelector('[name="trip_type"]')?.value || 'Trip' : 'Trip';
    const pickup = form ? form.querySelector('[name="pickup_location"]')?.value || 'Not specified' : 'Not specified';
    const drop = form ? form.querySelector('[name="drop_location"]')?.value || 'Not specified' : 'Not specified';
    const pickupDate = form ? form.querySelector('[name="pickup_date"]')?.value || 'Not specified' : 'Not specified';
    const pickupTime = form ? form.querySelector('[name="pickup_time"]')?.value || 'Not specified' : 'Not specified';
    const customerName = form ? form.querySelector('[name="customer_name"]')?.value || 'Not specified' : 'Not specified';
    const customerPhone = form ? form.querySelector('[name="customer_phone"]')?.value || 'Not specified' : 'Not specified';
    const customerEmail = form ? form.querySelector('[name="customer_email"]')?.value || 'Not provided' : 'Not provided';
    const vehicleName = form ? form.querySelector('input[name="vehicle_id"]:checked + span')?.textContent || 'Not selected' : 'Not selected';
    const passengers = form ? form.querySelector('[name="passengers"]')?.value || 'Not specified' : 'Not specified';
    const notes = form ? form.querySelector('[name="notes"]')?.value || 'No extra notes' : 'No extra notes';

    const message = [
      'Hi Rohit Transport,',
      '',
      'I want to book a ride. Please confirm the fare and availability.',
      '',
      '*Booking Details*',
      `Customer Name: ${customerName}`,
      `Phone: ${customerPhone}`,
      `Email: ${customerEmail}`,
      `Vehicle: ${vehicleName}`,
      `Trip Type: ${tripType}`,
      `Route: ${pickup} to ${drop}`,
      `Pickup Date: ${pickupDate}`,
      `Pickup Time: ${pickupTime}`,
      `Passengers: ${passengers}`,
      `Notes: ${notes}`,
      '',
      'Please share the final price and confirm the trip.'
    ].join('\n');

    return `https://wa.me/${ownerWhatsapp}?text=${encodeURIComponent(message)}`;
  };

  const syncRequiredFields = function () {
    bookingSteps.forEach((step, stepIndex) => {
      const isActive = stepIndex === currentStep;
      const fields = step.querySelectorAll('input, select, textarea');

      fields.forEach((field) => {
        const isInitiallyRequired = field.hasAttribute('required');
        field.required = isActive && isInitiallyRequired;
      });
    });
  };

  const validateStep = function (stepIndex) {
    const step = bookingSteps[stepIndex];
    if (!step) return true;

    const requiredFields = step.querySelectorAll('input[required], select[required], textarea[required]');
    for (const field of requiredFields) {
      if (!field.checkValidity()) {
        field.reportValidity();
        return false;
      }
    }

    if (stepIndex === 1) {
      const selectedVehicle = step.querySelector('input[name="vehicle_id"]:checked');
      if (!selectedVehicle) {
        alert('Please select a vehicle before continuing.');
        return false;
      }
    }

    return true;
  };

  const updateBookingUI = function () {
    if (!bookingSteps.length) return;

    bookingSteps.forEach((step, index) => {
      step.classList.toggle('active', index === currentStep);
    });

    stepper.forEach((dot, index) => {
      dot.classList.toggle('active', index === currentStep);
    });

    syncRequiredFields();

    const isLastStep = currentStep === bookingSteps.length - 1;

    if (nextBtn) {
      nextBtn.style.display = isLastStep ? 'none' : 'inline-flex';
      nextBtn.type = 'button';
    }

    if (submitBtn) {
      submitBtn.style.display = isLastStep ? 'inline-flex' : 'none';
      submitBtn.type = 'submit';
    }

    if (prevBtn) {
      prevBtn.style.display = currentStep === 0 ? 'none' : 'inline-flex';
    }
  };

  if (prevBtn) {
    prevBtn.addEventListener('click', function () {
      if (currentStep > 0) {
        currentStep -= 1;
        updateBookingUI();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function (event) {
      event.preventDefault();

      if (!validateStep(currentStep)) {
        return;
      }

      if (currentStep < bookingSteps.length - 1) {
        currentStep += 1;
        updateBookingUI();
      }
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener('click', function (event) {
      event.preventDefault();

      if (!validateStep(currentStep)) {
        return;
      }

      const whatsappUrl = buildWhatsAppUrl();
      const popup = window.open(whatsappUrl, '_blank');
      if (!popup) {
        window.location.href = whatsappUrl;
      }

      if (form) {
        form.submit();
      }
    });
  }

  updateBookingUI();

  const revealItems = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.15 });
  revealItems.forEach((item) => observer.observe(item));

  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach((item) => {
    const btn = item.querySelector('.faq-question');
    if (!btn) return;
    btn.addEventListener('click', () => {
      faqItems.forEach((faq) => faq.classList.remove('active'));
      item.classList.add('active');
    });
  });
});
