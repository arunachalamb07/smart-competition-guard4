const RESTRICTED = [
  "chatgpt.com","chat.openai.com","claude.ai","gemini.google.com",
  "copilot.microsoft.com","perplexity.ai","poe.com"
];
async function settings(){return await chrome.storage.local.get(["server","teamCode","laptopName","enabled"])}
function domainOf(url){try{return new URL(url).hostname.toLowerCase()}catch{return ""}}
async function sendEvent(type, detail, severity="info"){
  const s=await settings(); if(!s.enabled || !s.server || !s.teamCode || !s.laptopName)return;
  try{await fetch(s.server.replace(/\/$/,"")+"/api/events",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({team_code:s.teamCode,laptop_name:s.laptopName,event_type:type,detail,severity})})}catch(e){console.warn("Smart Guard server unavailable",e)}
}
chrome.tabs.onActivated.addListener(async info=>{
  await sendEvent("TAB_SWITCH",`Browser tab switched (tab id ${info.tabId})`,"info");
});
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab)=>{
  if(changeInfo.status!=="complete" || !tab.url)return;
  const host=domainOf(tab.url);
  if(!host)return;
  await sendEvent("WEBSITE_VISIT",`Visited domain: ${host}`,"info");
  if(RESTRICTED.some(d=>host===d || host.endsWith("."+d))){
    await sendEvent("RESTRICTED_AI_SITE",`Restricted AI website opened: ${host}`,"alert");
  }
});
chrome.runtime.onInstalled.addListener(async()=>{
  const s=await settings();
  if(s.enabled===undefined) await chrome.storage.local.set({enabled:true});
});
