export interface SubtitleWord {
  start: number; // in seconds
  end: number;   // in seconds
  text: string;
}

export interface SubtitleLine {
  start: number; // in seconds
  end: number;   // in seconds
  text: string;
  words?: SubtitleWord[];
}

/**
 * Parses an LRC format string into SubtitleLines.
 */
export function parseLrc(content: string): SubtitleLine[] {
  const lines = content.split('\n');
  const result: SubtitleLine[] = [];
  const timeRegex = /\[(\d+):(\d+\.?\d*)\](.*)/;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    
    const match = timeRegex.exec(line);
    if (match) {
      const minutes = parseInt(match[1], 10);
      const seconds = parseFloat(match[2]);
      const text = match[3].trim();
      const timeInSeconds = minutes * 60 + seconds;

      result.push({
        start: timeInSeconds,
        end: timeInSeconds, // LRC doesn't explicitly give end time, we'll patch it later
        text,
      });
    }
  }

  // Patch end times for LRC
  for (let i = 0; i < result.length; i++) {
    if (i < result.length - 1) {
      result[i].end = result[i + 1].start;
    } else {
      result[i].end = result[i].start + 5; // guess 5 seconds for the last line
    }
  }

  return result;
}

/**
 * Parses an SRT format string into SubtitleLines.
 */
export function parseSrt(content: string): SubtitleLine[] {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const result: SubtitleLine[] = [];
  
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    if (!line) {
      i++;
      continue;
    }

    // Usually there's an index number here, skip it
    if (/^\d+$/.test(line)) {
      i++;
      if (i >= lines.length) break;
    }

    const timeLine = lines[i].trim();
    const timeRegex = /(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/;
    const match = timeRegex.exec(timeLine);

    if (match) {
      const start = 
        parseInt(match[1], 10) * 3600 + 
        parseInt(match[2], 10) * 60 + 
        parseInt(match[3], 10) + 
        parseInt(match[4], 10) / 1000;
      
      const end = 
        parseInt(match[5], 10) * 3600 + 
        parseInt(match[6], 10) * 60 + 
        parseInt(match[7], 10) + 
        parseInt(match[8], 10) / 1000;

      i++;
      const textLines: string[] = [];
      while (i < lines.length && lines[i].trim() !== '') {
        textLines.push(lines[i].trim());
        i++;
      }

      result.push({
        start,
        end,
        text: textLines.join('\n'),
      });
    } else {
      i++;
    }
  }

  return result;
}

/**
 * Basic VTT parser
 */
export function parseVtt(content: string): SubtitleLine[] {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const result: SubtitleLine[] = [];
  
  let i = 0;
  // Skip WEBVTT header
  while (i < lines.length && lines[i].trim() !== '') {
    i++;
  }

  while (i < lines.length) {
    let line = lines[i].trim();
    if (!line) {
      i++;
      continue;
    }

    // Skip cue identifier if present
    if (!line.includes('-->')) {
      i++;
      if (i >= lines.length) break;
      line = lines[i].trim();
    }

    const timeRegex = /(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}:)?(\d{2}):(\d{2})\.(\d{3})/;
    const match = timeRegex.exec(line);

    if (match) {
      const parseTime = (h: string | undefined, m: string, s: string, ms: string) => {
        return (h ? parseInt(h.replace(':', ''), 10) * 3600 : 0) +
          parseInt(m, 10) * 60 +
          parseInt(s, 10) +
          parseInt(ms, 10) / 1000;
      };

      const start = parseTime(match[1], match[2], match[3], match[4]);
      const end = parseTime(match[5], match[6], match[7], match[8]);

      i++;
      const textLines: string[] = [];
      while (i < lines.length && lines[i].trim() !== '') {
        textLines.push(lines[i].trim());
        i++;
      }

      // VTT might contain tags like <c.color> or <00:00.000>. Strip them for now.
      const rawText = textLines.join('\n');
      const cleanText = rawText.replace(/<[^>]+>/g, '');

      result.push({
        start,
        end,
        text: cleanText,
      });
    } else {
      i++;
    }
  }

  return result;
}

export function parseLyrics(content: string, filename: string): SubtitleLine[] {
  const lowerName = filename.toLowerCase();
  if (lowerName.endsWith('.lrc')) {
    return parseLrc(content);
  }
  if (lowerName.endsWith('.srt')) {
    return parseSrt(content);
  }
  if (lowerName.endsWith('.vtt')) {
    return parseVtt(content);
  }
  
  // Try to guess JSON
  try {
    const json = JSON.parse(content);
    if (Array.isArray(json)) {
      return json as SubtitleLine[];
    }
  } catch (e) {
    // Not json
  }

  return [];
}
