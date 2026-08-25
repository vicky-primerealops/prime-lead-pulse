import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

// This is called by the Python script to register an email before sending
export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const { campaign_id, recipient, subject, sender_email, email_id } = payload;

    if (!campaign_id || !recipient || !email_id) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Fetch the campaign to verify it exists and get the user_id
    const { data: campaign, error: campaignError } = await supabase
      .from('campaigns')
      .select('user_id')
      .eq('id', campaign_id)
      .single();

    if (campaignError || !campaign) {
      return NextResponse.json({ error: 'Invalid campaign ID' }, { status: 404 });
    }

    // Insert the email, bypassing RLS since we use the service role
    // Wait, the regular supabase client uses the ANON key, which enforces RLS.
    // If we insert using the anon key, it will fail because auth.uid() is null (no token).
    // We need to bypass RLS here, so we must use the service role key!
    
    // Instead of using the service role key, we can temporarily disable RLS, OR use the service role key.
    // Since we are in an API route, we can initialize a supabase client with the service role key if it exists in env.
    // Let's check if NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY exists, or just do it via normal API if we have to.
    
    // Wait! A better way: The campaigns table is public to those who know the UUID? No.
    // Let's create a Supabase client with the Service Role Key.
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
    
    const adminSupabase = require('@supabase/supabase-js').createClient(supabaseUrl, supabaseServiceKey);

    const { data, error } = await adminSupabase
      .from('emails')
      .insert({
        id: email_id,
        user_id: campaign.user_id,
        campaign_id: campaign_id,
        sender_email: sender_email || 'campaign',
        recipient: recipient,
        subject: subject
      })
      .select()
      .single();

    if (error) throw error;

    return NextResponse.json({ success: true, email: data });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
