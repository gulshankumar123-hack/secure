const searchInput = document.querySelector("#product-search");
const filterButtons = document.querySelectorAll("[data-product-filter]");
const productCards = [...document.querySelectorAll(".product-card")];
const productStatus = document.querySelector("#product-status");
const emptyState = document.querySelector("#product-empty");
let activeCategory = "all";

function addProductEnquiryLinks() {
    productCards.forEach((card) => {
        const cardCopy = card.querySelector(".card-copy");
        const productName = card.querySelector("h3")?.textContent.trim();
        if (!cardCopy || !productName || cardCopy.querySelector(".product-inquiry")) return;

        const enquiryLink = document.createElement("a");
        const message = `Hello, I am interested in ${productName}. Please share more details.`;
        enquiryLink.className = "product-inquiry";
        enquiryLink.href = `https://wa.me/919814571695?text=${encodeURIComponent(message)}`;
        enquiryLink.target = "_blank";
        enquiryLink.rel = "noopener noreferrer";
        enquiryLink.textContent = "Enquire on WhatsApp";
        cardCopy.append(enquiryLink);
    });
}

function enableProductImagePreview() {
    const images = document.querySelectorAll(".product-card img, .gallery-card img");
    if (images.length === 0) return;

    const dialog = document.createElement("dialog");
    dialog.className = "image-preview";
    dialog.setAttribute("aria-label", "Product image preview");

    const closeButton = document.createElement("button");
    closeButton.className = "image-preview-close";
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "Close image preview");
    closeButton.textContent = "×";

    const previewImage = document.createElement("img");
    const caption = document.createElement("p");
    caption.className = "image-preview-caption";
    dialog.append(closeButton, previewImage, caption);
    document.body.append(dialog);

    const openPreview = (image) => {
        previewImage.src = image.currentSrc || image.src;
        previewImage.alt = image.alt;
        caption.textContent = image.alt;
        dialog.showModal();
        closeButton.focus();
    };

    images.forEach((image) => {
        image.tabIndex = 0;
        image.setAttribute("role", "button");
        image.setAttribute("aria-haspopup", "dialog");
        image.setAttribute("aria-label", `View larger image: ${image.alt}`);
        image.addEventListener("click", () => openPreview(image));
        image.addEventListener("keydown", (event) => {
            if (event.key !== "Enter" && event.key !== " ") return;
            event.preventDefault();
            openPreview(image);
        });
    });

    closeButton.addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });
}

function addQuickContactActions() {
    const actions = document.createElement("div");
    actions.className = "quick-contact";
    actions.setAttribute("aria-label", "Quick contact");

    const whatsapp = document.createElement("a");
    whatsapp.className = "quick-contact-link quick-contact-whatsapp";
    whatsapp.href = "https://wa.me/919814571695";
    whatsapp.target = "_blank";
    whatsapp.rel = "noopener noreferrer";
    whatsapp.setAttribute("aria-label", "Chat with us on WhatsApp");
    whatsapp.innerHTML = '<svg class="quick-contact-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11.6a8 8 0 0 1-11.8 7l-4.2 1.1 1.1-4.1A8 8 0 1 1 20 11.6Z"/><path d="M9 8.5c.2-.4.4-.4.7-.4h.5c.2 0 .4.1.5.4l.7 1.6c.1.2.1.4 0 .5l-.5.6c-.2.2-.2.4-.1.6.4.7 1 1.3 1.7 1.7.2.1.4.1.6-.1l.6-.6c.2-.2.4-.2.6-.1l1.5.7c.3.1.4.3.4.5 0 .5-.2 1-.5 1.3-.4.4-1 .6-1.6.5-1.4-.2-3-1-4.4-2.4-1.2-1.2-2-2.6-2.2-3.8-.1-.5.1-1 .5-1.4.2-.2.6-.4 1-.4Z"/></svg><span>WhatsApp</span>';

    const call = document.createElement("a");
    call.className = "quick-contact-link quick-contact-call";
    call.href = "tel:+919814573978";
    call.setAttribute("aria-label", "Call Star Engineering Tools");
    call.innerHTML = '<svg class="quick-contact-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h2.5l1.2 4-1.8 1.8a15 15 0 0 0 5.8 5.8l1.8-1.8 4 1.2V17c0 1.1-.9 2-2 2A15.5 15.5 0 0 1 5 5.5c0-1.1.9-2 2-2Z"/></svg><span>Call us</span>';

    actions.append(whatsapp, call);
    document.body.append(actions);
}

function categoryForCard(card) {
    const tag = card.querySelector(".product-tag")?.textContent.toLowerCase() ?? "";
    if (tag.includes("broach") || tag.includes("tooling")) return "broach";
    if (tag.includes("yoke")) return "yoke";
    if (tag.includes("pto")) return "pto";
    return "other";
}

function filterProducts() {
    if (!searchInput || !productStatus || !emptyState) return;

    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    productCards.forEach((card) => {
        const productName = card.querySelector("h3")?.textContent ?? "";
        const description = card.querySelector(".card-copy p")?.textContent ?? "";
        const productTag = card.querySelector(".product-tag")?.textContent ?? "";
        const imageAlt = card.querySelector("img")?.alt ?? "";
        const searchableText = `${productName} ${description} ${productTag} ${imageAlt}`.toLowerCase();
        const matches = (activeCategory === "all" || categoryForCard(card) === activeCategory)
            && searchableText.includes(query);

        card.hidden = !matches;
        if (matches) visibleCount += 1;
    });

    document.querySelectorAll("[data-product-section]").forEach((section) => {
        section.hidden = !section.querySelector(".product-card:not([hidden])");
    });

    productStatus.textContent = `Showing ${visibleCount} of ${productCards.length} products`;
    emptyState.hidden = visibleCount !== 0;
}

if (searchInput && productCards.length > 0) {
    searchInput.addEventListener("input", filterProducts);

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            activeCategory = button.dataset.productFilter ?? "all";
            filterButtons.forEach((filterButton) => {
                filterButton.setAttribute("aria-pressed", String(filterButton === button));
            });
            filterProducts();
        });
    });

    filterProducts();
}

addProductEnquiryLinks();
enableProductImagePreview();
addQuickContactActions();

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealTargets = document.querySelectorAll(
    ".section-heading, .product-card, .gallery-card, .value-card, .contact-grid .info-card, .callout, .split-image",
);

if (!reduceMotion && "IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.12, rootMargin: "0px 0px -35px 0px" });

    revealTargets.forEach((element) => {
        element.classList.add("reveal");
        revealObserver.observe(element);
    });
}

const introScreen = document.querySelector("#site-intro");
const introRobot = introScreen?.querySelector(".intro-robot");
const introContinue = document.querySelector("#intro-continue");

if (introScreen && introRobot instanceof SVGElement && introContinue instanceof HTMLButtonElement) {
    introRobot.addEventListener("animationend", (event) => {
        if (event.animationName !== "intro-travel") return;
        introScreen.classList.add("intro-ready");
        introContinue.disabled = false;
        introContinue.focus();
    }, { once: true });

    introContinue.addEventListener("click", () => {
        introScreen.classList.add("intro-leaving");
        introScreen.setAttribute("aria-hidden", "true");
        introContinue.disabled = true;

        window.setTimeout(() => {
            introScreen.hidden = true;
            document.body.classList.remove("intro-active");
            document.querySelectorAll("[inert]").forEach((element) => element.removeAttribute("inert"));
            document.querySelector("#home")?.focus({ preventScroll: true });
        }, reduceMotion ? 0 : 450);
    });
}
