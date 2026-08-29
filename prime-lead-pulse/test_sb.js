const { createClient } = require('@supabase/supabase-js');
const sb = createClient('https://ciihhdpjeklpqgpmrocm.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpaWhoZHBqZWtscHFncG1yb2NtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc0ODg2MzgsImV4cCI6MjEwMzA2NDYzOH0.LhIQ1J5DFp_gGwhr972Avlyo0niZqjEmA22urVSQqW4', { global: { headers: { Authorization: 'Bearer fake-token-123' } } });
sb.auth.getUser().then(res => console.log('getUser() without token:', res));
sb.auth.getUser('fake-token-123').then(res => console.log('getUser(token):', res));
