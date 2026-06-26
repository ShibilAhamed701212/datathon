// .env Protection Plugin
// Prevents reading of .env files containing secrets
// Install: Add to opencode.json hooks, or reference as a plugin

const SENSITIVE_PATTERNS = [
  /\.env$/,
  /\.env\.local$/,
  /\.env\.production$/,
  /credentials\.json$/,
  /secrets\./,
  /service-account\.json$/,
  /\.pem$/,
  /id_rsa/,
];

module.exports = {
  name: "env-protection",
  description: "Blocks access to files containing secrets",
  
  onFileRead: (filePath) => {
    for (const pattern of SENSITIVE_PATTERNS) {
      if (pattern.test(filePath)) {
        return {
          blocked: true,
          message: `Blocked: ${filePath} contains sensitive credentials. Use environment variables instead.`,
        };
      }
    }
    return { blocked: false };
  },
};
