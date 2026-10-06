# AirBridge Site

Independent product website for AirBridge, built with Vite, TypeScript, semantic HTML, and CSS. The Mac and Android repositories are not build dependencies.

## Local Development

Use Node.js 22.12+ or a newer supported Node release.

```sh
npm ci
npm run dev
```

Use the local URL printed by Vite. For a specific free port: `npm run dev -- --port 4175 --strictPort`.

```sh
npm run build
npx playwright install chromium # First-time browser setup only.
npm test
```

Tests start the built site on port 4176 and stop it afterward. They cover seven viewport sizes, light/dark theme persistence, feature-tab keyboard navigation, mobile navigation, the download dialog, FAQ expansion, local links, assets, and axe accessibility checks. Browser screenshots, traces, reports, dependencies, and build output are ignored by Git.

## Pages and Behavior

- `/`: product overview, feature tabs, pairing steps, FAQs, and download availability.
- `/guide/`: actual setup steps and limitations for pairing, files, clipboard, notifications, and mirroring.
- `/privacy/`: a plain-language account of the current preview's data handling. Review before any public launch or feature changes.
- Theme follows the system until a user chooses light/dark; only that preference is stored locally.
- Self-hosted fonts and assets. No analytics, forms, trackers, external API calls, or runtime framework.
- Native modal dialog, keyboard-accessible tabs, visible focus states, semantic page structure, and reduced-motion support.

## Downloads

No public release links are configured. The site explicitly labels the apps as private preview and does not pretend they are on an app store. Download controls show availability, not dead links or test APKs.

When verified releases exist, set `VITE_MAC_DOWNLOAD_URL` and `VITE_ANDROID_DOWNLOAD_URL` to HTTPS artifact URLs in an ignored local `.env` or the build environment. These URLs are public build-time configuration, not secrets. The site rejects non-HTTPS URLs and URLs containing credentials. Review the preview/notarization copy at the same time; it deliberately does not change automatically when a URL is supplied. Do not commit or serve local developer-signed builds as public releases.

## Artwork

`public/images` contains optimized, synthetic product imagery and the supplied AirBridge logo. WebP assets are intentional website source assets, not application binaries or test outputs. Mac captures come from the local core dashboard test fixture; Android comes from the isolated preview app's synthetic UI tests. No personal notifications, pairing codes, or real clipboard content are used. The clipboard and notification feature panels are labeled illustrations, not claimed screenshots.

The optional synthetic feature walkthrough is kept out of the published site. To render it locally, install Pillow and ffmpeg, then run `python3 scripts/render-demo.py`; the video and poster are written under ignored `artifacts/demo-media/`. Use `--preview` for scene stills under `artifacts/demo-stills/`.

To refresh imagery, use the app test fixtures and run the optional asset tool with Pillow installed:

```sh
python3 scripts/prepare-assets.py --captures /path/to/synthetic/mac/captures --logo /path/to/logo-source.png --phone /path/to/synthetic/android.png
```

It preserves screen proportions and creates light/dark hero compositions. Existing checked-in artwork is sufficient for normal builds.

## Deployment

`npm run build` produces the static site in `dist/`. No server or SPA fallback is required. The GitHub Pages workflow in `.github/workflows/deploy.yml` builds and deploys the site when `main` is pushed. It uses the base path reported by GitHub Pages, so a project URL such as `https://OWNER.github.io/airbridge-site/` and a root custom domain both work.

To publish, create a GitHub repository for this site, select **GitHub Actions** under **Settings > Pages > Build and deployment > Source**, then push `main`. The workflow publishes `dist/` automatically. This local repository has no remote or public deployment configured yet.

To check the project-path version locally, run `SITE_BASE_PATH=/airbridge-site npm run build` followed by `SITE_BASE_PATH=/airbridge-site npm test`. Build again without `SITE_BASE_PATH` for the normal root-path preview.

Before a public launch: finalize the distribution/signing workflow, review privacy wording for the chosen hosting provider, set the public canonical URL and social image URL once a domain is selected, and verify every download. App screenshots reflect a development preview and should be refreshed for the release.

## Third-Party Assets

Lucide icons: ISC license. DM Sans and Instrument Serif: SIL Open Font License, bundled locally through Fontsource. See `THIRD_PARTY_NOTICES.md`. The layout takes inspiration from Reel Motion's spacious product presentation; its code, imagery, and copy are not reused.
