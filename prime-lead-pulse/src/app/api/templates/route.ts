import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

function getAuthClient(request: Request) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader) return null;

  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      global: {
        headers: {
          Authorization: authHeader,
        },
      },
    }
  );
}

export async function GET(request: Request) {
  const supabase = getAuthClient(request);
  if (!supabase) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  try {
    const { data, error } = await supabase
      .from('templates')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;
    return NextResponse.json({ success: true, templates: data });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  const supabase = getAuthClient(request);
  if (!supabase) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return NextResponse.json({ error: 'Invalid token' }, { status: 401 });

    const { name, subject, body } = await request.json();

    const { data, error } = await supabase
      .from('templates')
      .insert({ user_id: user.id, name, subject, body })
      .select()
      .single();

    if (error) throw error;
    return NextResponse.json({ success: true, template: data });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  const supabase = getAuthClient(request);
  if (!supabase) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) return NextResponse.json({ error: 'ID required' }, { status: 400 });

    const { error } = await supabase.from('templates').delete().eq('id', id);
    if (error) throw error;

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
