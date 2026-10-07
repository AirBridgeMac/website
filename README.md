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

Tests start the built site on port 4176 and stop it afterward. They cover responsive layouts, word spacing across line-break breakpoints, light/dark theme persistence, feature-tab keyboard navigation, mobile navigation, the download dialog, FAQ expansion, local links, assets, and axe accessibility checks. Browser screenshots, traces, reports, dependencies, and build output are ignored by Git.

## Pages and Behavior

- `/`: product overview, feature tabs, pairing steps, FAQs, and download availability.
- `/guide/`: actual setup steps and limitations for pairing, files, clipboard, notifications, and mirroring.
- `/privacy/`: a plain-language account of the current preview's data handling. Review before any public launch or feature changes.
- Theme follows the system until a user chooses light/dark; only that preference is stored locally.
- Self-hosted fonts and assets. No analytics, forms, trackers, external API calls, or runtime framework.
- Native modal dialog, keyboard-accessible tabs, visible focus states, semantic page structure, and reduced-motion support.

## Downloads

The download panel includes separate Apple Silicon and Intel ZIPs for the public Mac preview, plus release notes and checksums. The version and public URLs live in `src/releases.ts`. These links are included in normal local and GitHub Pages builds without secrets or browser API requests. Android remains marked unavailable until a public APK is configured.

For the next Mac preview, verify the new release assets, update `macVersion` in `src/releases.ts`, and rebuild/deploy. Downloads are intentionally pinned to a reviewed version, not automatically changed by a release event. Do not use GitHub's Latest shortcut for pre-releases or a repository hosting both platforms.

Set `VITE_ANDROID_DOWNLOAD_URL` to a verified public HTTPS APK URL in an ignored local `.env`, the build environment, or the website repository's **Settings > Secrets and variables > Actions > Variables**. The Pages workflow passes this public variable into the build. The existing `VITE_MAC_DOWNLOAD_URL` override is also supported; when set, it replaces the architecture-specific controls with one generic Mac download and hides the default version/notes/checksums to avoid mismatched metadata.

These URLs are public build-time configuration, not secrets. The site rejects non-HTTPS URLs and URLs containing credentials. Review availability and preview/notarization copy when publishing a new platform or changing distribution: the current Mac preview is not notarized and omits Finder's Share extension. No app binaries or signing credentials belong in this repository.

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

To publish, select **GitHub Actions** under **Settings > Pages > Build and deployment > Source** in the website repository, then push `main`. The workflow publishes `dist/` automatically.

To check the project-path version locally, run `SITE_BASE_PATH=/airbridge-site npm run build` followed by `SITE_BASE_PATH=/airbridge-site npm test`. Build again without `SITE_BASE_PATH` for the normal root-path preview.

Before a public launch: finalize the distribution/signing workflow, review privacy wording for the chosen hosting provider, set the public canonical URL and social image URL once a domain is selected, and verify every download. App screenshots reflect a development preview and should be refreshed for the release.

## Third-Party Assets

Lucide icons: ISC license. DM Sans and Instrument Serif: SIL Open Font License, bundled locally through Fontsource. See `THIRD_PARTY_NOTICES.md`. The layout takes inspiration from Reel Motion's spacious product presentation; its code, imagery, and copy are not reused.
