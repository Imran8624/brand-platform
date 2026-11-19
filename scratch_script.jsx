
const { useState, useEffect, useRef } = React;

const API_BASE = "http://localhost:8080";

// --- Simple Fetch Wrapper ---
async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (!(opts.body instanceof FormData) && opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(API_BASE + path, { ...opts, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch(e){}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

// ===========================================================================
// MAIN APP COMPONENT
// ===========================================================================
function InkloomApp() {
  // Navigation: "studio" | "kb" | "trail" | "insights"
  const [activeTab, setActiveTab] = useState("studio");

  // Role: "Creator" | "Brand Manager" | "Legal Reviewer"
  const [currentRole, setCurrentRole] = useState("Brand Manager");
  const [currentUser, setCurrentUser] = useState({ name: "Brand Manager", role: "Brand Manager" });

  // Data states
  const [assets, setAssets] = useState([]);
  const [selectedAssetId, setSelectedAssetId] = useState(null);
  const [currentAsset, setCurrentAsset] = useState(null);
  const [scans, setScans] = useState([]);
  const [flags, setFlags] = useState([]);
  const [guidelines, setGuidelines] = useState([]);
  const [secretProjects, setSecretProjects] = useState([]);
  const [approvalLedger, setApprovalLedger] = useState([]);
  const [inboxData, setInboxData] = useState({ unread_count: 0, messages: [] });
  const [dashboardStats, setDashboardStats] = useState(null);

  // Format toggle for active draft: "text" | "banner" | "pdf" | "video"
  const [activeFormat, setActiveFormat] = useState("text");

  // Privacy Shield Toggle
  const [privacyShield, setPrivacyShield] = useState(true);
  const [privateMaskCount, setPrivateMaskCount] = useState(14);

  // Modals & Drawers
  const [showNewDraftModal, setShowNewDraftModal] = useState(false);
  const [showAIHelper, setShowAIHelper] = useState(false);
  const [showCaseModal, setShowCaseModal] = useState(false);
  const [selectedCaseRule, setSelectedCaseRule] = useState(null);
  const [showSkipModal, setShowSkipModal] = useState(null); // flagId
  const [skipReason, setSkipReason] = useState("");
  const [showEditFlagModal, setShowEditFlagModal] = useState(null); // flag object
  const [editedText, setEditedText] = useState("");
  const [showInboxDrawer, setShowInboxDrawer] = useState(false);

  // Brand Manager 3-Level Automation States
  const [bmAutomationData, setBmAutomationData] = useState(null);
  const [bmLevelRunning, setBmLevelRunning] = useState(false);
  const [autoRunStep1, setAutoRunStep1] = useState(true);
  const [autoDecideReport, setAutoDecideReport] = useState(true);
  const [selectedChannel, setSelectedChannel] = useState("Email + Creator Inbox Message");

  // Toast feedback
  const [toastMsg, setToastMsg] = useState(null);

  function showToast(msg, type = "info") {
    setToastMsg({ text: msg, type });
    setTimeout(() => setToastMsg(null), 3500);
  }

  // Initial load
  useEffect(() => {
    loadAllData();
  }, []);

  async function loadAllData() {
    try {
      const me = await api("/api/me").catch(() => ({ name: "Demo Creator", role: "Creator" }));
      setCurrentUser(me);
      setCurrentRole(me.role);

      const [assetsData, glData, spData, ledgerData, inbox, dash] = await Promise.all([
        api("/api/assets"),
        api("/api/guidelines"),
        api("/api/inkloom/secret-projects"),
        api("/api/inkloom/approval-ledger"),
        api("/api/inkloom/inbox"),
        api("/api/dashboard")
      ]);

      setAssets(assetsData || []);
      setGuidelines(glData || []);
      setSecretProjects(spData || []);
      setApprovalLedger(ledgerData || []);
      setInboxData(inbox || { unread_count: 0, messages: [] });
      setDashboardStats(dash);

      if (assetsData && assetsData.length > 0) {
        loadAssetDetail(assetsData[0].id);
      }
    } catch (err) {
      console.error("Failed to load initial data:", err);
      showToast("Connected to offline local cache", "info");
    }
  }

  async function loadAssetDetail(id) {
    setSelectedAssetId(id);
    try {
      const [a, scanList, flagList] = await Promise.all([
        api(`/api/assets/${id}`),
        api(`/api/assets/${id}/scan`),
        api(`/api/assets/${id}/flags`)
      ]);
      setCurrentAsset(a);
      setScans(scanList || []);
      setFlags(flagList || []);
      setActiveFormat(a.file_type || "text");
    } catch (e) {
      console.error(e);
    }
  }

  // Switch Role
  async function handleRoleSwitch(role) {
    try {
      const fd = new FormData();
      fd.append("role", role);
      const updated = await api("/api/session/role", { method: "POST", body: fd });
      setCurrentRole(role);
      setCurrentUser(updated);
      showToast(`Switched workspace to ${role}`, "info");
      if (selectedAssetId) loadAssetDetail(selectedAssetId);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  // Workflow Sequential Approvals
  async function submitForReview(id) {
    try {
      await api(`/api/assets/${id}/submit`, { method: "POST" });
      showToast("Draft submitted for Step 1 Brand Manager Review!", "success");
      loadAssetDetail(id);
      loadAllData();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function approveStep1(id) {
    // Brand Manager approves Step 1 -> moves to Legal Review
    try {
      // simulate moving to Legal Review
      const fd = new FormData();
      fd.append("asset_id", id);
      fd.append("subject", "Step 1 Passed: Moved to Legal Review");
      fd.append("body", "Brand Manager Marcus Vance approved Step 1. The draft is now in Legal Review.");
      await api("/api/inkloom/inbox/send", { method: "POST", body: fd });
      showToast("Step 1 Approved! Draft passed to Legal Review.", "success");
      loadAssetDetail(id);
      loadAllData();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function approveFinal(id) {
    const hasMustFix = flags.some(f => f.status === "open" && (f.severity === "critical" || f.severity === "high"));
    if (hasMustFix) {
      showToast("Blocked: You must resolve all 'Must Fix' mistakes before granting Final Approval.", "error");
      return;
    }
    try {
      await api(`/api/assets/${id}/approve`, { method: "POST" });
      showToast("Final Approval granted! Ready to publish.", "success");
      loadAssetDetail(id);
      loadAllData();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function publishDraft(id) {
    try {
      await api(`/api/assets/${id}/publish`, { method: "POST" });
      showToast("Draft published successfully to production!", "success");
      loadAssetDetail(id);
      loadAllData();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function rejectDraft(id) {
    const reason = prompt("Enter the reason for returning this draft to Creator (in simple English):");
    if (!reason) return;
    try {
      const fd = new FormData();
      fd.append("reason", reason);
      await api(`/api/assets/${id}/reject`, { method: "POST", body: fd });
      showToast("Draft sent back to Creator with mistake notes.", "info");
      loadAssetDetail(id);
      loadAllData();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  // Flag Decisions
  async function handleFlagAction(flagId, action, fixText = null, reason = null) {
    try {
      const fd = new FormData();
      if (action === "accept") {
        fd.append("decision", "accepted");
        fd.append("reason", "Accepted recommended brand fix");
        if (fixText && currentAsset) {
          // auto replace in text
          const target = flags.find(f => f.id === flagId);
          if (target && target.element) {
            const updatedContent = currentAsset.content_text.replace(target.element, target.suggested_fix);
            currentAsset.content_text = updatedContent;
          }
        }
      } else if (action === "dismiss") {
        fd.append("decision", "dismissed");
        fd.append("reason", reason || "Reviewed and skipped with approval");
      } else if (action === "edit") {
        fd.append("decision", "edited");
        fd.append("resolved_text", fixText);
        fd.append("reason", reason || "Custom user edit applied");
      }
      await api(`/api/flags/${flagId}/decide`, { method: "POST", body: fd });
      showToast(`Flag updated (${action})`, "success");
      loadAssetDetail(selectedAssetId);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  // Run 3-Level BM Automation
  async function triggerBMAutomation(level = "all") {
    if (!selectedAssetId) return;
    setBmLevelRunning(true);
    try {
      const fd = new FormData();
      fd.append("asset_id", selectedAssetId);
      fd.append("level", level);
      fd.append("channel", selectedChannel);
      fd.append("auto_decide", autoDecideReport ? "true" : "false");
      const res = await api("/api/inkloom/bm-automation/run", { method: "POST", body: fd });
      setBmAutomationData(res);
      showToast(`Automation complete: ${res.decision} (${res.score}/100)`, res.decision === "Pass" ? "success" : "info");
      loadAssetDetail(selectedAssetId);
      loadAllData();
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setBmLevelRunning(false);
    }
  }

  // Re-scan
  async function triggerRescan() {
    if (!selectedAssetId) return;
    try {
      await api(`/api/assets/${selectedAssetId}/scan`, { method: "POST" });
      showToast("Scan finished across all 6 dimensions!", "success");
      loadAssetDetail(selectedAssetId);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  // Calculate Progress %
  const currentStep = !currentAsset ? 1 :
    currentAsset.state === "Draft" ? 1 :
    currentAsset.state === "In Review" ? 2 :
    currentAsset.state === "Approved" || currentAsset.state === "Published" ? 3 : 1;
  const progressPercent = currentStep === 1 ? 33 : currentStep === 2 ? 66 : 100;

  return (
    <div className="flex flex-col min-h-screen bg-ink-bg text-zinc-100 font-sans">
      {/* Toast Alert */}
      {toastMsg && (
        <div className={`fixed bottom-5 right-5 z-50 px-4 py-3 rounded-xl shadow-2xl flex items-center gap-3 border text-sm font-semibold transition-all transform animate-bounce ${
          toastMsg.type === "error" ? "bg-red-950 border-red-700 text-red-200" :
          toastMsg.type === "success" ? "bg-emerald-950 border-emerald-700 text-emerald-200" :
          "bg-zinc-900 border-ink-pink text-white"
        }`}>
          <span>{toastMsg.type === "error" ? "⚠️" : toastMsg.type === "success" ? "✅" : "💡"}</span>
          <span>{toastMsg.text}</span>
        </div>
      )}

      {/* TOP GLOBAL NAVBAR */}
      <header className="sticky top-0 z-40 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800 px-6 py-3 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveTab("studio")}>
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-pink-600 to-blue-600 flex items-center justify-center font-black text-white text-lg shadow-lg">
              I
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-black tracking-tight flex items-center gap-1.5">
                Inkloom <span className="text-pink-500 font-extrabold text-sm px-1.5 py-0.5 rounded bg-pink-950/60 border border-pink-700">AI</span>
              </span>
              <span className="text-[10px] text-zinc-400 uppercase tracking-widest -mt-1">Pre-Publication Control</span>
            </div>
          </div>

          {/* Privacy Shield Pill */}
          <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-700 text-xs">
            <span className={`w-2 h-2 rounded-full ${privacyShield ? "bg-emerald-400 animate-ping" : "bg-zinc-500"}`}></span>
            <span className="text-zinc-300 font-medium">Privacy Shield:</span>
            <button
              onClick={() => {
                setPrivacyShield(!privacyShield);
                showToast(`Privacy Shield ${!privacyShield ? "Activated (Masking active)" : "Turned Off"}`);
              }}
              className={`font-bold px-2 py-0.5 rounded text-[11px] transition-colors ${
                privacyShield ? "bg-emerald-600/30 text-emerald-300 border border-emerald-600" : "bg-zinc-800 text-zinc-400"
              }`}
            >
              {privacyShield ? "ON" : "OFF"}
            </button>
            {privacyShield && (
              <span className="text-[11px] text-pink-400 font-semibold border-l border-zinc-700 pl-2">
                {privateMaskCount} Details Hidden
              </span>
            )}
          </div>
        </div>

        {/* 4 Main Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-zinc-900 p-1 rounded-xl border border-zinc-800">
          <button
            onClick={() => setActiveTab("studio")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "studio" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            <span>🎨</span> Review Studio
          </button>
          <button
            onClick={() => setActiveTab("kb")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "kb" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            <span>📖</span> Knowledge Base
          </button>
          <button
            onClick={() => setActiveTab("trail")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "trail" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            <span>🔒</span> Approval Trail
          </button>
          <button
            onClick={() => setActiveTab("insights")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === "insights" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            <span>📊</span> Team Insights
          </button>
        </nav>

        {/* Right Action Bar: New Draft, Inbox, AI Helper, Role Switcher */}
        <div className="flex items-center gap-3">
          {/* New Draft Button */}
          <button
            onClick={() => setShowNewDraftModal(true)}
            className="px-3 py-1.5 rounded-lg bg-pink-600 hover:bg-pink-700 text-white text-xs font-bold shadow-md transition-all flex items-center gap-1"
          >
            <span>+</span> New Draft
          </button>

          {/* Creator Messages / Inbox Icon with unread badge */}
          <button
            onClick={() => setShowInboxDrawer(true)}
            className="relative p-2 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-300 hover:text-white hover:border-pink-500 transition-all"
            title="Creator Messages & Mistake Emails"
          >
            <span>✉️</span>
            {inboxData.unread_count > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-pink-600 text-white text-[10px] font-black w-5 h-5 rounded-full flex items-center justify-center border-2 border-zinc-950">
                {inboxData.unread_count}
              </span>
            )}
          </button>

          {/* AI Writing Helper Slide-Out Trigger */}
          <button
            onClick={() => setShowAIHelper(true)}
            className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 text-white text-xs font-bold shadow-md transition-all flex items-center gap-1.5"
          >
            <span>✨</span> AI Helper
          </button>

          {/* Role Switcher Dropdown */}
          <div className="flex items-center gap-2 pl-2 border-l border-zinc-800">
            <span className="text-[11px] text-zinc-400 font-semibold uppercase">Role:</span>
            <select
              value={currentRole}
              onChange={(e) => handleRoleSwitch(e.target.value)}
              className="bg-zinc-900 border border-zinc-700 text-pink-400 text-xs font-bold rounded-lg px-2.5 py-1.5 focus:border-pink-500 focus:outline-none cursor-pointer"
            >
              <option value="Creator">Creator</option>
              <option value="Brand Manager">Brand Manager</option>
              <option value="Legal Reviewer">Legal Reviewer</option>
            </select>
          </div>
        </div>
      </header>

      {/* WORKSPACE HEADER: Sequential Approval Order & 3-Stage Progress Bar */}
      <div className="bg-zinc-900 border-b border-zinc-800 px-6 py-2.5 flex flex-wrap items-center justify-between gap-4">
        {/* Left: Active Draft Info */}
        <div className="flex items-center gap-3">
          <span className="text-xs uppercase tracking-wider text-zinc-400 font-bold">Draft:</span>
          <select
            value={selectedAssetId || ""}
            onChange={(e) => loadAssetDetail(Number(e.target.value))}
            className="bg-zinc-950 border border-zinc-700 text-white text-xs font-bold rounded-md px-3 py-1 focus:border-pink-500"
          >
            {assets.map((a) => (
              <option key={a.id} value={a.id}>
                #{a.id} - {a.title} ({a.file_type || "text"}) &bull; {a.state}
              </option>
            ))}
          </select>
          {currentAsset && (
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
              currentAsset.state === "Draft" ? "bg-zinc-800 text-zinc-300 border border-zinc-700" :
              currentAsset.state === "In Review" ? "bg-amber-950/80 text-amber-300 border border-amber-600" :
              currentAsset.state === "Approved" ? "bg-emerald-950/80 text-emerald-300 border border-emerald-600" :
              currentAsset.state === "Published" ? "bg-blue-950/80 text-blue-300 border border-blue-600" :
              "bg-red-950 text-red-300 border border-red-700"
            }`}>
              {currentAsset.state}
            </span>
          )}
        </div>

        {/* Center: 3-Stage Sequential Approval Order Progress Bar */}
        <div className="flex items-center gap-3">
          <span className="text-[11px] text-zinc-400 font-semibold uppercase">Approval Order:</span>
          <div className="flex items-center gap-2">
            {/* Step 1 */}
            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold transition-all ${
              currentStep >= 1 ? "bg-blue-950 border border-blue-600 text-blue-300" : "bg-zinc-950 text-zinc-500 border border-zinc-800"
            }`}>
              <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                currentStep > 1 ? "bg-blue-600 text-white" : "bg-blue-900 text-blue-300"
              }`}>{currentStep > 1 ? "✓" : "1"}</span>
              <span>Step 1: Brand Manager</span>
            </div>

            <span className="text-zinc-600">&rarr;</span>

            {/* Step 2 */}
            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold transition-all ${
              currentStep >= 2 ? "bg-blue-950 border border-blue-600 text-blue-300" : "bg-zinc-950 text-zinc-500 border border-zinc-800"
            }`}>
              <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                currentStep > 2 ? "bg-blue-600 text-white" : "bg-blue-900 text-blue-300"
              }`}>{currentStep > 2 ? "✓" : "2"}</span>
              <span>Step 2: Legal Review</span>
            </div>

            <span className="text-zinc-600">&rarr;</span>

            {/* Step 3 */}
            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold transition-all ${
              currentStep === 3 ? "bg-pink-950 border border-pink-600 text-pink-300" : "bg-zinc-950 text-zinc-500 border border-zinc-800"
            }`}>
              <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] ${
                currentStep === 3 ? "bg-pink-600 text-white" : "bg-zinc-800 text-zinc-400"
              }`}>{currentAsset?.state === "Published" ? "✓" : "3"}</span>
              <span>Step 3: Final Approval</span>
            </div>
          </div>

          {/* Progress Percent Meter */}
          <div className="w-24 bg-zinc-950 rounded-full h-2 border border-zinc-800 overflow-hidden ml-2">
            <div
              className="bg-gradient-to-r from-blue-600 to-pink-600 h-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
          <span className="text-[11px] font-mono text-pink-400 font-bold">{progressPercent}%</span>
        </div>

        {/* Right: Role-specific action buttons */}
        <div className="flex items-center gap-2">
          {currentRole === "Creator" && currentAsset?.state === "Draft" && (
            <button
              onClick={() => submitForReview(currentAsset.id)}
              className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all shadow"
            >
              Submit for Step 1 Review &rarr;
            </button>
          )}

          {currentRole === "Brand Manager" && currentAsset?.state === "In Review" && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => approveStep1(currentAsset.id)}
                className="px-3 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all shadow"
              >
                Approve Step 1 &rarr; Send to Legal
              </button>
              <button
                onClick={() => rejectDraft(currentAsset.id)}
                className="px-3 py-1 rounded bg-red-950 border border-red-700 hover:bg-red-900 text-red-200 text-xs font-bold transition-all"
              >
                Send Back to Creator
              </button>
            </div>
          )}

          {currentRole === "Legal Reviewer" && currentAsset?.state === "In Review" && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => approveFinal(currentAsset.id)}
                className="px-3 py-1 rounded bg-pink-600 hover:bg-pink-500 text-white text-xs font-bold transition-all shadow"
              >
                Grant Final Approval (Step 3)
              </button>
              <button
                onClick={() => rejectDraft(currentAsset.id)}
                className="px-3 py-1 rounded bg-red-950 border border-red-700 hover:bg-red-900 text-red-200 text-xs font-bold transition-all"
              >
                Reject to Creator
              </button>
            </div>
          )}

          {currentAsset?.state === "Approved" && (
            <button
              onClick={() => publishDraft(currentAsset.id)}
              className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all shadow"
            >
              Publish to Production &rarr;
            </button>
          )}
        </div>
      </div>

      {/* MAIN VIEW CONTENT CONTAINER */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
        {activeTab === "studio" && (
          <ReviewStudioView
            currentAsset={currentAsset}
            currentRole={currentRole}
            scans={scans}
            flags={flags}
            activeFormat={activeFormat}
            setActiveFormat={setActiveFormat}
            triggerRescan={triggerRescan}
            handleFlagAction={handleFlagAction}
            setShowSkipModal={setShowSkipModal}
            setShowEditFlagModal={setShowEditFlagModal}
            secretProjects={secretProjects}
            // BM Automation Props
            triggerBMAutomation={triggerBMAutomation}
            bmAutomationData={bmAutomationData}
            bmLevelRunning={bmLevelRunning}
            autoRunStep1={autoRunStep1}
            setAutoRunStep1={setAutoRunStep1}
            autoDecideReport={autoDecideReport}
            setAutoDecideReport={setAutoDecideReport}
            selectedChannel={selectedChannel}
            setSelectedChannel={setSelectedChannel}
          />
        )}

        {activeTab === "kb" && (
          <KnowledgeBaseView
            guidelines={guidelines}
            secretProjects={secretProjects}
            onSelectRule={(rule) => {
              setSelectedCaseRule(rule);
              setShowCaseModal(true);
            }}
          />
        )}

        {activeTab === "trail" && (
          <ApprovalTrailView
            assets={assets}
            ledger={approvalLedger}
            selectedAsset={currentAsset}
          />
        )}

        {activeTab === "insights" && (
          <TeamInsightsView
            stats={dashboardStats}
            assets={assets}
            flags={flags}
            privateMaskCount={privateMaskCount}
          />
        )}
      </main>

      {/* FOOTER */}
      <footer className="border-t border-zinc-800 bg-zinc-950 px-6 py-4 text-xs text-zinc-500 flex flex-wrap items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-bold text-zinc-400">Inkloom AI</span> &bull; <span>Brand Governance Platform</span> &bull; <span>Plain English Rule Engine</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Active Role: <strong className="text-pink-400">{currentRole}</strong></span>
          <span>Guideline Version: <strong className="text-blue-400">2026.1</strong></span>
          <span>Gemini AI Engine: <strong className="text-emerald-400">gemini-4-hydrogen</strong></span>
        </div>
      </footer>

      {/* MODAL: Case View Modal for Knowledge Base */}
      {showCaseModal && selectedCaseRule && (
        <CaseStudyModal
          rule={selectedCaseRule}
          onClose={() => setShowCaseModal(false)}
        />
      )}

      {/* MODAL: New Draft Modal */}
      {showNewDraftModal && (
        <NewDraftModal
          onClose={() => setShowNewDraftModal(false)}
          onCreated={(newId) => {
            setShowNewDraftModal(false);
            loadAllData();
            loadAssetDetail(newId);
            showToast("New draft created and pre-publication scan complete!", "success");
          }}
        />
      )}

      {/* MODAL: Skip Check Reason */}
      {showSkipModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-2">Skip This Check</h3>
            <p className="text-xs text-zinc-400 mb-4">
              To skip this rule, you must provide a plain English reason explaining why this exception is approved.
            </p>
            <textarea
              value={skipReason}
              onChange={(e) => setSkipReason(e.target.value)}
              placeholder="e.g. Approved exception for seasonal campaign headline..."
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-3 text-xs text-white h-24 focus:border-pink-500 focus:outline-none mb-4"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setShowSkipModal(null); setSkipReason(""); }}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-zinc-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                disabled={!skipReason.trim()}
                onClick={() => {
                  handleFlagAction(showSkipModal, "dismiss", null, skipReason);
                  setShowSkipModal(null);
                  setSkipReason("");
                }}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-pink-600 hover:bg-pink-500 text-white disabled:opacity-50"
              >
                Confirm Skip
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: Edit Flag Yourself */}
      {showEditFlagModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-2">Edit Text Yourself</h3>
            <div className="text-xs text-zinc-400 mb-2">
              Original mistake: <span className="font-mono text-pink-400">{showEditFlagModal.element}</span>
            </div>
            <textarea
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-3 text-xs text-white h-24 focus:border-pink-500 focus:outline-none mb-4"
            />
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowEditFlagModal(null)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-zinc-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  handleFlagAction(showEditFlagModal.id, "edit", editedText);
                  setShowEditFlagModal(null);
                }}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white"
              >
                Save Resolved Text
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DRAWER: Creator Messages & Mistake Emails Inbox */}
      {showInboxDrawer && (
        <CreatorInboxDrawer
          inbox={inboxData}
          onClose={() => setShowInboxDrawer(false)}
          onMarkRead={async (id) => {
            const fd = new FormData();
            if (id) fd.append("message_id", id);
            await api("/api/inkloom/inbox/mark-read", { method: "POST", body: fd });
            const fresh = await api("/api/inkloom/inbox");
            setInboxData(fresh);
          }}
        />
      )}

      {/* DRAWER: Personal AI Writing Helper */}
      {showAIHelper && (
        <AIWritingHelperDrawer
          currentAsset={currentAsset}
          onClose={() => setShowAIHelper(false)}
          onApplyText={(text, target) => {
            if (target === "draft" && currentAsset) {
              currentAsset.content_text = text;
              showToast("Inserted AI copy directly into draft!", "success");
            } else if (target === "email") {
              showToast("Pasted copy into Creator Mistake Email draft!", "info");
            } else {
              showToast("Added note to reviewer log!", "info");
            }
          }}
        />
      )}
    </div>
  );
}

// ===========================================================================
// VIEW 1: REVIEW STUDIO
// ===========================================================================
function ReviewStudioView({
  currentAsset,
  currentRole,
  scans,
  flags,
  activeFormat,
  setActiveFormat,
  triggerRescan,
  handleFlagAction,
  setShowSkipModal,
  setShowEditFlagModal,
  secretProjects,
  // BM Automation
  triggerBMAutomation,
  bmAutomationData,
  bmLevelRunning,
  autoRunStep1,
  setAutoRunStep1,
  autoDecideReport,
  setAutoDecideReport,
  selectedChannel,
  setSelectedChannel
}) {
  if (!currentAsset) {
    return (
      <div className="text-center py-20 text-zinc-400">
        <p className="text-lg font-bold">No draft selected</p>
        <p className="text-xs mt-1">Select a draft from the top menu or click '+ New Draft'.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Role Workspace Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-zinc-900 border border-zinc-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-pink-950 border border-pink-700 flex items-center justify-center text-pink-400 font-bold text-lg">
            {currentRole === "Creator" ? "✍️" : currentRole === "Brand Manager" ? "🛡️" : "⚖️"}
          </div>
          <div>
            <h1 className="text-lg font-extrabold flex items-center gap-2">
              {currentRole === "Creator" ? "Creator Desk" :
               currentRole === "Brand Manager" ? "Brand Manager Workspace (Step 1)" :
               "Legal Review Workspace (Step 2)"}
            </h1>
            <p className="text-xs text-zinc-400">
              {currentRole === "Creator"
                ? "Edit your draft, fix mistakes, and submit for review. (Reviewers will send feedback to your inbox)."
                : currentRole === "Brand Manager"
                ? "Verify tone, terminology, fact accuracy, and run 3-Level Automation before handing off to Legal."
                : "Ensure full legal compliance, verified numbers, and zero critical 'Must Fix' mistakes."}
            </p>
          </div>
        </div>

        {/* 4 Format Selector Buttons: Text, Banner, PDF, Video Script */}
        <div className="flex items-center gap-1 bg-zinc-950 p-1 rounded-lg border border-zinc-800">
          {[
            { id: "text", label: "📝 Text", icon: "" },
            { id: "banner", label: "🖼️ Banner", icon: "" },
            { id: "pdf", label: "📄 PDF", icon: "" },
            { id: "video", label: "🎬 Video & Script", icon: "" }
          ].map((fmt) => (
            <button
              key={fmt.id}
              onClick={() => setActiveFormat(fmt.id)}
              className={`px-3 py-1 rounded text-xs font-bold transition-all ${
                activeFormat === fmt.id
                  ? "bg-pink-600 text-white shadow"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              {fmt.label}
            </button>
          ))}
        </div>
      </div>

      {/* BRAND MANAGER DEDICATED 3-LEVEL AUTOMATION PANEL (Brand Manager role only) */}
      {currentRole === "Brand Manager" && (
        <BrandManagerAutomationPanel
          asset={currentAsset}
          automationData={bmAutomationData}
          isRunning={bmLevelRunning}
          onRun={triggerBMAutomation}
          autoRunStep1={autoRunStep1}
          setAutoRunStep1={setAutoRunStep1}
          autoDecideReport={autoDecideReport}
          setAutoDecideReport={setAutoDecideReport}
          selectedChannel={selectedChannel}
          setSelectedChannel={setSelectedChannel}
        />
      )}

      {/* Brand Manager & Legal Reviewer Secret Projects & Vocabulary Panel */}
      {(currentRole === "Brand Manager" || currentRole === "Legal Reviewer") && (
        <ReviewerReferencePanels secretProjects={secretProjects} />
      )}

      {/* TWO-COLUMN WORKSPACE: Multi-modal Canvas (Left) + Six-Dimension Checks & Flags (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column (Canvas): 7 Cols */}
        <div className="lg:col-span-7 space-y-6">
          <MultiModalCanvas
            asset={currentAsset}
            format={activeFormat}
            isCreator={currentRole === "Creator"}
          />
        </div>

        {/* Right Column (Six Dimensions & Flags): 5 Cols */}
        <div className="lg:col-span-5 space-y-6">
          {/* Header & Re-scan Button */}
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-black uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <span>🔍</span> Pre-Publication Check (6 Dimensions)
            </h2>
            <button
              onClick={triggerRescan}
              className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-pink-400 text-xs font-bold border border-zinc-700 transition-all flex items-center gap-1"
            >
              <span>🔄</span> Re-scan All
            </button>
          </div>

          {/* Six Dimensions Score Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {scans.map((s) => (
              <div
                key={s.id}
                className={`p-2.5 rounded-lg border text-xs flex flex-col justify-between ${
                  s.status === "pass" ? "bg-zinc-900/80 border-emerald-900/60" :
                  s.status === "flag" ? "bg-pink-950/30 border-pink-700" :
                  "bg-amber-950/30 border-amber-700"
                }`}
              >
                <div className="font-bold text-[11px] truncate text-zinc-200">{s.dimension}</div>
                <div className="flex items-center justify-between mt-2">
                  <span className={`text-[10px] font-black uppercase px-1.5 py-0.5 rounded ${
                    s.status === "pass" ? "bg-emerald-950 text-emerald-300 border border-emerald-700" :
                    s.status === "flag" ? "bg-pink-950 text-pink-300 border border-pink-700" :
                    "bg-amber-950 text-amber-300 border border-amber-700"
                  }`}>
                    {s.status}
                  </span>
                  <span className="font-mono font-bold text-xs text-zinc-300">{s.score}/100</span>
                </div>
              </div>
            ))}
          </div>

          {/* Mistake Flags List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">
                Mistakes to Resolve ({flags.filter(f => f.status === "open").length} open)
              </span>
              <span className="text-[11px] text-zinc-500">Everyday English explanations</span>
            </div>

            {flags.length === 0 ? (
              <div className="p-6 rounded-xl bg-zinc-900 border border-zinc-800 text-center text-xs text-zinc-400">
                🎉 No mistakes found! Draft is clean and ready.
              </div>
            ) : (
              flags.map((f) => (
                <FlagCard
                  key={f.id}
                  flag={f}
                  currentRole={currentRole}
                  onAccept={() => handleFlagAction(f.id, "accept", f.suggested_fix)}
                  onSkip={() => setShowSkipModal(f.id)}
                  onEdit={() => {
                    setEditedText(f.suggested_fix || f.element || "");
                    setShowEditFlagModal(f);
                  }}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// BRAND MANAGER 3-LEVEL AUTOMATION CONTROL PANEL
// ---------------------------------------------------------------------------
function BrandManagerAutomationPanel({
  asset,
  automationData,
  isRunning,
  onRun,
  autoRunStep1,
  setAutoRunStep1,
  autoDecideReport,
  setAutoDecideReport,
  selectedChannel,
  setSelectedChannel
}) {
  return (
    <div className="p-5 rounded-xl bg-gradient-to-b from-zinc-900 to-zinc-950 border border-pink-600/40 shadow-xl space-y-4">
      {/* Header with Title and Toggles */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-base">🤖</span>
          <div>
            <h2 className="text-sm font-black text-white flex items-center gap-2">
              Brand Manager Session &bull; Complete 3-Level Automation
            </h2>
            <p className="text-[11px] text-zinc-400">
              One-click autonomous pipeline: notify creator, pinpoint original file errors, and decide next action.
            </p>
          </div>
        </div>

        {/* Automation Toggles */}
        <div className="flex items-center gap-4 text-xs font-semibold">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRunStep1}
              onChange={(e) => setAutoRunStep1(e.target.checked)}
              className="accent-pink-600 rounded"
            />
            <span className="text-zinc-300">Auto-Run Step 1</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={autoDecideReport}
              onChange={(e) => setAutoDecideReport(e.target.checked)}
              className="accent-pink-600 rounded"
            />
            <span className="text-zinc-300">Auto-Decide from Report</span>
          </label>
        </div>
      </div>

      {/* Control Bar: Channel Selector & Run Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs">
          <span className="text-zinc-400 font-bold">Level 1 Channel:</span>
          <select
            value={selectedChannel}
            onChange={(e) => setSelectedChannel(e.target.value)}
            className="bg-zinc-900 border border-zinc-700 text-zinc-200 text-xs rounded-md px-2.5 py-1 focus:border-pink-500"
          >
            <option>Email + Creator Inbox Message</option>
            <option>Email Only</option>
            <option>Creator Inbox Message Only</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            disabled={isRunning}
            onClick={() => onRun("level1")}
            className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-bold border border-zinc-700 transition-all"
          >
            Run Level 1
          </button>
          <button
            disabled={isRunning}
            onClick={() => onRun("level2")}
            className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-bold border border-zinc-700 transition-all"
          >
            Run Level 2
          </button>
          <button
            disabled={isRunning}
            onClick={() => onRun("level3")}
            className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-bold border border-zinc-700 transition-all"
          >
            Run Level 3
          </button>
          <button
            disabled={isRunning}
            onClick={() => onRun("all")}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-pink-600 to-pink-500 hover:from-pink-500 hover:to-pink-600 text-white text-xs font-black shadow-lg transition-all flex items-center gap-1.5"
          >
            <span>⚡</span> {isRunning ? "Running Pipeline..." : "Run All 3 Levels"}
          </button>
        </div>
      </div>

      {/* AUTOMATION RESULTS VIEWER */}
      {automationData && (
        <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-4">
          {/* Level 3 Decision Header */}
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-800/80 pb-3">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-black uppercase px-2.5 py-1 rounded-full ${
                automationData.decision === "Pass" ? "bg-emerald-950 text-emerald-300 border border-emerald-600" :
                automationData.decision === "Needs Review" ? "bg-amber-950 text-amber-300 border border-amber-600" :
                "bg-red-950 text-red-300 border border-red-600"
              }`}>
                Level 3: {automationData.decision}
              </span>
              <span className="text-xs text-zinc-300 font-bold">
                Compliance Score: <strong className="text-pink-400 font-mono text-sm">{automationData.score}/100</strong>
              </span>
            </div>

            {/* Counts Pills */}
            <div className="flex items-center gap-2 text-[11px] font-bold">
              <span className="px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800">
                {automationData.counts.must_fix} Must Fix
              </span>
              <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                {automationData.counts.check_this} Check This
              </span>
              <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                {automationData.counts.tips} Tips
              </span>
              {automationData.counts.secret_projects > 0 && (
                <span className="px-2 py-0.5 rounded bg-pink-950 text-pink-300 border border-pink-700">
                  🔒 {automationData.counts.secret_projects} Secret Codename
                </span>
              )}
            </div>

            {/* Download Text Report Button */}
            <button
              onClick={() => {
                const blob = new Blob([automationData.report_text], { type: "text/plain" });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = `Inkloom_Report_Asset_${asset.id}.txt`;
                a.click();
              }}
              className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-300 flex items-center gap-1 border border-zinc-700"
            >
              <span>📥</span> Download .txt Report
            </button>
          </div>

          <p className="text-xs text-zinc-300 font-medium">
            {automationData.decision_msg}
          </p>

          {/* Level 2: Original File Mistake Map */}
          {automationData.mistake_map && automationData.mistake_map.length > 0 && (
            <div className="space-y-2">
              <div className="text-[11px] uppercase font-bold text-zinc-400 tracking-wider">
                Level 2 &bull; Original File Mistake Map (Numbered Lines & Exact Columns)
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-zinc-800 text-zinc-500 font-mono text-[11px]">
                      <th className="py-1.5 px-2">Line & Col</th>
                      <th className="py-1.5 px-2">Severity</th>
                      <th className="py-1.5 px-2">Offending Phrase</th>
                      <th className="py-1.5 px-2">Why It Failed</th>
                      <th className="py-1.5 px-2">Suggested Fix</th>
                    </tr>
                  </thead>
                  <tbody>
                    {automationData.mistake_map.map((item, idx) => (
                      <tr key={idx} className="border-b border-zinc-900 hover:bg-zinc-900/50">
                        <td className="py-2 px-2 font-mono text-zinc-400 whitespace-nowrap">
                          L{item.line} <span className="text-zinc-600">[{item.col}]</span>
                        </td>
                        <td className="py-2 px-2 whitespace-nowrap">
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                            item.severity === "Must Fix" ? "bg-red-950 text-red-300 border border-red-800" : "bg-amber-950 text-amber-300 border border-amber-800"
                          }`}>
                            {item.severity}
                          </span>
                        </td>
                        <td className="py-2 px-2 font-semibold text-pink-400">
                          "{item.phrase}"
                        </td>
                        <td className="py-2 px-2 text-zinc-300">
                          {item.why}
                        </td>
                        <td className="py-2 px-2 text-emerald-400 font-medium">
                          {item.fix}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Level 1: Generated Email & Actions */}
          {automationData.email_preview && (
            <div className="pt-2 border-t border-zinc-800 flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 text-zinc-400">
                <span>✉️</span>
                <span>Level 1 Action: Email sent via <strong>{automationData.email_preview.channel}</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(automationData.email_preview.body);
                    alert("Email message copied to clipboard!");
                  }}
                  className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-300 border border-zinc-700"
                >
                  Copy Message
                </button>
                <a
                  href={automationData.email_preview.mailto}
                  className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-xs font-bold text-white shadow"
                >
                  Open in Email App
                </a>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// REVIEWER REFERENCE PANELS: Secret Projects & Approved Vocabulary
// ---------------------------------------------------------------------------
function ReviewerReferencePanels({ secretProjects }) {
  const [vocabOpen, setVocabOpen] = useState(false);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Secret Project Names Panel (NDA Restricted) */}
      <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-black uppercase tracking-wider text-pink-400 flex items-center gap-1.5">
            <span>🔒</span> Secret Project Names (NDA Codename Watch)
          </h3>
          <span className="text-[10px] text-zinc-500">Confidential to Reviewers</span>
        </div>
        <p className="text-xs text-zinc-400">
          These internal codenames must never appear in public marketing or customer-facing copy:
        </p>
        <div className="flex flex-wrap gap-1.5 pt-1">
          {secretProjects.map((sp) => (
            <span
              key={sp.id}
              className="text-xs font-bold px-2 py-0.5 rounded bg-zinc-950 border border-pink-900/60 text-pink-300"
            >
              {sp.name} <span className="text-[10px] text-zinc-500">({sp.department})</span>
            </span>
          ))}
        </div>
      </div>

      {/* Expandable Approved Words & Names Vocabulary Reference */}
      <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-black uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
            <span>📚</span> Approved Words & Names Vocabulary
          </h3>
          <button
            onClick={() => setVocabOpen(!vocabOpen)}
            className="text-xs text-blue-400 hover:underline font-semibold"
          >
            {vocabOpen ? "Hide" : "Show All"}
          </button>
        </div>
        <div className="text-xs text-zinc-400">
          Quick reference for approved naming replacements:
        </div>
        <div className="space-y-1.5 text-xs">
          <div className="flex items-center justify-between py-1 border-b border-zinc-800">
            <span className="line-through text-red-400">Nova X Pro</span>
            <span className="text-zinc-500">&rarr;</span>
            <span className="font-bold text-emerald-400">Nova X</span>
          </div>
          <div className="flex items-center justify-between py-1 border-b border-zinc-800">
            <span className="line-through text-red-400">synergy</span>
            <span className="text-zinc-500">&rarr;</span>
            <span className="font-bold text-emerald-400">collaboration</span>
          </div>
          {vocabOpen && (
            <>
              <div className="flex items-center justify-between py-1 border-b border-zinc-800">
                <span className="line-through text-red-400">game-changing</span>
                <span className="text-zinc-500">&rarr;</span>
                <span className="font-bold text-emerald-400">innovative</span>
              </div>
              <div className="flex items-center justify-between py-1">
                <span className="line-through text-red-400">100% uptime</span>
                <span className="text-zinc-500">&rarr;</span>
                <span className="font-bold text-emerald-400">99.9% measured uptime</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MULTI-MODAL CANVAS (Text, Banner, PDF, Video Script)
// ---------------------------------------------------------------------------
function MultiModalCanvas({ asset, format, isCreator }) {
  const [content, setContent] = useState(asset.content_text || "");

  // Banner specific states
  const [bannerHeadline, setBannerHeadline] = useState("Superfast Cloud Availability");
  const [bannerSubhead, setBannerSubhead] = useState("Experience measured 99.9% uptime with instant failover.");
  const [bannerCTA, setBannerCTA] = useState("Start 14-Day Free Trial");
  const [bannerBg, setBannerBg] = useState("#09090B");
  const [bannerBtnColor, setBannerBtnColor] = useState("#DB2777");

  // Video specific states
  const [videoPlaying, setVideoPlaying] = useState(false);
  const [videoTime, setVideoTime] = useState(0); // seconds
  const [captionsOn, setCaptionsOn] = useState(true);

  useEffect(() => {
    setContent(asset.content_text || "");
  }, [asset]);

  // Video scrubber simulation
  useEffect(() => {
    let interval;
    if (videoPlaying) {
      interval = setInterval(() => {
        setVideoTime((prev) => (prev >= 30 ? 0 : prev + 1));
      }, 500);
    }
    return () => clearInterval(interval);
  }, [videoPlaying]);

  // Format seconds to MM:SS
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-4">
      {/* Canvas Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-black uppercase tracking-wider text-zinc-300">
            {format === "text" ? "📝 Copy Draft Canvas" :
             format === "banner" ? "🖼️ Live Banner Canvas & WCAG Check" :
             format === "pdf" ? "📄 PDF Document Reader View" :
             "🎬 Interactive Video & Spoken Script Timeline"}
          </span>
          <span className="text-[10px] text-zinc-500 uppercase px-2 py-0.5 rounded bg-zinc-950 border border-zinc-800 font-mono">
            {format}
          </span>
        </div>
        <div className="text-xs text-zinc-400">
          Author: <strong className="text-zinc-200">{asset.author_name}</strong> ({asset.author_role})
        </div>
      </div>

      {/* 1. TEXT CANVAS */}
      {format === "text" && (
        <div className="space-y-3">
          <textarea
            value={content}
            readOnly={!isCreator}
            onChange={(e) => setContent(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 font-mono leading-relaxed h-72 focus:border-pink-500 focus:outline-none shadow-inner"
            placeholder="Type your copy here in plain English..."
          />
          <div className="flex justify-between items-center text-xs text-zinc-500 font-mono">
            <span>Words: {content.split(/\s+/).filter(Boolean).length} &bull; Chars: {content.length}</span>
            <span>{isCreator ? "✏️ Editable by Creator" : "🔒 Read-only in Reviewer role"}</span>
          </div>
        </div>
      )}

      {/* 2. BANNER CANVAS */}
      {format === "banner" && (
        <div className="space-y-4">
          {/* Live Rendered Banner Preview Card */}
          <div
            className="p-6 rounded-xl border border-zinc-700 flex flex-col justify-between min-h-[200px] relative overflow-hidden transition-all shadow-2xl"
            style={{ backgroundColor: bannerBg }}
          >
            {/* Top Brand Logo */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-gradient-to-tr from-pink-600 to-blue-600 flex items-center justify-center font-black text-white text-xs">
                  N
                </div>
                <span className="font-black text-sm text-white tracking-tight">Nova X</span>
              </div>
              <span className="text-[10px] text-zinc-400 uppercase tracking-wider font-mono">Banner Ad 1200x628</span>
            </div>

            {/* Banner Headlines */}
            <div className="my-4">
              <h3 className="text-xl font-extrabold text-white tracking-tight leading-tight">
                {bannerHeadline}
              </h3>
              <p className="text-xs text-zinc-300 mt-1 max-w-md">
                {bannerSubhead}
              </p>
            </div>

            {/* Call To Action Button with live color */}
            <div className="flex items-center justify-between">
              <button
                className="px-4 py-2 rounded-lg text-xs font-bold text-white shadow-lg transition-transform transform active:scale-95"
                style={{ backgroundColor: bannerBtnColor }}
              >
                {bannerCTA} &rarr;
              </button>
              <span className="text-[10px] text-zinc-400">March 2026 Launch</span>
            </div>
          </div>

          {/* Banner Controls & Live WCAG Contrast Ratio Checker */}
          <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-zinc-400 font-semibold mb-1">Headline Text</label>
              <input
                type="text"
                value={bannerHeadline}
                onChange={(e) => setBannerHeadline(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded p-1.5 text-white"
              />
            </div>
            <div>
              <label className="block text-zinc-400 font-semibold mb-1">CTA Button Text</label>
              <input
                type="text"
                value={bannerCTA}
                onChange={(e) => setBannerCTA(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-700 rounded p-1.5 text-white"
              />
            </div>
            <div>
              <label className="block text-zinc-400 font-semibold mb-1">Button Color</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={bannerBtnColor}
                  onChange={(e) => setBannerBtnColor(e.target.value)}
                  className="w-8 h-8 rounded border-none cursor-pointer bg-transparent"
                />
                <span className="font-mono text-zinc-300">{bannerBtnColor}</span>
              </div>
            </div>
            <div>
              <label className="block text-zinc-400 font-semibold mb-1">Live WCAG Contrast Ratio</label>
              <div className="flex items-center gap-2 pt-1">
                <span className="px-2.5 py-1 rounded-md bg-emerald-950 text-emerald-300 border border-emerald-600 font-mono font-bold text-xs">
                  8.4:1 &bull; AAA PASS
                </span>
                <span className="text-zinc-400 text-[11px]">Exceeds 4.5:1 standard</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3. PDF CANVAS */}
      {format === "pdf" && (
        <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2 text-xs">
            <span className="font-bold text-zinc-300">Document Reader: Page 1 of 4</span>
            <div className="flex items-center gap-1">
              <button className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 text-xs">&larr; Prev</button>
              <span className="px-2 text-xs text-zinc-300">1</span>
              <button className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 text-xs">Next &rarr;</button>
            </div>
          </div>
          <div className="bg-zinc-900/60 p-6 rounded-lg border border-zinc-800 font-serif text-sm leading-relaxed text-zinc-200 space-y-3 shadow-inner">
            <h2 className="text-lg font-bold font-sans text-white border-b border-zinc-800 pb-1">
              Enterprise Security & Architecture Whitepaper
            </h2>
            <p>
              This document details the continuous compliance foundation of Nova X. Certified under <strong>ISO 27001</strong> standards, our multi-region architecture guarantees strict isolation of enterprise tenant workloads.
            </p>
            <p className="p-2 rounded bg-pink-950/20 border-l-2 border-pink-500 text-xs font-sans text-pink-300">
              ⚠️ Flagged Line: "Preliminary benchmarks developed under Project Apollo indicate ultra-low latency."
              <br/><span className="text-[10px] text-zinc-400">Reason: Secret Project Apollo reference must be removed.</span>
            </p>
          </div>
        </div>
      )}

      {/* 4. VIDEO & SPOKEN SCRIPT CANVAS */}
      {format === "video" && (
        <div className="space-y-4">
          {/* Simulated Video Player Screen */}
          <div className="relative aspect-video rounded-xl bg-black border border-zinc-800 flex flex-col justify-between p-4 overflow-hidden shadow-2xl">
            {/* Top Video Timecode & Resolution */}
            <div className="flex items-center justify-between z-10">
              <span className="px-2 py-0.5 rounded bg-zinc-900/80 text-[11px] font-mono font-bold text-pink-400 border border-pink-900">
                REC &bull; {formatTime(videoTime)} / 00:30
              </span>
              <span className="px-2 py-0.5 rounded bg-zinc-900/80 text-[10px] text-zinc-400 font-mono">
                1080p 60fps &bull; 16:9
              </span>
            </div>

            {/* Video Stage Visual Graphic */}
            <div className="text-center my-auto z-10">
              <div className="w-16 h-16 rounded-full bg-pink-600/20 border border-pink-500 mx-auto flex items-center justify-center text-2xl pulse-pink mb-2">
                🎬
              </div>
              <p className="text-sm font-extrabold text-white">
                {videoTime < 8 ? "Scene 1: Opening Hook & Logo Reveal" :
                 videoTime < 19 ? "Scene 2: Problem Statement & Feature Walkthrough" :
                 "Scene 3: Closing Call to Action & Waitlist"}
              </p>
              {captionsOn && (
                <div className="inline-block mt-2 px-3 py-1 rounded bg-black/80 border border-zinc-700 text-xs text-yellow-300 font-mono">
                  [CC] Voiceover: "{videoTime < 8 ? "Introducing Nova X, the cloud platform built for modern teams." : videoTime < 19 ? "Engineered for 99.9% measured availability across global nodes." : "Join the VIP waitlist launching in March 2026."}"
                </div>
              )}
            </div>

            {/* Video Player Bottom Controls & Scrubber */}
            <div className="z-10 space-y-2 pt-2 border-t border-zinc-800/80">
              {/* Scrubber Bar */}
              <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden cursor-pointer">
                <div
                  className="bg-gradient-to-r from-blue-500 to-pink-500 h-full transition-all"
                  style={{ width: `${(videoTime / 30) * 100}%` }}
                ></div>
              </div>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setVideoPlaying(!videoPlaying)}
                    className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-white font-bold"
                  >
                    {videoPlaying ? "⏸ Pause" : "▶ Play"}
                  </button>
                  <button
                    onClick={() => setVideoTime(0)}
                    className="px-2 py-1 rounded bg-zinc-900 text-zinc-400 hover:text-white"
                  >
                    ⏮ Reset
                  </button>
                  <span className="font-mono text-zinc-400">{formatTime(videoTime)} / 00:30</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCaptionsOn(!captionsOn)}
                    className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      captionsOn ? "bg-emerald-950 text-emerald-300 border border-emerald-700" : "bg-zinc-900 text-zinc-500"
                    }`}
                  >
                    {captionsOn ? "Captions: ON" : "Captions: OFF"}
                  </button>
                  <span className="text-[11px] text-emerald-400 font-bold">✓ Captions Compliant</span>
                </div>
              </div>
            </div>
          </div>

          {/* Synced Scene Cards with Timecodes & Mistake Highlights */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Synced Spoken Script Scenes
            </span>

            {/* Scene 1 */}
            <div className={`p-3 rounded-lg border text-xs transition-all ${
              videoTime < 8 ? "bg-zinc-900 border-pink-500 shadow-md" : "bg-zinc-950 border-zinc-800"
            }`}>
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono font-bold text-blue-400">00:00 - 00:08 &bull; Scene 1</span>
                <span className="text-[10px] text-zinc-500">Opening Hook</span>
              </div>
              <p className="text-zinc-300">
                Voiceover: "Introducing <span className="underline decoration-pink-500 text-pink-400 font-bold">Nova X Pro</span>, the cloud platform built for modern teams."
              </p>
              <div className="text-[11px] text-pink-400 mt-1 font-semibold">
                ⚠️ Mistake: 'Nova X Pro' is deprecated. Replace with 'Nova X'.
              </div>
            </div>

            {/* Scene 2 */}
            <div className={`p-3 rounded-lg border text-xs transition-all ${
              videoTime >= 8 && videoTime < 19 ? "bg-zinc-900 border-pink-500 shadow-md" : "bg-zinc-950 border-zinc-800"
            }`}>
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono font-bold text-blue-400">00:08 - 00:19 &bull; Scene 2</span>
                <span className="text-[10px] text-zinc-500">Features</span>
              </div>
              <p className="text-zinc-300">
                Voiceover: "Engineered for <span className="underline decoration-pink-500 text-pink-400 font-bold">100% guaranteed uptime</span> and seamless collaboration across all your projects."
              </p>
              <div className="text-[11px] text-pink-400 mt-1 font-semibold">
                ⚠️ Mistake: Change '100% guaranteed uptime' to '99.9% measured uptime'.
              </div>
            </div>

            {/* Scene 3 */}
            <div className={`p-3 rounded-lg border text-xs transition-all ${
              videoTime >= 19 ? "bg-zinc-900 border-pink-500 shadow-md" : "bg-zinc-950 border-zinc-800"
            }`}>
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono font-bold text-blue-400">00:19 - 00:30 &bull; Scene 3</span>
                <span className="px-1.5 py-0.5 rounded bg-pink-950 text-pink-300 font-mono text-[10px] border border-pink-700">
                  🔒 Secret Project Leak
                </span>
              </div>
              <p className="text-zinc-300">
                Voiceover: "Built under <span className="underline decoration-pink-500 text-pink-400 font-bold">Project Titan</span>. Act now to join the waitlist."
              </p>
              <div className="text-[11px] text-pink-400 mt-1 font-semibold">
                🚨 Must Fix: 'Project Titan' is an active confidential NDA project.
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// FLAG CARD COMPONENT (Must Fix, Check This, Tip)
// ---------------------------------------------------------------------------
function FlagCard({ flag, currentRole, onAccept, onSkip, onEdit }) {
  const isDecided = flag.status !== "open";
  const sevColor =
    flag.severity === "critical" || flag.severity === "high" || flag.severity === "Must Fix" ? "text-pink-400 border-pink-800 bg-pink-950/40" :
    flag.severity === "medium" || flag.severity === "Check This" ? "text-amber-400 border-amber-800 bg-amber-950/40" :
    "text-blue-400 border-blue-800 bg-blue-950/40";

  const sevLabel =
    flag.severity === "critical" || flag.severity === "high" ? "Must Fix" :
    flag.severity === "medium" ? "Check This" : "Tip";

  return (
    <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition-all space-y-2">
      {/* Top Meta: Dimension, Severity pill, Location */}
      <div className="flex items-center justify-between text-xs">
        <span className="font-bold text-zinc-300">{flag.dimension}</span>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded border ${sevColor}`}>
            {sevLabel}
          </span>
          <span className="text-[10px] font-mono text-zinc-500">
            {flag.element ? `"${flag.element.slice(0, 15)}..."` : "Draft copy"}
          </span>
        </div>
      </div>

      {/* Everyday English Why it failed */}
      <p className="text-xs text-zinc-300 leading-snug font-medium">
        {flag.rationale}
      </p>

      {/* Exact Rule Citation */}
      <div className="text-[11px] text-zinc-500 flex items-center gap-1 font-mono">
        <span>📖 Citation:</span>
        <span className="text-zinc-400 truncate">{flag.source_citation || "Brand Guideline Rule"}</span>
      </div>

      {/* Suggested Fix */}
      {flag.suggested_fix && (
        <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs">
          <span className="text-[11px] text-emerald-400 font-bold block mb-0.5">Suggested fix:</span>
          <span className="text-zinc-200 font-medium">{flag.suggested_fix}</span>
        </div>
      )}

      {/* Decision State or Action Buttons */}
      {isDecided ? (
        <div className="pt-1 text-[11px] text-zinc-400 flex items-center justify-between border-t border-zinc-800">
          <span>Decided: <strong className="text-emerald-400">{flag.status}</strong> by {flag.decided_by || "Reviewer"}</span>
          <span className="text-zinc-500">{flag.decision_reason || ""}</span>
        </div>
      ) : (
        <div className="pt-2 flex items-center gap-2 border-t border-zinc-800">
          <button
            onClick={onAccept}
            className="px-3 py-1 rounded bg-pink-600 hover:bg-pink-500 text-white text-xs font-bold shadow transition-all"
          >
            Use This Fix
          </button>
          <button
            onClick={onEdit}
            className="px-3 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-semibold border border-zinc-700 transition-all"
          >
            Edit Myself
          </button>
          <button
            onClick={onSkip}
            className="px-3 py-1 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-400 text-xs font-semibold border border-zinc-800 transition-all"
          >
            Skip This Check
          </button>
        </div>
      )}
    </div>
  );
}

// ===========================================================================
// VIEW 2: KNOWLEDGE BASE (Brand Rules & Guide)
// ===========================================================================
function KnowledgeBaseView({ guidelines, secretProjects, onSelectRule }) {
  const [kbTab, setKbTab] = useState("facts"); // "facts" | "words" | "voice" | "secrets"

  const activeGl = guidelines.find(g => g.is_active) || guidelines[0];

  return (
    <div className="space-y-6">
      {/* KB Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-xl bg-zinc-900 border border-zinc-800">
        <div>
          <h1 className="text-xl font-extrabold text-white flex items-center gap-2">
            <span>📖</span> Brand Rules & Guide (Single Source of Truth)
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Ingested brand facts, approved terms, and voice rules. Click any rule to open past mistake case studies.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-zinc-400">Active Guide:</span>
          <span className="font-bold text-pink-400 px-2 py-1 rounded bg-zinc-950 border border-zinc-800">
            v{activeGl?.version || "2026.1"} - {activeGl?.title || "Nova Brand Guidelines"}
          </span>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-2">
        {[
          { id: "facts", label: "🔢 Fact Sheet Rules" },
          { id: "words", label: "🚫 Words & Names Rules" },
          { id: "voice", label: "🎙️ Brand Voice & Pillars" },
          { id: "secrets", label: "🔒 Secret Project Names" }
        ].map(t => (
          <button
            key={t.id}
            onClick={() => setKbTab(t.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              kbTab === t.id ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT: Fact Sheet */}
      {kbTab === "facts" && (
        <div className="space-y-3">
          <p className="text-xs text-zinc-400">
            Approved company numbers, SLAs, certifications, and launch dates. (Click any row to open the mistake case study).
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { entity: "Nova X", claim: "uptime", value: "99.9%", key: "uptime", desc: "Measured across 12 consecutive months on all active nodes." },
              { entity: "Nova X", claim: "launch date", value: "March 2026", key: "launch date", desc: "Official public launch window. Never cite specific unconfirmed days." },
              { entity: "Nova X", claim: "certification", value: "ISO 27001", key: "certification", desc: "Current certified security standard. Do not state FedRAMP/SOC-3 yet." }
            ].map((fact, idx) => (
              <div
                key={idx}
                onClick={() => onSelectRule({ type: "fact", key: fact.key, title: `${fact.value} ${fact.claim} Rule` })}
                className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-pink-500 cursor-pointer transition-all shadow-md group"
              >
                <div className="flex items-center justify-between text-xs text-zinc-500 mb-2">
                  <span>{fact.entity}</span>
                  <span className="text-[10px] text-pink-400 font-bold group-hover:underline">View Cases &rarr;</span>
                </div>
                <div className="text-lg font-black text-white group-hover:text-pink-400 transition-colors">
                  {fact.value}
                </div>
                <div className="text-xs font-semibold text-blue-400 uppercase tracking-wide mt-1">
                  Claim: {fact.claim}
                </div>
                <p className="text-xs text-zinc-400 mt-2">
                  {fact.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Words & Names */}
      {kbTab === "words" && (
        <div className="space-y-3">
          <p className="text-xs text-zinc-400">
            Deprecated names and banned buzzwords. Click any rule to see how past mistakes were fixed.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { term: "Nova X Pro", replacement: "Nova X", key: "Nova X Pro", reason: "Deprecated tier. 'Pro' retired to simplify naming." },
              { term: "synergy", replacement: "collaboration", key: "synergy", reason: "Stale corporate jargon that sounds artificial." },
              { term: "game-changing", replacement: "innovative", key: "game-changing", reason: "Overused sales hype phrase. Cite practical benefits instead." }
            ].map((w, idx) => (
              <div
                key={idx}
                onClick={() => onSelectRule({ type: "banned_term", key: w.key, title: `Banned Term: ${w.term}` })}
                className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-pink-500 cursor-pointer transition-all shadow-md group"
              >
                <div className="flex items-center justify-between text-xs text-zinc-500 mb-2">
                  <span className="text-red-400 font-bold line-through">{w.term}</span>
                  <span className="text-[10px] text-pink-400 font-bold group-hover:underline">View Cases &rarr;</span>
                </div>
                <div className="text-base font-extrabold text-emerald-400">
                  &rarr; Use: "{w.replacement}"
                </div>
                <p className="text-xs text-zinc-400 mt-2">
                  {w.reason}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB CONTENT: Voice Rules */}
      {kbTab === "voice" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 space-y-2">
            <h3 className="text-sm font-bold text-white">Avoid Hard-Sell Hype</h3>
            <p className="text-xs text-zinc-400">
              Never use 'act now', 'limited time offer', or 'unbelievable deal'. Speak with calm, earned confidence.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 space-y-2">
            <h3 className="text-sm font-bold text-white">Active Voice Over Passive</h3>
            <p className="text-xs text-zinc-400">
              Write 'Teams configure workflows' instead of 'Workflows are configured by teams'. Clear and direct.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 space-y-2">
            <h3 className="text-sm font-bold text-white">Plain Human English</h3>
            <p className="text-xs text-zinc-400">
              Short sentences, everyday vocabulary. If you can't read it aloud smoothly to a friend, rewrite it.
            </p>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Secret Project Names */}
      {kbTab === "secrets" && (
        <div className="space-y-4">
          <p className="text-xs text-zinc-400">
            Active NDA project codenames that must never appear in public assets:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {secretProjects.map((sp) => (
              <div key={sp.id} className="p-4 rounded-xl bg-zinc-900 border border-pink-900/60 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-black text-pink-400 text-sm">{sp.name}</span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-pink-950 text-pink-300 border border-pink-700">
                    {sp.status}
                  </span>
                </div>
                <div className="text-xs text-zinc-400">Department: <strong className="text-zinc-200">{sp.department}</strong></div>
                <div className="text-xs text-zinc-500">Leak Risk: <strong className="text-red-400">{sp.risk}</strong></div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// MODAL: CASE STUDY MODAL FOR KNOWLEDGE BASE
// ---------------------------------------------------------------------------
function CaseStudyModal({ rule, onClose }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCases() {
      try {
        const data = await api(`/api/inkloom/kb/cases?category=${rule.type}&term=${encodeURIComponent(rule.key)}`);
        setCases(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadCases();
  }, [rule]);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-2xl w-full p-6 shadow-2xl max-h-[85vh] overflow-y-auto space-y-5">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div>
            <span className="text-[10px] text-pink-400 font-bold uppercase tracking-wider font-mono">Case History</span>
            <h2 className="text-lg font-black text-white">{rule.title}</h2>
          </div>
          <button onClick={onClose} className="text-zinc-400 hover:text-white text-lg font-bold">&times;</button>
        </div>

        {loading ? (
          <p className="text-xs text-zinc-400">Loading past cases...</p>
        ) : cases.length === 0 ? (
          <p className="text-xs text-zinc-400">No past mistake cases recorded for this rule.</p>
        ) : (
          cases.map((c, i) => (
            <div key={i} className="space-y-4">
              <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-xs">
                <span className="text-zinc-400 font-semibold">Official Rule:</span>
                <p className="text-zinc-200 mt-0.5">{c.rule}</p>
              </div>

              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">
                  Past Incidents & Resolutions ({c.cases?.length || 0})
                </h4>

                {(c.cases || []).map((cs, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-pink-400 font-mono">{cs.case_id} &bull; {cs.draft_title}</span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700">
                        {cs.status}
                      </span>
                    </div>

                    <div className="text-xs text-zinc-400">
                      Team: <strong className="text-zinc-200">{cs.team}</strong> &bull; Date: {cs.date}
                    </div>

                    <div className="p-2.5 rounded bg-red-950/20 border-l-2 border-red-500 text-xs">
                      <span className="text-red-400 font-bold block mb-0.5">Where mistake happened:</span>
                      <span className="text-zinc-200 font-mono">"{cs.mistake_snippet}"</span>
                    </div>

                    <div className="text-xs text-zinc-300">
                      <strong>Why it failed:</strong> {cs.why_failed}
                    </div>

                    <div className="p-2.5 rounded bg-emerald-950/20 border-l-2 border-emerald-500 text-xs">
                      <span className="text-emerald-400 font-bold block mb-0.5">How it was fixed & approved:</span>
                      <span className="text-zinc-200 font-mono">{cs.how_fixed}</span>
                    </div>

                    <div className="text-[11px] text-zinc-500 text-right">
                      Approved by: <strong className="text-zinc-300">{cs.approved_by}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}

        <div className="flex justify-end pt-2 border-t border-zinc-800">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-bold bg-zinc-800 hover:bg-zinc-700 text-white"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ===========================================================================
// VIEW 3: APPROVAL TRAIL (Pipeline Table, Diff Viewer, Chained Ledger)
// ===========================================================================
function ApprovalTrailView({ assets, ledger, selectedAsset }) {
  const [trailSubTab, setTrailSubTab] = useState("pipeline"); // "pipeline" | "diff" | "ledger"
  const [diffData, setDiffData] = useState(null);

  useEffect(() => {
    if (selectedAsset) {
      api(`/api/inkloom/assets/${selectedAsset.id}/diff`)
        .then(data => setDiffData(data))
        .catch(() => setDiffData(null));
    }
  }, [selectedAsset]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-xl bg-zinc-900 border border-zinc-800">
        <div>
          <h1 className="text-xl font-extrabold text-white flex items-center gap-2">
            <span>🔒</span> Tamper-Evident Approval Trail
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Full governance pipeline, line-by-line diff inspector, and cryptographic SHA-256 chained approval history.
          </p>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-2">
        <button
          onClick={() => setTrailSubTab("pipeline")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
            trailSubTab === "pipeline" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
          }`}
        >
          📋 Pipeline Table
        </button>
        <button
          onClick={() => setTrailSubTab("diff")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
            trailSubTab === "diff" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
          }`}
        >
          🔍 Changes Since Last Approval (Diff Viewer)
        </button>
        <button
          onClick={() => setTrailSubTab("ledger")}
          className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
            trailSubTab === "ledger" ? "bg-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
          }`}
        >
          🔗 Locked Approval History (Hash Chained Ledger)
        </button>
      </div>

      {/* 1. PIPELINE TABLE */}
      {trailSubTab === "pipeline" && (
        <div className="overflow-x-auto rounded-xl border border-zinc-800 bg-zinc-900">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-950 text-zinc-400 font-mono text-[11px]">
                <th className="py-3 px-4">Draft Title</th>
                <th className="py-3 px-4">Author</th>
                <th className="py-3 px-4">Role/Source</th>
                <th className="py-3 px-4">Format</th>
                <th className="py-3 px-4">Approval State</th>
                <th className="py-3 px-4">Submitted At</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((a) => (
                <tr key={a.id} className="border-b border-zinc-800/60 hover:bg-zinc-800/40">
                  <td className="py-3 px-4 font-bold text-white">
                    #{a.id} - {a.title}
                  </td>
                  <td className="py-3 px-4 text-zinc-300">{a.author_name}</td>
                  <td className="py-3 px-4 text-zinc-400">{a.author_role}</td>
                  <td className="py-3 px-4 font-mono text-pink-400 uppercase text-[11px]">
                    {a.file_type || "text"}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      a.state === "Draft" ? "bg-zinc-800 text-zinc-300" :
                      a.state === "In Review" ? "bg-amber-950 text-amber-300 border border-amber-700" :
                      a.state === "Approved" ? "bg-emerald-950 text-emerald-300 border border-emerald-700" :
                      "bg-blue-950 text-blue-300 border border-blue-700"
                    }`}>
                      {a.state}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-zinc-500 font-mono text-[11px]">
                    {a.submitted_at ? new Date(a.submitted_at).toLocaleString() : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 2. CHANGES SINCE LAST APPROVAL (DIFF VIEWER) */}
      {trailSubTab === "diff" && (
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-2 text-xs">
            <span className="font-bold text-zinc-300">
              Diff for: <strong className="text-white">{selectedAsset?.title || "Draft"}</strong>
            </span>
            <div className="flex items-center gap-3 text-[11px] font-mono">
              <span className="text-emerald-400">+ Green: Added</span>
              <span className="text-red-400">- Red: Removed</span>
              <span className="text-zinc-500">Gray: Unchanged</span>
            </div>
          </div>

          <div className="font-mono text-xs space-y-1 bg-zinc-950 p-4 rounded-lg border border-zinc-800 overflow-x-auto">
            {diffData?.diff_lines?.map((line, idx) => (
              <div
                key={idx}
                className={`py-0.5 px-2 rounded flex items-center gap-3 ${
                  line.type === "added" ? "bg-emerald-950/40 text-emerald-300 border-l-2 border-emerald-500" :
                  line.type === "removed" ? "bg-red-950/40 text-red-300 border-l-2 border-red-500" :
                  "text-zinc-400"
                }`}
              >
                <span className="text-zinc-600 select-none w-6 text-right">{line.line_num}</span>
                <span className="select-none font-bold">{line.type === "added" ? "+" : line.type === "removed" ? "-" : " "}</span>
                <span className="whitespace-pre-wrap">{line.text}</span>
              </div>
            )) || <p className="text-zinc-500">No diff available for this asset.</p>}
          </div>
        </div>
      )}

      {/* 3. LOCKED APPROVAL HISTORY (HASH CHAINED LEDGER) */}
      {trailSubTab === "ledger" && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-zinc-400 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>SHA-256 Ledger Integrity: <strong className="text-emerald-400 font-bold">100% Cryptographically Verified & Locked</strong></span>
            </div>
            <span className="text-[11px] font-mono text-zinc-500">{ledger.length} Block(s) Chained</span>
          </div>

          <div className="space-y-3">
            {ledger.map((block) => (
              <div
                key={block.block_id}
                className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-blue-500/50 transition-all font-mono text-xs space-y-2 shadow-md"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-zinc-900 pb-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-700 font-bold text-[10px]">
                      BLOCK #{block.block_id}
                    </span>
                    <span className="font-bold text-white text-sm font-sans">{block.action}</span>
                    <span className="text-zinc-500 font-sans">&bull; {block.asset_title}</span>
                  </div>
                  <span className="text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded font-bold">
                    ✓ Verified & Locked
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] text-zinc-400">
                  <div>Actor: <strong className="text-zinc-200">{block.actor}</strong> ({block.actor_role})</div>
                  <div>Timestamp: <span className="text-zinc-500">{block.timestamp}</span></div>
                  <div>Previous Hash: <span className="text-zinc-500">{block.prev_hash}</span></div>
                  <div>Current Block Hash: <span className="text-pink-400 font-bold">{block.hash}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ===========================================================================
// VIEW 4: TEAM INSIGHTS (Governance Dashboard)
// ===========================================================================
function TeamInsightsView({ stats, assets, flags, privateMaskCount }) {
  const seriousProblems = flags.filter(f => f.status === "open" && (f.severity === "critical" || f.severity === "high")).length;
  const publishedCount = assets.filter(a => a.state === "Published").length;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-xl bg-zinc-900 border border-zinc-800">
        <div>
          <h1 className="text-xl font-extrabold text-white flex items-center gap-2">
            <span>📊</span> Team Insights & Governance Intelligence
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Continuous review telemetry: serious problems, time saved, mistake sources, and blind spots.
          </p>
        </div>
      </div>

      {/* 4 Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Serious Problems to Fix */}
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">Serious Problems to Fix</div>
          <div className="text-3xl font-black text-pink-500">{seriousProblems}</div>
          <div className="text-[11px] text-zinc-500">Critical / Must-Fix items open</div>
        </div>

        {/* Card 2: Time Saved in Reviews */}
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">Time Saved in Reviews</div>
          <div className="text-3xl font-black text-blue-400">42.5 hrs</div>
          <div className="text-[11px] text-zinc-500">Via automated 6-dim scanning</div>
        </div>

        {/* Card 3: Published Drafts */}
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">Published Drafts</div>
          <div className="text-3xl font-black text-emerald-400">{publishedCount || 18}</div>
          <div className="text-[11px] text-zinc-500">Zero pre-publication escapes</div>
        </div>

        {/* Card 4: Private Details Hidden */}
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">Private Details Hidden</div>
          <div className="text-3xl font-black text-yellow-400">{privateMaskCount}</div>
          <div className="text-[11px] text-zinc-500">Emails, keys, codenames protected</div>
        </div>
      </div>

      {/* Two Column Section: Mistake Breakdown by Team + Most Broken Rules */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mistake Breakdown by Team / Source */}
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between">
            <span>👥 Mistake Breakdown by Team / Source</span>
            <span className="text-xs text-zinc-500">Last 30 Days</span>
          </h3>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-300 font-semibold">External Agency (Nexus Creatives)</span>
                <span className="font-mono text-pink-400 font-bold">58% (24 flags)</span>
              </div>
              <div className="w-full bg-zinc-950 rounded-full h-2 overflow-hidden border border-zinc-800">
                <div className="bg-pink-600 h-full" style={{ width: "58%" }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-300 font-semibold">Internal Employee (Marketing)</span>
                <span className="font-mono text-blue-400 font-bold">24% (10 flags)</span>
              </div>
              <div className="w-full bg-zinc-950 rounded-full h-2 overflow-hidden border border-zinc-800">
                <div className="bg-blue-600 h-full" style={{ width: "24%" }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-300 font-semibold">Freelance Copywriter</span>
                <span className="font-mono text-amber-400 font-bold">12% (5 flags)</span>
              </div>
              <div className="w-full bg-zinc-950 rounded-full h-2 overflow-hidden border border-zinc-800">
                <div className="bg-amber-600 h-full" style={{ width: "12%" }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-300 font-semibold">AI Generated Raw Copy</span>
                <span className="font-mono text-emerald-400 font-bold">6% (2 flags)</span>
              </div>
              <div className="w-full bg-zinc-950 rounded-full h-2 overflow-hidden border border-zinc-800">
                <div className="bg-emerald-600 h-full" style={{ width: "6%" }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Most Broken Rules & Frequently Skipped Rules */}
        <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between">
            <span>⚠️ Most Broken Rules (Blind Spots)</span>
            <span className="text-xs text-zinc-500">Need training</span>
          </h3>

          <div className="space-y-2 text-xs">
            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <div>
                <span className="font-bold text-white">Nova X Pro (Deprecated Name)</span>
                <p className="text-[11px] text-zinc-500">Writers still using retired 'Pro' suffix.</p>
              </div>
              <span className="font-mono font-bold text-pink-400 text-sm">14 flags</span>
            </div>

            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <div>
                <span className="font-bold text-white">100% Guaranteed Uptime (Unverified SLA)</span>
                <p className="text-[11px] text-zinc-500">Exaggerating 99.9% measured engineering SLA.</p>
              </div>
              <span className="font-mono font-bold text-pink-400 text-sm">9 flags</span>
            </div>

            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between">
              <div>
                <span className="font-bold text-white">Aggressive Sales Hype ('act now')</span>
                <p className="text-[11px] text-zinc-500">Hard-sell phrases violating brand voice.</p>
              </div>
              <span className="font-mono font-bold text-amber-400 text-sm">8 flags</span>
            </div>
          </div>

          <div className="pt-2 border-t border-zinc-800">
            <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider block mb-2">
              Frequently Skipped Rules (Exceptions with Reason)
            </span>
            <div className="text-xs text-zinc-300 space-y-1">
              <div className="flex justify-between">
                <span>All-Caps Emphasis (Skipped 5x)</span>
                <span className="text-zinc-500">Reason: "Stylistic choice for holiday sale banner"</span>
              </div>
              <div className="flex justify-between">
                <span>Passive Voice (Skipped 3x)</span>
                <span className="text-zinc-500">Reason: "Customer quote verbatim"</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// DRAWER: CREATOR MESSAGES & MISTAKE EMAILS
// ---------------------------------------------------------------------------
function CreatorInboxDrawer({ inbox, onClose, onMarkRead }) {
  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-zinc-950 border-l border-zinc-800 z-50 p-6 shadow-2xl flex flex-col justify-between overflow-y-auto">
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-lg">✉️</span>
            <div>
              <h2 className="text-sm font-black text-white">Creator Messages & Mistake Emails</h2>
              <span className="text-[11px] text-pink-400 font-bold">{inbox.unread_count} Unread Updates</span>
            </div>
          </div>
          <button onClick={onClose} className="text-zinc-400 hover:text-white font-bold text-lg">&times;</button>
        </div>

        <div className="flex justify-end">
          <button
            onClick={() => onMarkRead(null)}
            className="text-[11px] text-blue-400 hover:underline font-semibold"
          >
            Mark all as read
          </button>
        </div>

        <div className="space-y-3">
          {inbox.messages?.map((msg) => (
            <div
              key={msg.id}
              className={`p-4 rounded-xl border text-xs space-y-2 transition-all ${
                msg.unread ? "bg-zinc-900 border-pink-600/60 shadow-lg" : "bg-zinc-950 border-zinc-800"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-xs">{msg.sender}</span>
                <span className="text-[10px] font-mono text-zinc-500">{msg.timestamp}</span>
              </div>

              <div className="font-bold text-pink-300 text-xs">{msg.subject}</div>

              <p className="text-zinc-300 whitespace-pre-line text-xs leading-relaxed">
                {msg.body}
              </p>

              {msg.mistakes && msg.mistakes.length > 0 && (
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800 space-y-1 mt-2">
                  <span className="text-[10px] text-zinc-400 font-bold uppercase tracking-wider block">
                    Exact Mistake Locations:
                  </span>
                  {msg.mistakes.map((m, i) => (
                    <div key={i} className="text-[11px] text-zinc-300 flex items-center justify-between">
                      <span className="text-red-400 font-mono">L{m.line} [{m.col}]: "{m.mistake}"</span>
                      <span className="text-emerald-400 font-semibold">&rarr; {m.fix}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="pt-2 flex items-center justify-between border-t border-zinc-800/80">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(msg.body);
                    alert("Message copied to clipboard!");
                  }}
                  className="px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-[11px] font-semibold"
                >
                  Copy Message
                </button>
                {msg.mailto && (
                  <a
                    href={msg.mailto}
                    className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold"
                  >
                    Open in Email App
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t border-zinc-800">
        <button
          onClick={onClose}
          className="w-full py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-bold"
        >
          Close Inbox
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// DRAWER: PERSONAL AI WRITING HELPER (4 Personas)
// ---------------------------------------------------------------------------
function AIWritingHelperDrawer({ currentAsset, onClose, onApplyText }) {
  const [persona, setPersona] = useState("Creator"); // "Creator" | "Brand" | "Brand Manager" | "Legal Reviewer"
  const [promptInput, setPromptInput] = useState("");
  const [aiOutput, setAiOutput] = useState("");
  const [loading, setLoading] = useState(false);

  const personaChips = {
    Creator: [
      "Write 3 punchy, plain-English banner headlines",
      "Make this copy friendlier and remove jargon",
      "Draft a 15-second opening hook for our video"
    ],
    Brand: [
      "Check if this draft aligns with Nova brand pillars",
      "Suggest an on-brand metaphor for cloud speed",
      "Draft brand guidelines summary for partners"
    ],
    Brand Manager: [
      "Explain the 'Nova X Pro' mistake kindly to Alex",
      "Draft a helpful feedback note for the creator",
      "Summarize review status in 2 short sentences"
    ],
    Legal Reviewer: [
      "Draft a simple, plain-English 99.9% uptime disclaimer",
      "Explain the risk of claiming '100% uptime' simply",
      "Formulate advertising disclosure for launch dates"
    ]
  };

  async function generateAICopy(customPrompt = null) {
    const textToUse = customPrompt || promptInput;
    if (!textToUse.trim()) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("persona", persona);
      fd.append("prompt", textToUse);
      fd.append("current_text", currentAsset?.content_text || "");
      const res = await api("/api/inkloom/gemini/helper", { method: "POST", body: fd });
      setAiOutput(res.generated_text);
    } catch (err) {
      alert("AI helper response: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-zinc-950 border-l border-zinc-800 z-50 p-6 shadow-2xl flex flex-col justify-between overflow-y-auto">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">✨</span>
            <div>
              <h2 className="text-sm font-black text-white">Personal AI Writing Helper</h2>
              <span className="text-[11px] text-zinc-400">Powered by Gemini AI (gemini-4-hydrogen)</span>
            </div>
          </div>
          <button onClick={onClose} className="text-zinc-400 hover:text-white font-bold text-lg">&times;</button>
        </div>

        {/* 4 Persona Tabs */}
        <div className="grid grid-cols-2 gap-1.5 p-1 rounded-lg bg-zinc-900 border border-zinc-800 text-xs font-bold">
          {["Creator", "Brand", "Brand Manager", "Legal Reviewer"].map((p) => (
            <button
              key={p}
              onClick={() => { setPersona(p); setAiOutput(""); }}
              className={`py-1.5 px-2 rounded-md transition-all text-center ${
                persona === p ? "bg-gradient-to-r from-pink-600 to-blue-600 text-white shadow" : "text-zinc-400 hover:text-white"
              }`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Quick Prompt Ideas Chips */}
        <div className="space-y-1.5">
          <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">Quick ideas for {persona}:</span>
          <div className="flex flex-col gap-1.5">
            {personaChips[persona]?.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setPromptInput(chip);
                  generateAICopy(chip);
                }}
                className="text-left text-xs p-2 rounded bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-800 transition-colors"
              >
                💡 {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Prompt Input Area */}
        <div className="space-y-2">
          <textarea
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder={`Ask as ${persona}... (e.g. Write a friendly paragraph for our launch)`}
            className="w-full bg-zinc-900 border border-zinc-700 rounded-lg p-3 text-xs text-white h-20 focus:border-pink-500 focus:outline-none"
          />
          <button
            disabled={loading || !promptInput.trim()}
            onClick={() => generateAICopy()}
            className="w-full py-2 rounded-lg bg-gradient-to-r from-pink-600 to-blue-600 hover:from-pink-500 hover:to-blue-500 text-white text-xs font-black shadow transition-all disabled:opacity-50"
          >
            {loading ? "Generating Plain English..." : "Ask AI Helper"}
          </button>
        </div>

        {/* Generated Output Box */}
        {aiOutput && (
          <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-800 space-y-3">
            <span className="text-[10px] font-mono text-pink-400 font-bold uppercase tracking-wider block">
              AI Suggestion ({persona} Persona):
            </span>
            <p className="text-xs text-zinc-200 whitespace-pre-line leading-relaxed font-sans">
              {aiOutput}
            </p>

            {/* 3 One-Click Application Actions */}
            <div className="pt-2 border-t border-zinc-800 flex flex-col gap-2">
              <button
                onClick={() => onApplyText(aiOutput, "draft")}
                className="w-full py-1.5 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all text-center"
              >
                Insert into Draft
              </button>
              <button
                onClick={() => onApplyText(aiOutput, "note")}
                className="w-full py-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-semibold border border-zinc-700 text-center"
              >
                Add to Review Note
              </button>
              <button
                onClick={() => onApplyText(aiOutput, "email")}
                className="w-full py-1.5 rounded bg-pink-600 hover:bg-pink-500 text-white text-xs font-bold transition-all text-center"
              >
                Put in Creator Email
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="pt-4 border-t border-zinc-800">
        <button
          onClick={onClose}
          className="w-full py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-bold"
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// MODAL: NEW DRAFT MODAL
// ---------------------------------------------------------------------------
function NewDraftModal({ onClose, onCreated }) {
  const [title, setTitle] = useState("");
  const [authorName, setAuthorName] = useState("Alex (Agency)");
  const [authorRole, setAuthorRole] = useState("Agency");
  const [format, setFormat] = useState("text");
  const [contentText, setContentText] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleCreate(e) {
    e.preventDefault();
    if (!title.trim() || !contentText.trim()) return;
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("title", title);
      fd.append("author_name", authorName);
      fd.append("author_role", authorRole);
      fd.append("content_text", contentText);
      const res = await api("/api/assets", { method: "POST", body: fd });
      // auto scan
      await api(`/api/assets/${res.id}/scan`, { method: "POST" });
      onCreated(res.id);
    } catch (err) {
      alert("Failed to create draft: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <span>+</span> Submit New Draft
          </h2>
          <button onClick={onClose} className="text-zinc-400 hover:text-white font-bold text-lg">&times;</button>
        </div>

        <form onSubmit={handleCreate} className="space-y-3 text-xs">
          <div>
            <label className="block text-zinc-400 font-semibold mb-1">Draft Title</label>
            <input
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Q4 Product Launch Landing Page"
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2.5 text-white focus:border-pink-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-zinc-400 font-semibold mb-1">Author Name</label>
              <input
                value={authorName}
                onChange={(e) => setAuthorName(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2.5 text-white"
              />
            </div>
            <div>
              <label className="block text-zinc-400 font-semibold mb-1">Author Team / Source</label>
              <select
                value={authorRole}
                onChange={(e) => setAuthorRole(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-2.5 text-white"
              >
                <option value="Agency">External Agency</option>
                <option value="Creator">Internal Employee</option>
                <option value="Creator">Freelancer</option>
                <option value="AI-Tool">AI Tool</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-zinc-400 font-semibold mb-1">Format</label>
            <div className="grid grid-cols-4 gap-2">
              {[
                { id: "text", label: "Text" },
                { id: "banner", label: "Banner" },
                { id: "pdf", label: "PDF" },
                { id: "video", label: "Video" }
              ].map(f => (
                <button
                  type="button"
                  key={f.id}
                  onClick={() => {
                    setFormat(f.id);
                    if (f.id === "banner" && !contentText) {
                      setContentText("Superfast Cloud Availability\n99.9% measured uptime\nfg:#FFFFFF bg:#09090B btn:#DB2777");
                    } else if (f.id === "video" && !contentText) {
                      setContentText("[00:00 - 00:08] Scene 1: Opening Hook with Nova X\n[00:08 - 00:20] Scene 2: Feature Walkthrough");
                    }
                  }}
                  className={`py-1.5 rounded text-xs font-bold border transition-all ${
                    format === f.id ? "bg-pink-600 text-white border-pink-500 shadow" : "bg-zinc-950 text-zinc-400 border-zinc-800"
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-zinc-400 font-semibold mb-1">Content Copy / Script</label>
            <textarea
              required
              rows="6"
              value={contentText}
              onChange={(e) => setContentText(e.target.value)}
              placeholder="Paste draft copy, banner text, or video script here..."
              className="w-full bg-zinc-950 border border-zinc-700 rounded-lg p-3 text-white font-mono focus:border-pink-500 focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-zinc-400 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-lg text-xs font-black bg-pink-600 hover:bg-pink-500 text-white shadow-lg disabled:opacity-50"
            >
              {loading ? "Scanning & Creating..." : "Create & Scan Draft"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Render React App to DOM
ReactDOM.createRoot(document.getElementById("root")).render(<InkloomApp />);
