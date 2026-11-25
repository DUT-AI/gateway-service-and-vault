export interface ParsedEnvEntry {
  key: string;
  value: string;
}

/**
 * Parse raw .env file content into normalized key-value pairs on the frontend.
 * Handles comments (#), blank lines, `export KEY=VAL`, single/double quotes,
 * and inline comments on unquoted values.
 */
export function parseEnvContent(raw: string): ParsedEnvEntry[] {
  const resultMap = new Map<string, string>();
  const lines = raw.split(/\r?\n/);

  for (const rawLine of lines) {
    const trimmed = rawLine.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    const lineWithoutExport = trimmed.startsWith("export ")
      ? trimmed.slice(7).trim()
      : trimmed;

    const eqIndex = lineWithoutExport.indexOf("=");
    if (eqIndex <= 0) {
      continue;
    }

    const rawKey = lineWithoutExport.slice(0, eqIndex).trim().toUpperCase();
    // Skip invalid keys
    if (!/^[A-Z0-9_]+$/.test(rawKey)) {
      continue;
    }

    let rawValue = lineWithoutExport.slice(eqIndex + 1).trim();

    if (
      (rawValue.startsWith('"') && rawValue.endsWith('"') && rawValue.length >= 2) ||
      (rawValue.startsWith("'") && rawValue.endsWith("'") && rawValue.length >= 2)
    ) {
      const quote = rawValue[0];
      rawValue = rawValue.slice(1, -1);
      if (quote === '"') {
        rawValue = rawValue
          .replace(/\\n/g, "\n")
          .replace(/\\r/g, "\r")
          .replace(/\\t/g, "\t")
          .replace(/\\"/g, '"');
      }
    } else {
      // Strip inline comment for unquoted values (e.g. PORT=8000 # comment)
      const hashIndex = rawValue.indexOf(" #");
      if (hashIndex !== -1) {
        rawValue = rawValue.slice(0, hashIndex).trim();
      }
    }

    if (rawValue.length > 0) {
      resultMap.set(rawKey, rawValue);
    }
  }

  return Array.from(resultMap.entries()).map(([key, value]) => ({
    key,
    value,
  }));
}
