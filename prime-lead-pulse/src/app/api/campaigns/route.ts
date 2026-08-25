import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

// GET all campaigns for the logged-in user
export async function GET(request: Request) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader) return new NextResponse('Unauthorized', { status: 401 });

  const token = authHeader.replace('Bearer ', '');
  const { data: { user }, error: authError } = await supabase.auth.getUser(token);
  
  if (authError || !user) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  const { data: campaigns, error } = await supabase
    .from('campaigns')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false });

  if (error) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }

  return NextResponse.json({ success: true, campaigns });
}

// POST a new campaign
export async function POST(request: Request) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader) return new NextResponse('Unauthorized', { status: 401 });

  const token = authHeader.replace('Bearer ', '');
  const { data: { user }, error: authError } = await supabase.auth.getUser(token);
  
  if (authError || !user) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  try {
    const payload = await request.json();
    
    const { data: campaign, error } = await supabase
      .from('campaigns')
      .insert({
        user_id: user.id,
        name: payload.name,
        subject: payload.subject,
        body: payload.body,
        sheet_url: payload.sheet_url,
        batch_size: payload.batch_size || 50,
        delay_seconds: payload.delay_seconds || 40,
        status: 'Ready'
      })
      .select()
      .single();

    if (error) throw error;
    
    return NextResponse.json({ success: true, campaign });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
