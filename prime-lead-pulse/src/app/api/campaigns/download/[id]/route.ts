import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  
  const url = new URL(request.url);
  const token = url.searchParams.get('token');

  if (!token) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  const { data: { user }, error: authError } = await supabase.auth.getUser(token);
  if (authError || !user) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  const { data: campaign, error } = await campaignQuery(id, user.id);
  
  if (error || !campaign) {
    return new NextResponse('Campaign not found', { status: 404 });
  }

  const baseUrl = url.origin;
  
  // Create Google Apps Script code
  const appsScriptCode = `
/**
 * Prime Lead Pulse - Google Apps Script Sender
 * Campaign: ${campaign.name}
 * 
 * INSTRUCTIONS:
 * 1. Open your Google Sheet containing your contacts.
 * 2. Make sure it has 'name' and 'email' columns.
 * 3. Click Extensions > Apps Script in the menu.
 * 4. Paste ALL of this code into the editor (replace any existing code).
 * 5. Click the "Run" button at the top.
 * 6. Google will ask you to authorize the script. Click "Review Permissions" -> Choose your account -> Click "Advanced" -> "Go to script (unsafe)" -> "Allow".
 * 7. You can now close the tab. The script will run in the background!
 */

var CAMPAIGN_ID = "${campaign.id}";
var PLATFORM_API_URL = "${baseUrl}";
var BATCH_SIZE = ${campaign.batch_size};
var DELAY_SECONDS = ${campaign.delay_seconds};
var EMAIL_SUBJECT = ${JSON.stringify(campaign.subject)};
var EMAIL_BODY = ${JSON.stringify(campaign.body)};

function startCampaign() {
  // Check if a trigger already exists to prevent duplicates
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() == "processBatch") {
      Logger.log("Campaign is already running in the background.");
      return;
    }
  }
  
  Logger.log("Starting Campaign...");
  
  // Set up the sheet if needed (add a 'Status' column)
  var sheet = SpreadsheetApp.getActiveSheet();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var statusColIndex = headers.indexOf("Status");
  if (statusColIndex === -1) {
    sheet.getRange(1, sheet.getLastColumn() + 1).setValue("Status");
  }
  
  // Start the first batch immediately
  processBatch();
}

function processBatch() {
  var startTime = new Date().getTime();
  var sheet = SpreadsheetApp.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  
  var nameCol = headers.findIndex(function(h) { return h.toString().toLowerCase() === 'name'; });
  var emailCol = headers.findIndex(function(h) { return h.toString().toLowerCase() === 'email'; });
  var statusCol = headers.findIndex(function(h) { return h.toString().toLowerCase() === 'status'; });
  
  if (nameCol === -1 || emailCol === -1) {
    Logger.log("Error: Could not find 'name' or 'email' columns.");
    return;
  }
  
  var emailsSentThisRun = 0;
  
  for (var i = 1; i < data.length; i++) {
    // Check if we are approaching the 6-minute Google Apps Script timeout (stop at 4.5 minutes)
    if (new Date().getTime() - startTime > 270000) {
      Logger.log("Approaching time limit. Pausing and scheduling the next batch...");
      scheduleNextBatch();
      return;
    }
    
    // Stop if we hit the batch limit
    if (emailsSentThisRun >= BATCH_SIZE) {
      Logger.log("Batch size limit reached. Campaign complete or scheduling next batch...");
      // Depending on if you want it to send EVERYTHING in chunks, or just stop at batch limit
      // Assuming batch limit is the TOTAL they want to send right now.
      clearTriggers();
      return;
    }
    
    var row = data[i];
    var status = statusCol !== -1 ? row[statusCol] : "";
    
    if (status !== "Sent") {
      var name = row[nameCol];
      var email = row[emailCol];
      
      if (name && email) {
        var success = sendEmail(name, email);
        if (success) {
          if (statusCol !== -1) {
            sheet.getRange(i + 1, statusCol + 1).setValue("Sent");
          }
          emailsSentThisRun++;
          
          if (emailsSentThisRun < BATCH_SIZE) {
            Utilities.sleep(DELAY_SECONDS * 1000);
          }
        }
      }
    }
  }
  
  Logger.log("Finished sending to all contacts in the sheet.");
  clearTriggers();
}

function sendEmail(toName, toEmail) {
  try {
    var firstName = toName.split(' ')[0] || "";
    var subject = EMAIL_SUBJECT.replace(/{name}/g, firstName).replace(/{first_name}/g, firstName);
    var bodyHtml = EMAIL_BODY.replace(/{name}/g, firstName).replace(/{first_name}/g, firstName);
    bodyHtml = bodyHtml.replace(/\\n/g, "<br>");
    
    var senderEmail = Session.getActiveUser().getEmail();
    var pixelHtml = registerAndGetPixel(senderEmail, toEmail, subject);
    
    bodyHtml = bodyHtml + "<br><br>" + pixelHtml;
    
    MailApp.sendEmail({
      to: toEmail,
      subject: subject,
      htmlBody: bodyHtml
    });
    
    Logger.log("Sent to " + toEmail);
    return true;
  } catch (e) {
    Logger.log("Failed to send to " + toEmail + ": " + e.toString());
    return false;
  }
}

function registerAndGetPixel(senderEmail, toEmail, subject) {
  var emailId = Utilities.getUuid();
  var payload = {
    "campaign_id": CAMPAIGN_ID,
    "sender_email": senderEmail,
    "recipient": toEmail,
    "subject": subject,
    "email_id": emailId
  };
  
  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(PLATFORM_API_URL + "/api/campaigns/register", options);
    if (response.getResponseCode() == 200) {
      var currentTime = new Date().getTime();
      var pixelUrl = PLATFORM_API_URL + "/api/track/pixel/" + emailId + "?t=" + currentTime;
      return '<img src="' + pixelUrl + '" width="1" height="1" alt="" style="display:none" />';
    }
  } catch (e) {
    Logger.log("Failed to register pixel for " + toEmail);
  }
  return "";
}

function scheduleNextBatch() {
  clearTriggers();
  ScriptApp.newTrigger("processBatch")
    .timeBased()
    .after(60000) // 1 minute from now
    .create();
}

function clearTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() == "processBatch") {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}
`;

  return new NextResponse(appsScriptCode, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain',
      'Content-Disposition': `attachment; filename="plp_campaign_${campaign.id.split('-')[0]}.txt"`,
    },
  });
}

async function campaignQuery(id: string, userId: string) {
    return supabase.from('campaigns').select('*').eq('id', id).eq('user_id', userId).single();
}
