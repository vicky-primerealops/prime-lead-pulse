import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const emailId = params.id;
  const { searchParams } = new URL(request.url);
  const targetUrl = searchParams.get('url');

  const userAgent = request.headers.get('user-agent') || 'Unknown';
  const ipAddress = request.headers.get('x-forwarded-for') || 'Unknown';

  if (!targetUrl) {
    return new NextResponse('Missing target URL', { status: 400 });
  }

  try {
    // Log the click event in Supabase
    await supabase.from('tracking_events').insert({
      email_id: emailId,
      event_type: 'click',
      url: targetUrl,
      ip_address: ipAddress,
      user_agent: userAgent,
    });
  } catch (error) {
    console.error('Error logging link click:', error);
  }

  // Redirect the user to their actual destination
  return NextResponse.redirect(targetUrl);
}
