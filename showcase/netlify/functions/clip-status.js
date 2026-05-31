import { getStore } from '@netlify/blobs';

export const handler = async (event) => {
  const jobId = event.queryStringParameters?.job;
  if (!jobId) return { statusCode: 400, body: 'Missing job ID' };
  
  const store = getStore('clip-jobs');
  const status = await store.get(`${jobId}:status`, { type: 'text' }) || 'unknown';
  
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  };
};
