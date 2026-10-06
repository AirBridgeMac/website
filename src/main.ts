import "./style.css";
import {
  createIcons,
  ArrowDown,
  ArrowDownToLine,
  ArrowDownUp,
  ArrowUp,
  ArrowUpRight,
  Bell,
  Check,
  Clipboard,
  ClipboardCheck,
  Files,
  Fingerprint,
  Menu,
  Monitor,
  MonitorDown,
  Moon,
  PictureInPicture2,
  Plus,
  QrCode,
  ScanLine,
  SlidersHorizontal,
  Smartphone,
  Sparkles,
  Sun,
  ToggleRight,
  UserRoundCheck,
  Wifi,
  X,
  Clock,
} from "lucide";

const iconSet = {
  ArrowDown,
  ArrowDownToLine,
  ArrowDownUp,
  ArrowUp,
  ArrowUpRight,
  Bell,
  Check,
  Clipboard,
  ClipboardCheck,
  Files,
  Fingerprint,
  Menu,
  Monitor,
  MonitorDown,
  Moon,
  PictureInPicture2,
  Plus,
  QrCode,
  ScanLine,
  SlidersHorizontal,
  Smartphone,
  Sparkles,
  Sun,
  ToggleRight,
  UserRoundCheck,
  Wifi,
  X,
  Clock,
};
const renderIcons = () =>
  createIcons({ icons: iconSet, attrs: { "aria-hidden": "true" } });
const root = document.documentElement;
const siteBase = import.meta.env.BASE_URL;
const themeButton = document.querySelector<HTMLButtonElement>(".theme-toggle");
const preferredTheme = matchMedia("(prefers-color-scheme: dark)");
let explicitTheme: string | null = null;
try {
  explicitTheme = localStorage.getItem("airbridge-site-theme");
} catch {
  /* Storage may be blocked. */
}
if (explicitTheme !== "light" && explicitTheme !== "dark") explicitTheme = null;

function applyTheme(theme: "light" | "dark") {
  root.dataset.theme = theme;
  const label = `Switch to ${theme === "light" ? "dark" : "light"} mode`;
  if (themeButton) {
    themeButton.setAttribute("aria-label", label);
    themeButton.title = label;
    themeButton.innerHTML = `<i data-lucide="${theme === "light" ? "moon" : "sun"}"></i>`;
  }
  document
    .querySelectorAll<HTMLImageElement>("[data-themed]")
    .forEach((image) => {
      image.src = `${siteBase}images/${image.dataset.themed}-${theme}.webp`;
    });
  document
    .querySelector('meta[name="theme-color"]')
    ?.setAttribute("content", theme === "light" ? "#f6f8f6" : "#181a1e");
  renderIcons();
}
applyTheme(root.dataset.theme === "dark" ? "dark" : "light");
themeButton?.addEventListener("click", () => {
  const theme = root.dataset.theme === "dark" ? "light" : "dark";
  explicitTheme = theme;
  try {
    localStorage.setItem("airbridge-site-theme", theme);
  } catch {
    /* The in-memory choice still works. */
  }
  applyTheme(theme);
});
preferredTheme.addEventListener("change", (event) => {
  if (!explicitTheme) applyTheme(event.matches ? "dark" : "light");
});

const menuButton = document.querySelector<HTMLButtonElement>(".menu-toggle");
const mobileNav = document.querySelector<HTMLElement>("#mobile-nav");
function setMenu(open: boolean) {
  if (!menuButton || !mobileNav) return;
  mobileNav.hidden = !open;
  menuButton.setAttribute("aria-expanded", String(open));
  menuButton.setAttribute(
    "aria-label",
    open ? "Close navigation" : "Open navigation",
  );
  menuButton.innerHTML = `<i data-lucide="${open ? "x" : "menu"}"></i>`;
  renderIcons();
}
menuButton?.addEventListener("click", () =>
  setMenu(menuButton.getAttribute("aria-expanded") !== "true"),
);
mobileNav
  ?.querySelectorAll("a")
  .forEach((link) => link.addEventListener("click", () => setMenu(false)));
document.addEventListener("pointerdown", (event) => {
  if (event.target instanceof Element && !event.target.closest(".site-header"))
    setMenu(false);
});
document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    menuButton?.getAttribute("aria-expanded") === "true"
  ) {
    setMenu(false);
    menuButton.focus();
  }
});
matchMedia("(min-width: 801px)").addEventListener("change", (event) => {
  if (event.matches) setMenu(false);
});

const tabs = [...document.querySelectorAll<HTMLButtonElement>('[role="tab"]')];
function selectTab(tab: HTMLButtonElement, focus = false) {
  tabs.forEach((item) => {
    const selected = item === tab;
    item.setAttribute("aria-selected", String(selected));
    item.tabIndex = selected ? 0 : -1;
    const panel = document.getElementById(
      item.getAttribute("aria-controls") ?? "",
    );
    if (panel) panel.hidden = !selected;
  });
  if (focus) tab.focus({ preventScroll: true });
}
tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectTab(tab));
  tab.addEventListener("keydown", (event) => {
    const next =
      event.key === "ArrowRight"
        ? (index + 1) % tabs.length
        : event.key === "ArrowLeft"
          ? (index - 1 + tabs.length) % tabs.length
          : event.key === "Home"
            ? 0
            : event.key === "End"
              ? tabs.length - 1
              : null;
    if (next === null) return;
    event.preventDefault();
    selectTab(tabs[next], true);
  });
});

// Only explicitly configured HTTPS release assets become download links.
function releaseUrl(value: unknown): string | null {
  if (typeof value !== "string" || !value.trim()) return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password
      ? url.href
      : null;
  } catch {
    return null;
  }
}
const releases = {
  mac: releaseUrl(import.meta.env.VITE_MAC_DOWNLOAD_URL),
  android: releaseUrl(import.meta.env.VITE_ANDROID_DOWNLOAD_URL),
};
const dialogRoot = document.querySelector("#dialog-root");
if (dialogRoot) {
  dialogRoot.innerHTML = `<dialog class="download-dialog" aria-labelledby="download-title" aria-describedby="download-description">
    <div class="dialog-inner"><button class="icon-button dialog-close" aria-label="Close download panel"><i data-lucide="x"></i></button>
    <img class="dialog-brand" src="${siteBase}images/logo.webp" width="52" height="52" alt="" />
    <p class="eyebrow">TWO APPS. ONE CONNECTION.</p><h2 id="download-title">Get AirBridge.</h2>
    <p id="download-description" class="dialog-intro">You'll need AirBridge on both your Mac and Android phone. Public release builds are still being prepared.</p>
    <div class="download-options"><section class="download-option"><i data-lucide="monitor"></i><h3>AirBridge for Mac</h3><p>macOS 14 or later<br />Mac app and menu-bar companion</p><div data-release="mac"></div></section>
    <section class="download-option"><i data-lucide="smartphone"></i><h3>AirBridge for Android</h3><p>Android 8 or later<br />Phone app and optional keyboard</p><div data-release="android"></div></section></div>
    <p class="download-note">Currently in private preview. Not yet distributed through the App Store or Google Play. The Mac preview is not notarized for public distribution.</p>
    <div class="dialog-links"><a href="${siteBase}guide/">Read the setup guide</a><a href="${siteBase}privacy/">Privacy, plainly</a></div></div></dialog>`;
  for (const platform of ["mac", "android"] as const) {
    const slot = dialogRoot.querySelector(`[data-release="${platform}"]`)!;
    const url = releases[platform];
    if (url) {
      const link = document.createElement("a");
      link.className = "button";
      link.href = url;
      link.rel = "noopener noreferrer";
      link.innerHTML = `Download ${platform === "mac" ? "for Mac" : "APK"} <i data-lucide="arrow-down-to-line"></i>`;
      slot.append(link);
    } else
      slot.innerHTML =
        '<p class="unavailable"><i data-lucide="clock"></i>Public build coming soon</p>';
  }
  if (releases.mac || releases.android) {
    dialogRoot.querySelector("#download-description")!.textContent =
      "You'll need AirBridge on both devices. Available preview builds are listed below; these are not store releases.";
  }
  const dialog = dialogRoot.querySelector<HTMLDialogElement>("dialog")!;
  let opener: HTMLElement | null = null;
  let savedOverflow = "";
  document
    .querySelectorAll<HTMLButtonElement>("[data-download]")
    .forEach((button) =>
      button.addEventListener("click", () => {
        opener = button;
        setMenu(false);
        savedOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        dialog.showModal();
      }),
    );
  dialog
    .querySelector(".dialog-close")
    ?.addEventListener("click", () => dialog.close());
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const controls = [
      ...dialog.querySelectorAll<HTMLElement>("button:not(:disabled), a[href]"),
    ];
    const first = controls[0],
      last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  });
  dialog.addEventListener("click", (event) => {
    const rect = dialog.getBoundingClientRect();
    if (
      event.target === dialog &&
      (event.clientX < rect.left ||
        event.clientX > rect.right ||
        event.clientY < rect.top ||
        event.clientY > rect.bottom)
    )
      dialog.close();
  });
  dialog.addEventListener("close", () => {
    document.body.style.overflow = savedOverflow;
    opener?.focus({ preventScroll: true });
  });
}
document.querySelectorAll("[data-year]").forEach((element) => {
  element.textContent = String(new Date().getFullYear());
});
document.querySelector("[data-top]")?.addEventListener("click", () => {
  window.scrollTo({
    top: 0,
    behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "instant"
      : "smooth",
  });
  document
    .querySelector<HTMLAnchorElement>(".site-header .brand")
    ?.focus({ preventScroll: true });
});
renderIcons();
