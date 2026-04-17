const toggle = document.querySelector(".nav-toggle");
const drawer = document.getElementById("drawer");
const overlay = document.getElementById("drawerOverlay");

function openDrawer() {
  document.body.classList.add("drawer-open");
  toggle.classList.add("open");
  toggle.setAttribute("aria-expanded", "true");
  drawer.setAttribute("aria-hidden", "false");
  overlay.hidden = false;
}

function closeDrawer() {
  document.body.classList.remove("drawer-open");
  toggle.classList.remove("open");
  toggle.setAttribute("aria-expanded", "false");
  drawer.setAttribute("aria-hidden", "true");
  overlay.hidden = true;
}

if (toggle && drawer && overlay) {
  toggle.addEventListener("click", () => {
    const isOpen = document.body.classList.contains("drawer-open");
    isOpen ? closeDrawer() : openDrawer();
  });

  overlay.addEventListener("click", closeDrawer);

  drawer.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", closeDrawer);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && document.body.classList.contains("drawer-open")) {
      closeDrawer();
    }
  });
}

// Fade-in + fade-out on scroll for elements with .reveal
const revealEls = document.querySelectorAll(".reveal");

if (revealEls.length) {
  const obs = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        entry.target.classList.toggle("is-visible", entry.isIntersecting);
      });
    },
    {
      threshold: 0.25,
    }
  );

  revealEls.forEach((el) => obs.observe(el));
}

// Run page enhancements after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  // Themed date picker
  const dateInput = document.querySelector("#event_date");
  if (dateInput && window.flatpickr) {
    flatpickr(dateInput, {
      dateFormat: "Y-m-d",
      minDate: "today",
      disableMobile: true,
    });
  }

  // AJAX contact form
  const contactForm = document.getElementById("contact-form");
  const submitBtn = document.getElementById("contact-submit-btn");
  const submitText = submitBtn?.querySelector(".contact-submit-text");

  if (contactForm && submitBtn && submitText) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const originalText = "Send";
      submitBtn.classList.remove("is-success", "is-error");
      submitBtn.classList.add("is-loading");
      submitText.textContent = "Sending...";

      try {
        const formData = new FormData(contactForm);

        const response = await fetch(contactForm.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        const data = await response.json();

        submitBtn.classList.remove("is-loading");

        if (response.ok && data.ok) {
          submitBtn.classList.add("is-success");
          submitText.textContent = data.message || "Inquiry Sent!";

          contactForm.reset();

          setTimeout(() => {
            submitBtn.classList.remove("is-success");
            submitText.textContent = originalText;
          }, 3000);
        } else {
          submitBtn.classList.add("is-error");
          submitText.textContent = data.message || "Try Again";

          setTimeout(() => {
            submitBtn.classList.remove("is-error");
            submitText.textContent = originalText;
          }, 3000);
        }
      } catch (err) {
        console.error("FORM SUBMIT ERROR:", err);

        submitBtn.classList.remove("is-loading");
        submitBtn.classList.add("is-error");
        submitText.textContent = "Try Again";

        setTimeout(() => {
          submitBtn.classList.remove("is-error");
          submitText.textContent = originalText;
        }, 3000);
      }
    });
  }

  // Auto-hide old flash message if it still exists
  const contactFlash = document.getElementById("contact-flash");
  if (contactFlash) {
    setTimeout(() => {
      contactFlash.classList.add("is-fading");

      setTimeout(() => {
        contactFlash.remove();
      }, 500);
    }, 3500);
  }
});