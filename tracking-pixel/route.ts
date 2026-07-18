// =============================================================
// File: app/api/track/route.ts
// Deploy this in your Next.js project on Vercel
// =============================================================

import { NextRequest, NextResponse } from "next/server";
import { Pool } from "@neondatabase/serverless";

// 1x1 transparent GIF (smallest valid image — 43 bytes)
const TRANSPARENT_GIF = Buffer.from(
  "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
  "base64"
);

export const runtime = "edge"; // Runs on Vercel Edge for fastest response

export async function GET(request: NextRequest) {
  try {
    // --- 1. Extract tracking info from the URL ---
    const { searchParams } = new URL(request.url);
    const encodedEmail = searchParams.get("id");

    if (!encodedEmail) {
      return new NextResponse(TRANSPARENT_GIF, {
        headers: pixelHeaders(),
      });
    }

    // Decode the recipient email (base64 encoded for privacy)
    let recipientEmail: string;
    try {
      recipientEmail = atob(encodedEmail);
    } catch {
      return new NextResponse(TRANSPARENT_GIF, {
        headers: pixelHeaders(),
      });
    }

    // --- 2. Get device/browser info ---
    const userAgent = request.headers.get("user-agent") || "Unknown";
    const ip =
      request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
      request.headers.get("x-real-ip") ||
      "Unknown";

    // --- 3. Log the open to NeonDB ---
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });

    // Check if this is the first open for this recipient
    const { rows: existing } = await pool.query(
      "SELECT id FROM email_opens WHERE recipient = $1 LIMIT 1",
      [recipientEmail]
    );

    const isFirstOpen = existing.length === 0;

    // Insert the open event
    await pool.query(
      `INSERT INTO email_opens (recipient, user_agent, ip_address, is_first_open)
       VALUES ($1, $2, $3, $4)`,
      [recipientEmail, userAgent, ip, isFirstOpen]
    );

    // --- 4. Send notification email on FIRST open only ---
    if (isFirstOpen && process.env.NOTIFY_EMAIL) {
      // Fire-and-forget — don't block the pixel response
      sendNotification(recipientEmail).catch(() => {});
    }

    await pool.end();

    // --- 5. Return the invisible pixel ---
    return new NextResponse(TRANSPARENT_GIF, {
      headers: pixelHeaders(),
    });
  } catch (error) {
    // Always return the pixel even if logging fails
    console.error("Tracking error:", error);
    return new NextResponse(TRANSPARENT_GIF, {
      headers: pixelHeaders(),
    });
  }
}

// --- Helper: HTTP headers for the pixel image ---
function pixelHeaders(): HeadersInit {
  return {
    "Content-Type": "image/gif",
    "Content-Length": TRANSPARENT_GIF.byteLength.toString(),
    // Prevent caching so every open is tracked
    "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
    Pragma: "no-cache",
    Expires: "0",
  };
}

// --- Helper: Send notification email via SMTP ---
async function sendNotification(recipientEmail: string) {
  // Uses a simple fetch to a notification endpoint
  // You can replace this with any email service (Resend, SendGrid, etc.)
  // Or use the built-in Vercel email if available

  // For now, we log it. Your dev team can wire up their preferred
  // notification method here.
  console.log(`📬 FIRST OPEN: ${recipientEmail} opened the email!`);

  // Optional: If you set up Resend (free tier: 100 emails/day)
  // Uncomment and configure:
  /*
  if (process.env.RESEND_API_KEY) {
    await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: "tracker@primerealops.com",
        to: process.env.NOTIFY_EMAIL,
        subject: `📬 ${recipientEmail} opened your email!`,
        text: `${recipientEmail} just opened your outreach email for the first time.\n\nTime: ${new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })} IST`,
      }),
    });
  }
  */
}
