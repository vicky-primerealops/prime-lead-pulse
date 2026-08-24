import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

// 1x1 transparent PNG buffer
const PIXEL_BUFFER = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
  'base64'
);

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id: emailId } = await params;
  const userAgent = request.headers.get('user-agent') || 'Unknown';
  const ipAddress = request.headers.get('x-forwarded-for') || 'Unknown';

  try {
    // 1. Fetch the email to check its creation time
    const { data: emailData } = await supabase
      .from('emails')
      .select('created_at')
      .eq('id', emailId)
      .single();

    // 2. BOT FILTER: Ignore opens that happen within 120 seconds of sending
    if (emailData) {
      const emailAgeMs = Date.now() - new Date(emailData.created_at).getTime();
      if (emailAgeMs < 120000) {
        // Return the pixel but DO NOT log the event
        return new NextResponse(PIXEL_BUFFER, {
          status: 200,
          headers: {
            'Content-Type': 'image/png',
            'Content-Length': PIXEL_BUFFER.length.toString(),
            'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
          },
        });
      }
    }

    // 3. Debounce: prevent duplicate opens within 5 seconds
    const fiveSecondsAgo = new Date(Date.now() - 5000).toISOString();
    const { data: recentOpens } = await supabase
      .from('tracking_events')
      .select('id')
      .eq('email_id', emailId)
      .eq('event_type', 'open')
      .gte('created_at', fiveSecondsAgo)
      .limit(1);

    if (!recentOpens || recentOpens.length === 0) {
      await supabase.from('tracking_events').insert({
        email_id: emailId,
        event_type: 'open',
        ip_address: ipAddress,
        user_agent: userAgent,
      });
    }
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
