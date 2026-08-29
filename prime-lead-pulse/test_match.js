const emailCache = [
  { subject: "The New Dashboard and Call Forwarding", recipient: "DLewis@diyflatfee.com" }
];
const subject = "The New Dashboard and Call Forwarding - Hi Darrell, I wanted to provide a few up...";
const recipientEmail = "To: Darrell";

function findEmail(subject, recipientEmail) {
  if (!subject) return null;
  const norm = s => s.toLowerCase().replace(/\s+/g, ' ').trim();
  const normSubj = norm(subject);
  const cleanRecipientUI = recipientEmail ? recipientEmail.replace(/^To:\s*/i, '').trim().toLowerCase() : '';
  let match = emailCache.find(e => {
    const isSubjMatch = norm(e.subject) === normSubj || normSubj.startsWith(norm(e.subject));
    const isRecipMatch = cleanRecipientUI ? e.recipient.toLowerCase().includes(cleanRecipientUI) || cleanRecipientUI.includes(e.recipient.toLowerCase()) : true;
    if (isSubjMatch && !isRecipMatch && e.subject.length > 15) return true;
    return isSubjMatch && isRecipMatch;
  });
  return match || null;
}
console.log('Match?', findEmail(subject, recipientEmail));
