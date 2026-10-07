// Public release metadata only. Keep binaries and credentials out of the website.
const macVersion = "0.1.0-preview.1";
const macTag = `mac-v${macVersion}`;
const repository = "https://github.com/AirBridgeMac/website/releases";

export const macRelease = {
  version: macVersion,
  notes: `${repository}/tag/${macTag}`,
  checksums: `${repository}/download/${macTag}/SHA256SUMS.txt`,
  downloads: [
    {
      label: "Apple Silicon",
      url: `${repository}/download/${macTag}/AirBridge-${macVersion}-macos-arm64.zip`,
    },
    {
      label: "Intel Mac",
      url: `${repository}/download/${macTag}/AirBridge-${macVersion}-macos-x86_64.zip`,
    },
  ],
};
