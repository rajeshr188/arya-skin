(function () {
  "use strict";

  const configNode = document.getElementById("analytics-config");
  if (!configNode) {
    return;
  }

  let config;
  try {
    config = JSON.parse(configNode.textContent);
  } catch (error) {
    return;
  }

  const providerPatterns = {
    ga4: /^G-[A-Z0-9]+$/,
    gtm: /^GTM-[A-Z0-9]+$/,
  };
  if (
    !providerPatterns[config.provider] ||
    !providerPatterns[config.provider].test(config.tracking_id)
  ) {
    return;
  }

  const consentKey = "arya_skin_analytics_consent_v1";
  const allowedEvents = new Set([
    "phone_click",
    "whatsapp_click",
    "directions_click",
    "appointment_click",
    "appointment_form_submit",
    "clinic_view",
    "treatment_view",
  ]);
  const safeValuePattern = /^[a-z0-9_-]{1,100}$/;
  const banner = document.getElementById("analytics-consent");
  const manageButton = document.querySelector("[data-analytics-consent='manage']");
  const firedOnLoad = new WeakSet();
  let analyticsReady = false;

  window.dataLayer = window.dataLayer || [];

  function gtag() {
    window.dataLayer.push(arguments);
  }

  function readConsent() {
    try {
      return window.localStorage.getItem(consentKey);
    } catch (error) {
      return null;
    }
  }

  function saveConsent(value) {
    try {
      window.localStorage.setItem(consentKey, value);
    } catch (error) {
      // A blocked storage API must not cause analytics to load implicitly.
    }
  }

  function consentState(value) {
    return {
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      analytics_storage: value,
      functionality_storage: "denied",
      personalization_storage: "denied",
      security_storage: "granted",
    };
  }

  function addScript(source) {
    const script = document.createElement("script");
    script.async = true;
    script.src = source;
    document.head.appendChild(script);
  }

  function addTagManagerFallback(containerId) {
    const iframe = document.createElement("iframe");
    iframe.src =
      "https://www.googletagmanager.com/ns.html?id=" +
      encodeURIComponent(containerId);
    iframe.height = "0";
    iframe.width = "0";
    iframe.hidden = true;
    iframe.title = "Google Tag Manager";
    document.body.appendChild(iframe);
  }

  function safeValue(value) {
    const normalized = String(value || "").toLowerCase();
    return safeValuePattern.test(normalized) ? normalized : "";
  }

  function eventParameters(element) {
    const body = document.body.dataset;
    const elementData = element.dataset;
    const values = {
      page_type: elementData.analyticsPageType || body.analyticsPageType,
      clinic_slug: elementData.analyticsClinic || body.analyticsClinic,
      treatment_slug:
        elementData.analyticsTreatment || body.analyticsTreatment,
      success_state: elementData.analyticsSuccess,
    };
    return Object.fromEntries(
      Object.entries(values)
        .map(([key, value]) => [key, safeValue(value)])
        .filter(([, value]) => Boolean(value)),
    );
  }

  function sendEvent(element, eventName) {
    if (!analyticsReady || !allowedEvents.has(eventName)) {
      return;
    }
    const parameters = eventParameters(element);
    if (config.provider === "ga4") {
      gtag("event", eventName, parameters);
    } else {
      window.dataLayer.push({ event: eventName, ...parameters });
    }
  }

  function fireOnLoadEvents() {
    document
      .querySelectorAll("[data-analytics-event-on-load]")
      .forEach(function (element) {
        if (firedOnLoad.has(element)) {
          return;
        }
        firedOnLoad.add(element);
        sendEvent(element, element.dataset.analyticsEventOnLoad);
      });
  }

  function loadAnalytics() {
    if (analyticsReady) {
      return;
    }

    gtag("consent", "default", consentState("denied"));
    gtag("consent", "update", consentState("granted"));

    if (config.provider === "ga4") {
      addScript(
        "https://www.googletagmanager.com/gtag/js?id=" +
          encodeURIComponent(config.tracking_id),
      );
      gtag("js", new Date());
      gtag("config", config.tracking_id, {
        allow_ad_personalization_signals: false,
        allow_google_signals: false,
      });
    } else {
      window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
      addScript(
        "https://www.googletagmanager.com/gtm.js?id=" +
          encodeURIComponent(config.tracking_id),
      );
      addTagManagerFallback(config.tracking_id);
    }

    analyticsReady = true;
    fireOnLoadEvents();
  }

  function showBanner() {
    if (banner) {
      banner.hidden = false;
      const firstButton = banner.querySelector("button");
      if (firstButton) {
        firstButton.focus();
      }
    }
  }

  function hideBanner() {
    if (banner) {
      banner.hidden = true;
    }
  }

  document.addEventListener("click", function (event) {
    const action = event.target.closest("[data-analytics-event]");
    if (action) {
      sendEvent(action, action.dataset.analyticsEvent);
    }

    const consentButton = event.target.closest("[data-analytics-consent]");
    if (!consentButton) {
      return;
    }
    const choice = consentButton.dataset.analyticsConsent;
    if (choice === "accept") {
      saveConsent("granted");
      hideBanner();
      loadAnalytics();
    } else if (choice === "decline") {
      saveConsent("denied");
      if (analyticsReady) {
        gtag("consent", "update", consentState("denied"));
        analyticsReady = false;
      }
      hideBanner();
      if (manageButton) {
        manageButton.focus();
      }
    } else if (choice === "manage") {
      showBanner();
    }
  });

  const savedConsent = readConsent();
  if (savedConsent === "granted") {
    loadAnalytics();
  } else if (savedConsent !== "denied") {
    showBanner();
  }
})();
