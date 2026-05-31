import { getStore } from '@netlify/blobs';
import { randomUUID } from 'crypto';

export const handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method Not Allowed' };

  let body;
  try {
    body = JSON.parse(event.body || '{}');
  } catch(e) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const { url, start, end, format, template, fade, platform } = body;

  const host = event.headers.host || 'clipped-showcase.netlify.app';

  // Basic validation
  if (!url || (!url.startsWith('http') && url !== 'local' && !url.includes(host))) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid or missing Source URL' }) };
  }

  // Disable cloud video generation
  if (format === 'video') {
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Video rendering is currently available through the Clipped CLI. Cloud video rendering is under development.' })
    };
  }

  const jobId = randomUUID();
  const store = getStore('clip-jobs');

  await store.set(`${jobId}:params`, JSON.stringify({ url, start, end, format, template, fade, platform }), { ttl: 3600 });
  await store.set(`${jobId}:status`, 'pending', { ttl: 3600 });

  // Fire background function (fire-and-forget)
  const protocol = host.includes('localhost') ? 'http' : 'https';
  const bgUrl = `${protocol}://${host}/.netlify/functions/clip-job-background`;

  fetch(bgUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jobId }),
  }).catch((err) => {
    console.error("Failed to trigger background function:", err);
  });

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jobId }),
  };
};
