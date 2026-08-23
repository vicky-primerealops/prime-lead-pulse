import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

// 1x1 transparent PNG buffer
const PIXEL_BUFFER = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
  'base64'
);

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const emailId = params.id;
  const userAgent = request.headers.get('user-agent') || 'Unknown';
  const ipAddress = request.headers.get('x-forwarded-for') || 'Unknown';

  try {
    // Log the open event in Supabase
    await supabase.from('tracking_events').insert({
      email_id: emailId,
      event_type: 'open',
      ip_address: ipAddress,
      user_agent: userAgent,
    });
  } catch (error) {
    console.error('Error logging pixel open:', error);
    // Even if it fails, we still want to return the pixel so the email doesn't break
  }

  // Return the invisible pixel
  return new NextResponse(PIXEL_BUFFER, {
    status: 200,
    headers: {
      'Content-Type': 'image/png',
      'Content-Length': PIXEL_BUFFER.length.toString(),
      // Extremely important: prevent Gmail from caching the pixel, or opens will only be logged once!
      'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
  });
}
