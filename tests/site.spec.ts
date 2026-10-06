import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const sitePath = (path: string) =>
  `${process.env.SITE_BASE_PATH?.replace(/\/+$/, "") || ""}${path}`;

async function ready(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator("i[data-lucide]")).toHaveCount(0);
}

async function assertLayout(page: Page) {
  const issues = await page.evaluate(() => {
    const issues: string[] = [];
    if (document.documentElement.scrollWidth > innerWidth + 1)
      issues.push("Horizontal page overflow");
    for (const element of document.querySelectorAll<HTMLElement>(
      "h1,h2,h3,button,summary,.hero-meta,.feature-tabs,.nav-wrap",
    )) {
      if (!element.getClientRects().length) continue;
      const rect = element.getBoundingClientRect();
      if (element.scrollWidth > element.clientWidth + 2)
        issues.push(`Clipped text: ${element.textContent}`);
      if (rect.left < -1 || rect.right > innerWidth + 1)
        issues.push(`Outside viewport: ${element.textContent}`);
    }
    const copy = document.querySelector(".hero-copy")?.getBoundingClientRect();
    const art = document.querySelector(".hero-art")?.getBoundingClientRect();
    const hero = document.querySelector(".hero")?.getBoundingClientRect();
    if (copy && art && copy.bottom > art.top)
      issues.push("Hero copy overlaps product image");
    if (hero && hero.bottom > innerHeight - 20)
      issues.push("No next-section hint in first viewport");
    return issues;
  });
  expect(issues).toEqual([]);
}

test("home has working assets, no external tracking, and responsive light/dark layouts", async ({
  page,
}, testInfo) => {
  const errors: string[] = [];
  const external: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (!request.url().startsWith("http://127.0.0.1:4176"))
      external.push(request.url());
  });
  const sizes =
    testInfo.project.name === "mobile"
      ? [
          { width: 393, height: 851 },
          { width: 320, height: 568 },
          { width: 540, height: 720 },
        ]
      : [
          { width: 1440, height: 960 },
          { width: 1920, height: 1080 },
          { width: 1024, height: 768 },
          { width: 800, height: 1024 },
        ];
  for (const theme of ["light", "dark"] as const) {
    await page.emulateMedia({ colorScheme: theme, reducedMotion: "reduce" });
    await page.goto(sitePath("/"));
    await ready(page);
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    for (const size of sizes) {
      await page.setViewportSize(size);
      await page.evaluate(() => window.scrollTo(0, 0));
      await assertLayout(page);
      await page.screenshot({
        path: `artifacts/${testInfo.project.name}-${theme}-${size.width}.png`,
        fullPage: false,
      });
    }
    for (const image of await page.locator("img:visible").all()) {
      await image.scrollIntoViewIfNeeded();
      await expect
        .poll(() =>
          image.evaluate(
            (element: HTMLImageElement) =>
              element.complete && element.naturalWidth > 0,
          ),
        )
        .toBeTruthy();
    }
  }
  expect(errors).toEqual([]);
  expect(external).toEqual([]);
});

test("feature tabs support pointer and arrow-key navigation without moving focus into hidden content", async ({
  page,
}) => {
  await page.goto(sitePath("/"));
  await ready(page);
  for (const name of ["Clipboard", "Notifications", "Mirroring", "Files"]) {
    const tab = page.getByRole("tab", { name, exact: true });
    await tab.click();
    await expect(tab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("tabpanel")).toHaveCount(1);
    await expect(page.getByRole("tabpanel")).toHaveAttribute(
      "aria-labelledby",
      `tab-${name.toLowerCase()}`,
    );
  }
  await page.getByRole("tab", { name: "Files", exact: true }).focus();
  await page.keyboard.press("ArrowRight");
  await expect(
    page.getByRole("tab", { name: "Clipboard", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("End");
  await expect(
    page.getByRole("tab", { name: "Mirroring", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Home");
  await expect(
    page.getByRole("tab", { name: "Files", exact: true }),
  ).toBeFocused();
});

test("download panel is honest about release availability, traps focus, and restores it", async ({
  page,
}) => {
  await page.goto(sitePath("/"));
  await ready(page);
  const opener = page
    .locator(".hero")
    .getByRole("button", { name: "Get AirBridge" });
  await opener.click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.getByText("Public build coming soon")).toHaveCount(2);
  await expect(dialog.locator('a[href$=".apk"],a[href$=".dmg"]')).toHaveCount(
    0,
  );
  for (const link of await dialog.locator(".dialog-links a").all()) {
    expect(
      (await link.getAttribute("href"))?.startsWith(sitePath("/")),
    ).toBeTruthy();
  }
  await dialog.getByRole("button", { name: "Close download panel" }).focus();
  await page.keyboard.press("Shift+Tab");
  expect(
    await page.evaluate(() =>
      Boolean(document.activeElement?.closest("dialog")),
    ),
  ).toBeTruthy();
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(opener).toBeFocused();
  await expect(page.locator("body")).not.toHaveCSS("overflow", "hidden");
  await opener.click();
  await dialog.getByRole("button", { name: "Close download panel" }).click();
  await expect(opener).toBeFocused();
});

test("theme persists across pages and FAQs expand with the keyboard", async ({
  page,
}) => {
  await page.emulateMedia({ colorScheme: "light" });
  await page.goto(sitePath("/"));
  await ready(page);
  await page.getByRole("button", { name: "Switch to dark mode" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByText("Can I keep using Gboard?", { exact: true }).focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("details[open]")).toContainText(
    "The AirBridge keyboard is optional",
  );
  await page.goto(sitePath("/guide/"));
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "A good connection",
  );
  await page.goto(sitePath("/privacy/"));
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "Privacy",
  );
  await page.getByRole("button", { name: "Switch to light mode" }).click();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("mobile navigation closes on selection and Escape", async ({
  page,
}, testInfo) => {
  test.skip(testInfo.project.name !== "mobile", "Mobile-specific navigation");
  await page.goto(sitePath("/"));
  await ready(page);
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(
    page.getByRole("navigation", { name: "Mobile navigation" }),
  ).toBeVisible();
  await page
    .getByRole("navigation", { name: "Mobile navigation" })
    .getByText("Getting started")
    .click();
  await expect(
    page.getByRole("navigation", { name: "Mobile navigation" }),
  ).not.toBeVisible();
  await expect(page).toHaveURL(/#setup$/);
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Open navigation" }),
  ).toBeFocused();
});

test("local pages, fragment links, and accessibility checks pass in both themes", async ({
  page,
}) => {
  for (const theme of ["light", "dark"] as const) {
    await page.emulateMedia({ colorScheme: theme, reducedMotion: "reduce" });
    for (const path of ["/", "/guide/", "/privacy/"]) {
      await page.goto(sitePath(path));
      await ready(page);
      const result = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze();
      expect(
        result.violations.map((v) => ({
          id: v.id,
          nodes: v.nodes.map((n) => n.target),
        })),
      ).toEqual([]);
      const links = await page
        .locator("a[href]")
        .evaluateAll((anchors) => anchors.map((a) => a.getAttribute("href")!));
      for (const href of [...new Set(links)]) {
        const url = new URL(href, page.url());
        if (url.origin !== new URL(page.url()).origin) continue;
        expect(url.pathname.startsWith(sitePath("/")), href).toBeTruthy();
        expect(
          (await page.request.get(url.pathname)).status(),
          url.pathname,
        ).toBe(200);
        if (url.pathname === new URL(page.url()).pathname && url.hash)
          expect(await page.locator(url.hash).count(), href).toBe(1);
      }
    }
  }
});
