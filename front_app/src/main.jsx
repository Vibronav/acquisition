import React from "react";
import ReactDOM from "react-dom/client";
import { IntlProvider, createIntl, createIntlCache } from "react-intl";
import messagesEn from "../src/languages/en.json";
import messagesPl from "../src/languages/pl.json";
import App from "./App.jsx";

let currentLocale = 'en';
const cache = createIntlCache();
const messages = {
  en: messagesEn,
  pl: messagesPl,
}
export const intl = createIntl(
  {
    locale: currentLocale,
    messages: messages[currentLocale],
  },
  cache
);
export const setLocale = (locale) => {
  currentLocale = locale;
  intl.locale = locale;
  intl.messages = messages[locale];
  console.log(intl.messages)
};

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <IntlProvider locale={intl.locale} messages={intl.messages}>
      <App />    
    </IntlProvider>
  </React.StrictMode>
);
