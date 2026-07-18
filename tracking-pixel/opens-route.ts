// =============================================================
// File: app/api/track/opens/route.ts
// Dashboard API — returns all tracked opens as JSON
// Call: GET https://primerealops.com/api/track/opens
// Optional: ?first_only=true (shows only first opens)
// =============================================================

import { NextRequest, NextResponse } from "next/server";
import { Pool } from "@neondatabase/serverless";

export const runtime = "edge";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const firstOnly = searchParams.get("first_only") === "true";

    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });

    let query: string;

    if (firstOnly) {
      // Only show first opens (one row per recipient)
      query = `
        SELECT recipient, opened_at, user_agent, ip_address
        FROM email_opens
        WHERE is_first_open = TRUE
        ORDER BY opened_at DESC
        LIMIT 200
      `;
    } else {
      // Show all opens
      query = `
        SELECT recipient, opened_at, user_agent, ip_address, is_first_open
        FROM email_opens
        ORDER BY opened_at DESC
        LIMIT 200
      `;
    }

    const { rows } = await pool.query(query);
    await pool.end();

    // Summary stats
    const statsQuery = await new Pool({
      connectionString: process.env.DATABASE_URL,
    });
    const { rows: stats } = await statsQuery.query(`
      SELECT
        COUNT(DISTINCT recipient) as unique_openers,
        COUNT(*) as total_opens,
        MIN(opened_at) as first_open_ever,
        MAX(opened_at) as latest_open
      FROM email_opens
    `);
    await statsQuery.end();

    return NextResponse.json({
      summary: stats[0],
      opens: rows,
    });
  } catch (error) {
    console.error("Opens query error:", error);
    return NextResponse.json(
      { error: "Failed to fetch opens" },
      { status: 500 }
    );
  }
}
