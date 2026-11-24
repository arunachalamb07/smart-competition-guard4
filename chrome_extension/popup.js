const $=id=>document.getElementById(id);
chrome.storage.local.get(["server","teamCode","laptopName","enabled"],s=>{
  $("server").value=s.server||"http://127.0.0.1:5000";
  $("code").value=s.teamCode||"";
  $("laptop").value=s.laptopName||"";
  $("msg").textContent=s.enabled?"Monitoring enabled":"Monitoring not configured";
});
$("save").addEventListener("click",async()=>{
  const server=$("server").value.trim().replace(/\/$/,""),teamCode=$("code").value.trim().toUpperCase(),laptopName=$("laptop").value.trim();
  if(!server||!teamCode||!laptopName){$("msg").textContent="Please fill all fields.";return}
  await chrome.storage.local.set({server,teamCode,laptopName,enabled:true});
  try{
    const r=await fetch(server+"/api/heartbeat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({team_code:teamCode,laptop_name:laptopName})});
    const d=await r.json(); $("msg").textContent=r.ok?"Connected successfully. Monitoring is ON.":(d.error||"Could not connect.");
    $("msg").className=r.ok?"note ok":"note";
  }catch(e){$("msg").textContent="Server unreachable. Check URL and same Wi-Fi."; $("msg").className="note"}
});
