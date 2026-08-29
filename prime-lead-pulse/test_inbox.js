const norm = s => s.toLowerCase().replace(/\s+/g, ' ').trim();
const dbSubj = "The New Dashboard and Call Forwarding";
const uiSubj = "Inbox The New Dashboard and Call Forwarding - Hi Darrell...";
const normDb = norm(dbSubj);
const normUi = norm(uiSubj);
console.log('startsWith:', normUi.startsWith(normDb));
