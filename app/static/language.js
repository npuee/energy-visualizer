
// language.js: Multi-language support for all static UI text in index.html and related templates.
//
// Usage:
//   - All UI strings are in LANGUAGES (add more languages as needed).
//   - Use setLanguage('en'), setLanguage('et'), etc. to switch language at runtime.
//   - Use getLang() to get the current language object for UI rendering.
//   - LANG is provided for legacy compatibility (returns the current language).
//
// Example:
//   setLanguage('et'); // Switch to Estonian
//   const lang = getLang();
//   document.title = lang.TITLE;


const LANGUAGES = {
  en: {
    TITLE: 'Energy Daily Visualization',
    PLOT_TITLE: 'Daily consumption (kWh)',
    X_AXIS: 'Date',
    Y_AXIS: 'kWh',
    LEGEND_TOTAL: 'Total',
    SUMMARY_TOTAL: 'Total kWh',
    SUMMARY_AVG: 'Avg / day (kWh)',
    SUMMARY_MIN: 'Min day (kWh)',
    SUMMARY_MAX: 'Max day (kWh)',
    SUMMARY_TODAY: 'Today (kWh)',
    DATA_UPDATED: 'Data updated:',
  },
  et: {
    TITLE: 'Energia päevane visualiseerimine',
    PLOT_TITLE: 'Päevane tarbimine (kWh)',
    X_AXIS: 'Kuupäev',
    Y_AXIS: 'kWh',
    LEGEND_TOTAL: 'Kokku',
    SUMMARY_TOTAL: 'Kokku kWh',
    SUMMARY_AVG: 'Keskmine / päev (kWh)',
    SUMMARY_MIN: 'Min päev (kWh)',
    SUMMARY_MAX: 'Max päev (kWh)',
    SUMMARY_TODAY: 'Täna (kWh)',
    DATA_UPDATED: 'Andmed uuendatud:',
  }
};

let currentLang = 'en';

function setLanguage(langCode) {
  if (LANGUAGES[langCode]) {
    currentLang = langCode;
  }
}

function getLang() {
  return LANGUAGES[currentLang];
}

// For legacy compatibility:
const LANG = getLang();
