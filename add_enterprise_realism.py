import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Sound Synthesizer near the top of the babel script
sound_synth_code = '''    // ─── TACTILE AUDIO SYNTHESIZER ─────────────────────────────────────────────
    var soundEnabled = true;
    function playChime(type) {
      if (!soundEnabled) return;
      try {
        var AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        var ctx = new AudioCtx();
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        gain.gain.setValueAtTime(0.04, ctx.currentTime);
        if (type === 'success') {
          osc.frequency.setValueAtTime(523.25, ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(659.25, ctx.currentTime + 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.22);
          osc.start();
          osc.stop(ctx.currentTime + 0.22);
        } else if (type === 'error') {
          osc.frequency.setValueAtTime(329.63, ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(220.00, ctx.currentTime + 0.12);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
          osc.start();
          osc.stop(ctx.currentTime + 0.25);
        } else {
          osc.frequency.setValueAtTime(440, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
          osc.start();
          osc.stop(ctx.currentTime + 0.12);
        }
      } catch(e) {}
    }

    // ─── OFFICIAL COMPLIANCE CERTIFICATE MODAL ─────────────────────────────────
    function ComplianceCertificateModal({ asset, onClose }) {
      var certId = 'CERT-2026-VRT-' + (asset ? (asset.id * 1841 + 4210) : '94182');
      var shaHash = '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08';
      var issuedDate = 'November 19, 2026';

      return (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-[#0C101A] border-2 border-blue-600/40 rounded-2xl w-full max-w-3xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden relative">
            
            {/* Certificate Header Bar */}
            <div className="px-6 py-4 bg-[#131926] border-b border-[#1E293B] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">📜</span>
                <div>
                  <h3 className="text-sm font-extrabold text-white">Pre-Publication Governance Certificate</h3>
                  <p className="text-[10px] text-slate-400 font-mono">Issued by Veritas Brand & Regulatory Compliance Board</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={function() { window.print(); }}
                  className="px-3 py-1 rounded-lg text-xs font-bold bg-[#1E293B] hover:bg-[#28354D] text-slate-200 transition-all flex items-center gap-1.5"
                >
                  <span>🖨️</span>
                  <span>Print Certificate</span>
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="w-8 h-8 rounded-lg bg-[#182030] hover:bg-[#202B40] text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold transition-all border border-[#1E293B]"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Certificate Canvas Body */}
            <div className="p-8 overflow-y-auto space-y-6 text-xs bg-gradient-to-b from-[#0D121F] to-[#080B12]">
              
              {/* Seal & Issuer */}
              <div className="text-center space-y-2 border-b border-[#1E293B] pb-6">
                <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-blue-600 via-indigo-600 to-orange-500 mx-auto flex items-center justify-center shadow-xl border-2 border-white/20">
                  <span className="text-2xl font-black text-white">V</span>
                </div>
                <div className="font-mono text-[10px] tracking-widest text-orange-400 uppercase font-black">
                  VERITAS BRAND GOVERNANCE · PRODUCTION AUDIT CERTIFICATE
                </div>
                <h2 className="text-xl font-black text-white tracking-tight">
                  Official Certificate of Pre-Publication Clearance
                </h2>
                <p className="text-xs text-slate-400 max-w-lg mx-auto">
                  This document certifies that the commercial digital asset referenced below has undergone 6-dimension algorithmic inspection and sequential executive review.
                </p>
              </div>

              {/* Asset Identity Card */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-[#131926] border border-[#1E293B] text-[11px]">
                <div>
                  <span className="text-slate-400 block text-[10px]">Certificate Number</span>
                  <span className="font-mono font-bold text-white text-xs">{certId}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Asset Title</span>
                  <span className="font-bold text-white truncate block">{asset ? asset.title : 'Q3 Campaign Blog Draft'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Format & Version</span>
                  <span className="font-mono text-blue-400 font-bold uppercase">{asset ? asset.file_type : 'Text'} · v2.4 Release</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Date of Certification</span>
                  <span className="font-mono text-slate-300 font-bold">{issuedDate}</span>
                </div>
              </div>

              {/* 6 Dimensions Compliance Checklist */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Automated & Human Review Audit Results
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                  {[
                    { dim: 'Tone & Style Dimension', note: 'Professional, benefit-led voice confirmed', status: 'VERIFIED' },
                    { dim: 'Words & Deprecated Names', note: 'Zero unapproved terms or obsolete brand naming', status: 'VERIFIED' },
                    { dim: 'Claims & Facts Verification', note: '99.9% measured uptime and 14-day trial verified', status: 'VERIFIED' },
                    { dim: 'Privacy Shield & NDA Vault', note: '0 secret codenames or NDA tokens exposed', status: 'VERIFIED' },
                    { dim: 'Visual & Palette Compliance', note: 'Cobalt Blue & Obsidian brand palette verified', status: 'VERIFIED' },
                    { dim: 'Accessibility & WCAG 2.1', note: 'Color contrast ratio > 7.0:1 AAA Pass', status: 'VERIFIED' }
                  ].map(function(item) {
                    return (
                      <div key={item.dim} className="p-2.5 rounded-lg bg-[#131926] border border-[#1E293B] flex items-center justify-between">
                        <div>
                          <div className="font-bold text-white flex items-center gap-1.5">
                            <span className="text-emerald-400">✓</span>
                            <span>{item.dim}</span>
                          </div>
                          <div className="text-[10px] text-slate-400">{item.note}</div>
                        </div>
                        <span className="px-2 py-0.5 rounded text-[9px] font-mono font-black bg-emerald-950/60 border border-emerald-800 text-emerald-400">
                          {item.status}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Cryptographic SHA-256 Proof */}
              <div className="p-3.5 rounded-xl bg-[#090D17] border border-[#1E293B] space-y-1 font-mono text-[10px]">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="flex items-center gap-1.5 text-blue-400 font-bold">
                    <span>🔒</span> Cryptographic Content Signature (SHA-256)
                  </span>
                  <span className="text-emerald-400">Ledger Block #842</span>
                </div>
                <div className="p-2 rounded bg-black/60 text-slate-300 break-all select-all border border-[#1E293B]">
                  {shaHash}
                </div>
                <div className="text-[9px] text-slate-500">
                  Immutable hash recorded in tamper-evident approval ledger. Any byte change invalidates this certificate.
                </div>
              </div>

              {/* Signatures Strip */}
              <div className="grid grid-cols-2 gap-6 pt-4 border-t border-[#1E293B]">
                <div className="p-3 rounded-lg bg-[#131926] border border-[#1E293B] text-center">
                  <div className="h-8 flex items-center justify-center font-serif italic text-base text-blue-300 font-bold">
                    Jordan Miller
                  </div>
                  <div className="border-t border-[#1E293B] pt-1">
                    <div className="font-bold text-white text-[11px]">Jordan Miller</div>
                    <div className="text-[10px] text-slate-400">Step 1 Brand Governance Lead</div>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-[#131926] border border-[#1E293B] text-center">
                  <div className="h-8 flex items-center justify-center font-serif italic text-base text-orange-300 font-bold">
                    Elena Vance, Esq.
                  </div>
                  <div className="border-t border-[#1E293B] pt-1">
                    <div className="font-bold text-white text-[11px]">Elena Vance, Esq.</div>
                    <div className="text-[10px] text-slate-400">Step 2 Legal & Regulatory Counsel</div>
                  </div>
                </div>
              </div>

            </div>

            {/* Certificate Footer */}
            <div className="px-6 py-3 bg-[#131926] border-t border-[#1E293B] flex items-center justify-between text-[11px] text-slate-400">
              <span className="font-mono">Security Hash: {certId} · Status: CLEAR FOR PRODUCTION</span>
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-1.5 rounded-lg bg-[#1F293D] hover:bg-[#2B3854] text-white font-bold transition-all text-xs"
              >
                Close Certificate
              </button>
            </div>

          </div>
        </div>
      );
    }

    // ─── COMMAND PALETTE MODAL (⌘K / Ctrl+K) ───────────────────────────────────
    function CommandPaletteModal({
      isOpen,
      onClose,
      assets,
      onSelectAsset,
      onNavigateTab,
      onTriggerScan,
      onExportCert,
      onSwitchRole,
      currentUser
    }) {
      if (!isOpen) return null;
      var [search, setSearch] = useState('');

      var commands = [
        { id: 'scan', icon: '🔍', title: 'Run 6-Dimension Pre-Publication Scan', cat: 'Actions', action: function() { onTriggerScan(); onClose(); } },
        { id: 'cert', icon: '📜', title: 'Export Official Compliance Certificate', cat: 'Actions', action: function() { onExportCert(); onClose(); } },
        { id: 'studio', icon: '🎨', title: 'Go to Review Studio', cat: 'Navigation', action: function() { onNavigateTab('studio'); onClose(); } },
        { id: 'kb', icon: '📚', title: 'Go to Knowledge Base & Brand Guide', cat: 'Navigation', action: function() { onNavigateTab('kb'); onClose(); } },
        { id: 'trail', icon: '🔒', title: 'Go to Approval Trail & Ledger', cat: 'Navigation', action: function() { onNavigateTab('trail'); onClose(); } },
        { id: 'insights', icon: '📊', title: 'Go to Team Insights & Telemetry', cat: 'Navigation', action: function() { onNavigateTab('insights'); onClose(); } }
      ];

      (assets || []).forEach(function(a) {
        commands.push({
          id: 'asset-' + a.id,
          icon: a.file_type === 'banner' ? '🖼️' : a.file_type === 'pdf' ? '📄' : a.file_type === 'video' ? '🎬' : '📝',
          title: 'Jump to: ' + a.title + ' (' + (a.state || 'Draft') + ')',
          cat: 'Drafts',
          action: function() { onSelectAsset(a.id); onNavigateTab('studio'); onClose(); }
        });
      });

      if (currentUser && currentUser.role === 'Admin') {
        commands.push(
          { id: 'role-admin', icon: '👑', title: 'Switch Role to Admin', cat: 'Role Switcher', action: function() { onSwitchRole('Admin'); onClose(); } },
          { id: 'role-creator', icon: '✍️', title: 'Switch Role to Creator', cat: 'Role Switcher', action: function() { onSwitchRole('Creator'); onClose(); } },
          { id: 'role-bm', icon: '🛡️', title: 'Switch Role to Brand Manager', cat: 'Role Switcher', action: function() { onSwitchRole('Brand Manager'); onClose(); } },
          { id: 'role-legal', icon: '⚖️', title: 'Switch Role to Company Review', cat: 'Role Switcher', action: function() { onSwitchRole('Legal Reviewer'); onClose(); } }
        );
      }

      var filtered = commands.filter(function(c) {
        var q = search.toLowerCase();
        return c.title.toLowerCase().indexOf(q) !== -1 || c.cat.toLowerCase().indexOf(q) !== -1;
      });

      return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-start justify-center pt-24 p-4" onClick={onClose}>
          <div className="bg-[#0F141F] border border-[#1E293B] rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden" onClick={function(e) { e.stopPropagation(); }}>
            <div className="p-3 border-b border-[#1E293B] flex items-center gap-3 bg-[#131926]">
              <span className="text-slate-400 text-sm">🔍</span>
              <input
                autoFocus
                type="text"
                value={search}
                onChange={function(e) { setSearch(e.target.value); }}
                placeholder="Type a command or search drafts... (Esc to close)"
                className="w-full bg-transparent text-sm text-white focus:outline-none placeholder-slate-500"
              />
              <kbd className="px-1.5 py-0.5 rounded bg-[#1C2436] text-[10px] text-slate-400 font-mono border border-[#28354D]">ESC</kbd>
            </div>
            <div className="max-h-80 overflow-y-auto p-2 space-y-1">
              {filtered.map(function(item) {
                return (
                  <button
                    key={item.id}
                    onClick={item.action}
                    className="w-full p-2.5 rounded-lg text-left flex items-center justify-between text-xs hover:bg-[#1A2336] transition-all group"
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="text-base">{item.icon}</span>
                      <span className="text-white group-hover:text-blue-400 transition-colors font-medium">{item.title}</span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 uppercase">{item.cat}</span>
                  </button>
                );
              })}
              {filtered.length === 0 && (
                <div className="p-6 text-center text-xs text-slate-500">
                  No commands or drafts matching "{search}".
                </div>
              )}
            </div>
            <div className="px-4 py-2 border-t border-[#1E293B] bg-[#0A0D15] flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>Navigate with arrows · Press Enter to execute</span>
              <span>Command Palette · Inkloom v2.4</span>
            </div>
          </div>
        </div>
      );
    }

    // ─── TEAM REVIEW DISCUSSION & ACTIVITY PANEL ──────────────────────────────
    function TeamDiscussionPanel({ assetId, currentUser, onNewActivity }) {
      var [tab, setTab] = useState('comments');
      var [commentText, setCommentText] = useState('');
      var [commentType, setCommentType] = useState('Feedback Note');

      var initialComments = [
        {
          id: 1,
          author: 'Alex Rivera',
          role: 'Senior Copywriter',
          avatar: 'A',
          time: '2 hours ago',
          type: 'Revision Note',
          typeColor: 'text-blue-400 bg-blue-950/60 border-blue-800',
          text: 'Adjusted paragraph 1 to focus on benefit-led outcomes for our cloud launch. Please verify that the 99.9% uptime SLA wording matches engineering latest sign-off.',
          reactions: ['👍 2', '👀 1']
        },
        {
          id: 2,
          author: 'Jordan Miller',
          role: 'Brand Manager',
          avatar: 'J',
          time: '1 hour ago',
          type: 'Brand Review',
          typeColor: 'text-orange-400 bg-orange-950/60 border-orange-800',
          text: 'Copy is much clearer Alex! Found a remnant of "Nova X Pro" in paragraph 2 line 15 (remember Pro is deprecated). Also let us keep button contrast aligned to Cobalt Blue #2563EB to hit WCAG AAA. Once edited, I will approve Step 1.',
          reactions: ['✓ Acknowledged']
        },
        {
          id: 3,
          author: 'Elena Vance, Esq.',
          role: 'Legal & Regulatory Counsel',
          avatar: 'E',
          time: '24 mins ago',
          type: 'Legal Objection',
          typeColor: 'text-red-400 bg-red-950/60 border-red-800',
          text: 'Preliminary review: Uptime SLA 99.9% is compliant with our standard master services agreement clause 4b. However, please redact the "Project Apollo" benchmark reference in paragraph 3 prior to final approval.',
          reactions: ['🔒 NDA Enforced']
        }
      ];

      var [comments, setComments] = useState(initialComments);

      var auditLogs = [
        { time: '09:14 AM', actor: 'Alex Rivera', action: 'Draft submitted for Step 1 Review', hash: 'sha256:7f4a...e1' },
        { time: '09:15 AM', actor: '6-Dimension Engine', action: 'Scan complete: 3 Must Fix, 1 Check This', hash: 'sha256:881b...9c' },
        { time: '09:42 AM', actor: 'Privacy Shield', action: '14 sensitive tokens masked for AI inspection', hash: 'sha256:4a02...55' },
        { time: '10:15 AM', actor: 'Jordan Miller', action: 'Ran 3-Level Automation suite; report exported', hash: 'sha256:9f86...08' }
      ];

      function handlePostComment(e) {
        if (e && e.preventDefault) e.preventDefault();
        if (!commentText.trim()) return;
        var newC = {
          id: Date.now(),
          author: currentUser ? currentUser.name : 'Reviewer',
          role: currentUser ? currentUser.role : 'Team Member',
          avatar: (currentUser ? currentUser.name : 'U').charAt(0),
          time: 'Just now',
          type: commentType,
          typeColor: commentType === 'Legal Objection' ? 'text-red-400 bg-red-950/60 border-red-800' :
                     commentType === 'Approved / LGTM' ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800' :
                     'text-blue-400 bg-blue-950/60 border-blue-800',
          text: commentText.trim(),
          reactions: ['👍 1']
        };
        setComments(function(prev) { return [newC, ...prev]; });
        setCommentText('');
        playChime('chime');
        if (onNewActivity) onNewActivity('Added review comment: ' + newC.type);
      }

      return (
        <div className="p-4 rounded-xl bg-[#0F141F] border border-[#1E293B] space-y-4">
          
          {/* Header & Tabs */}
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={function() { setTab('comments'); }}
                className={'px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ' + (tab === 'comments' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white')}
              >
                <span>💬</span>
                <span>Team Discussion ({comments.length})</span>
              </button>
              <button
                type="button"
                onClick={function() { setTab('audit'); }}
                className={'px-3 py-1 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ' + (tab === 'audit' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white')}
              >
                <span>📋</span>
                <span>Audit Stream ({auditLogs.length})</span>
              </button>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Live Sync
            </span>
          </div>

          {tab === 'comments' && (
            <div className="space-y-3">
              {/* Add Comment Form */}
              <form onSubmit={handlePostComment} className="p-3 rounded-lg bg-[#131926] border border-[#1E293B] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-300">Add Team Review Feedback:</span>
                  <select
                    value={commentType}
                    onChange={function(e) { setCommentType(e.target.value); }}
                    className="bg-[#0F141F] border border-[#1E293B] rounded px-2 py-0.5 text-[10px] text-white focus:outline-none"
                  >
                    <option value="Feedback Note">📝 Feedback Note</option>
                    <option value="Revision Required">⚠️ Revision Required</option>
                    <option value="Legal Objection">⚖️ Legal Objection</option>
                    <option value="Approved / LGTM">✓ Approved / LGTM</option>
                  </select>
                </div>
                <textarea
                  rows={2}
                  value={commentText}
                  onChange={function(e) { setCommentText(e.target.value); }}
                  placeholder="Type feedback, cite specific clauses, or tag @colleague..."
                  className="w-full bg-[#0F141F] border border-[#1E293B] rounded p-2 text-xs text-white focus:border-blue-500 focus:outline-none"
                />
                <div className="flex justify-between items-center pt-1">
                  <span className="text-[10px] text-slate-500 font-mono">Press Post to notify assigned reviewers</span>
                  <button
                    type="submit"
                    className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all"
                  >
                    Post Comment
                  </button>
                </div>
              </form>

              {/* Comments Feed */}
              <div className="space-y-2.5 max-h-80 overflow-y-auto pr-1">
                {comments.map(function(c) {
                  return (
                    <div key={c.id} className="p-3 rounded-lg bg-[#131926] border border-[#1E293B] space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-blue-600 to-orange-500 flex items-center justify-center font-bold text-white text-[10px]">
                            {c.avatar}
                          </div>
                          <span className="font-bold text-white text-[11px]">{c.author}</span>
                          <span className="text-[10px] text-slate-500 font-mono">({c.role})</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span className={'px-1.5 py-0.5 rounded text-[9px] font-mono font-bold border ' + c.typeColor}>
                            {c.type}
                          </span>
                          <span className="text-[10px] text-slate-500">{c.time}</span>
                        </div>
                      </div>
                      <p className="text-slate-300 text-[11px] leading-relaxed">
                        {c.text}
                      </p>
                      <div className="flex items-center gap-2 pt-1">
                        {c.reactions.map(function(r, idx) {
                          return (
                            <span key={idx} className="px-1.5 py-0.5 rounded bg-[#182030] text-[10px] text-slate-400 font-mono border border-[#25324D]">
                              {r}
                            </span>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {tab === 'audit' && (
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1 text-xs font-mono">
              {auditLogs.map(function(a, idx) {
                return (
                  <div key={idx} className="p-2.5 rounded-lg bg-[#131926] border border-[#1E293B] flex items-center justify-between">
                    <div>
                      <div className="text-slate-300 font-sans text-xs">
                        <strong className="text-blue-400">{a.actor}</strong>: {a.action}
                      </div>
                      <div className="text-[10px] text-slate-500">{a.hash}</div>
                    </div>
                    <span className="text-[10px] text-slate-500">{a.time}</span>
                  </div>
                );
              })}
            </div>
          )}

        </div>
      );
    }
'''

# 2. Upgraded MultiModalCanvas
upgraded_canvas_code = '''    // ─── ENHANCED PRODUCTION MULTI-MODAL CANVAS ──────────────────────────────
    function MultiModalCanvas({ asset, format, isCreator, onContentUpdate }) {
      var [content, setContent] = useState(asset ? (asset.content_text || '') : '');
      
      // Banner State
      var [bannerHeadline, setBannerHeadline] = useState('Superfast Cloud Availability');
      var [bannerCTA, setBannerCTA] = useState('Start 14-Day Free Trial');
      var [bannerBtnColor, setBannerBtnColor] = useState('#2563EB');
      var [bannerAspect, setBannerAspect] = useState('1200x628');
      var [showSafeMargins, setShowSafeMargins] = useState(true);
      var [logoPosition, setLogoPosition] = useState('top-left');

      // PDF Reader State
      var [pdfPage, setPdfPage] = useState(1);
      var [pdfZoom, setPdfZoom] = useState(100);

      // Video & Audio State
      var [videoTime, setVideoTime] = useState(0);
      var [videoPlaying, setVideoPlaying] = useState(false);
      var [captionsOn, setCaptionsOn] = useState(true);
      var [playbackSpeed, setPlaybackSpeed] = useState(1.0);

      // Approved brand color presets
      var brandColorPresets = [
        { name: 'Cobalt Blue (#2563EB) — Primary Brand Action', hex: '#2563EB', contrast: '8.4:1 · AAA PASS' },
        { name: 'Signal Orange (#F97316) — Dynamic Accent / Highlight', hex: '#F97316', contrast: '7.1:1 · AAA PASS' },
        { name: 'Obsidian Black (#080B12) — Primary Canvas Background', hex: '#080B12', contrast: '19.2:1 · AAA PASS' },
        { name: 'Surface Slate (#0F141F) — Secondary Surface Card', hex: '#0F141F', contrast: '16.5:1 · AAA PASS' },
        { name: 'Emerald Green (#10B981) — Verified Badge / Success', hex: '#10B981', contrast: '6.8:1 · AAA PASS' },
        { name: 'Signal Amber (#F59E0B) — Warning / Review Callout', hex: '#F59E0B', contrast: '6.2:1 · AA PASS' },
        { name: 'Pure White (#FFFFFF) — High Contrast Typography', hex: '#FFFFFF', contrast: '21:1 · AAA PASS' }
      ];

      var activePreset = brandColorPresets.find(function(p) { return p.hex.toLowerCase() === bannerBtnColor.toLowerCase(); });

      useEffect(function() {
        if (asset) setContent(asset.content_text || '');
      }, [asset]);

      useEffect(function() {
        var iv;
        if (videoPlaying) {
          iv = setInterval(function() {
            setVideoTime(function(t) { return t >= 30 ? 0 : t + 1; });
          }, 500 / playbackSpeed);
        }
        return function() { clearInterval(iv); };
      }, [videoPlaying, playbackSpeed]);

      function fmtTime(s) {
        var m = String(Math.floor(s / 60)).padStart(2, '0');
        var sec = String(s % 60).padStart(2, '0');
        return m + ':' + sec;
      }

      var scene = videoTime < 8 ? 'Scene 1: Opening Hook & Animated Logo Reveal' :
                  videoTime < 19 ? 'Scene 2: Core Platform Architecture & Benchmark' :
                  'Scene 3: Closing Call to Action & VIP Waitlist';
      var caption = videoTime < 8 ? 'Introducing Nova X, the cloud platform built for modern teams.' :
                    videoTime < 19 ? 'Engineered for 99.9% measured availability across global nodes.' :
                    'Join the waitlist launching in March 2026.';

      // Text analytics
      var words = (content || '').trim().split(/\s+/).filter(Boolean).length;
      var chars = (content || '').length;
      var readTimeMinutes = Math.max(1, Math.ceil(words / 200));

      return (
        <div className="p-5 rounded-xl bg-[#0F141F] border border-[#1E293B] space-y-4">
          
          {/* Canvas Top Bar */}
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm text-white">
                {format === 'text' ? '📝 Production Copy & Script Canvas' :
                 format === 'banner' ? '🖼️ Visual Ad Banner & WCAG Engine' :
                 format === 'pdf' ? '📄 Multi-Page Document Whitepaper Reader' :
                 format === 'audio' ? '🎙️ Spoken Audio & Speech Waveform Suite' :
                 '🎬 Video Timeline & Scene Cue Sheet'}
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#151B28] text-blue-400 border border-[#1E293B]">
                {format.toUpperCase()} · LIVE RENDER
              </span>
            </div>
            <span className="text-[11px] font-mono text-slate-400">
              {format === 'text' ? words + ' words · ' + readTimeMinutes + ' min read' :
               format === 'banner' ? bannerAspect + ' px' :
               format === 'pdf' ? 'Page ' + pdfPage + ' of 4 · ' + pdfZoom + '%' :
               'Timeline: 00:30 · 1080p 60fps'}
            </span>
          </div>

          {/* TEXT CANVAS */}
          {format === 'text' && (
            <div className="space-y-3">
              {/* Analytics strip */}
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2 rounded bg-[#131926] border border-[#1E293B]">
                  <span className="text-[10px] text-slate-400 block font-mono">Word Count</span>
                  <span className="font-black text-white text-sm">{words}</span>
                </div>
                <div className="p-2 rounded bg-[#131926] border border-[#1E293B]">
                  <span className="text-[10px] text-slate-400 block font-mono">Reading Time</span>
                  <span className="font-black text-blue-400 text-sm">~{readTimeMinutes} min</span>
                </div>
                <div className="p-2 rounded bg-[#131926] border border-[#1E293B]">
                  <span className="text-[10px] text-slate-400 block font-mono">Grade Level</span>
                  <span className="font-black text-emerald-400 text-sm">Grade 8.2</span>
                </div>
                <div className="p-2 rounded bg-[#131926] border border-[#1E293B]">
                  <span className="text-[10px] text-slate-400 block font-mono">Plain English</span>
                  <span className="font-black text-emerald-400 text-sm">✓ Compliant</span>
                </div>
              </div>

              {/* Notice banner */}
              <div className="p-3 rounded-lg bg-orange-950/30 border-l-2 border-orange-500 text-xs text-orange-300 flex items-center justify-between">
                <span>⚠️ Line 2, Col 15: "Nova X Pro" (deprecated nomenclature) — Approved: "Nova X"</span>
                <span className="font-mono text-[10px] text-slate-400">Rule REF-104</span>
              </div>

              {/* Editor with Line Numbers */}
              <div className="flex border border-[#1E293B] rounded-lg bg-[#131926] overflow-hidden focus-within:border-blue-500">
                <div className="w-10 py-3 bg-[#0E131E] border-r border-[#1E293B] text-[11px] font-mono text-slate-600 select-none text-right pr-2 space-y-1">
                  {[1,2,3,4,5,6,7,8,9,10,11,12].map(function(num) {
                    return <div key={num}>{num}</div>;
                  })}
                </div>
                <textarea
                  value={content}
                  onChange={function(e) {
                    setContent(e.target.value);
                    if (onContentUpdate) onContentUpdate(e.target.value);
                  }}
                  readOnly={!isCreator}
                  rows={12}
                  className="w-full bg-transparent p-3 text-xs font-mono text-slate-200 resize-y focus:outline-none leading-relaxed"
                  placeholder="Paste or write commercial copy, blog text, or advertising draft..."
                />
              </div>
            </div>
          )}

          {/* BANNER CANVAS */}
          {format === 'banner' && (
            <div className="space-y-4">
              
              {/* Controls bar: Aspect Ratio & Safe Margins */}
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs bg-[#131926] p-2.5 rounded-lg border border-[#1E293B]">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 font-bold">Preset:</span>
                  <select
                    value={bannerAspect}
                    onChange={function(e) { setBannerAspect(e.target.value); }}
                    className="bg-[#0F141F] border border-[#1E293B] rounded px-2 py-1 text-white font-mono text-xs focus:border-blue-500 focus:outline-none"
                  >
                    <option value="1200x628">1200x628 · LinkedIn / Twitter Card</option>
                    <option value="1080x1080">1080x1080 · Instagram / FB Square</option>
                    <option value="300x250">300x250 · Google Display Ad</option>
                    <option value="1920x1080">1920x1080 · Homepage Hero Billboard</option>
                  </select>
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
                    <input
                      type="checkbox"
                      checked={showSafeMargins}
                      onChange={function(e) { setShowSafeMargins(e.target.checked); }}
                      className="w-3.5 h-3.5 rounded accent-blue-600"
                    />
                    <span>Safe Margins Grid</span>
                  </label>

                  <div className="flex items-center gap-1.5">
                    <span className="text-slate-400">Logo:</span>
                    <select
                      value={logoPosition}
                      onChange={function(e) { setLogoPosition(e.target.value); }}
                      className="bg-[#0F141F] border border-[#1E293B] rounded px-2 py-0.5 text-white text-xs"
                    >
                      <option value="top-left">Top-Left</option>
                      <option value="top-right">Top-Right</option>
                      <option value="bottom-left">Bottom-Left</option>
                      <option value="bottom-right">Bottom-Right</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Live Banner Preview Box */}
              <div className={'rounded-xl overflow-hidden border border-[#1E293B] flex flex-col justify-between relative bg-[#080B12] p-8 shadow-2xl transition-all ' + (
                bannerAspect === '1080x1080' ? 'aspect-square max-w-sm mx-auto' :
                bannerAspect === '300x250' ? 'aspect-[300/250] max-w-xs mx-auto' :
                'aspect-[1200/628] w-full'
              )}>
                {/* Background gradient & safe margins */}
                <div className="absolute inset-0 opacity-20" style={{backgroundImage: 'radial-gradient(circle at 25% 40%, #2563EB 0%, transparent 55%), radial-gradient(circle at 75% 60%, #F97316 0%, transparent 55%)'}}></div>
                {showSafeMargins && (
                  <div className="absolute inset-4 border border-dashed border-blue-500/30 rounded pointer-events-none flex items-start justify-end p-1">
                    <span className="text-[9px] font-mono text-blue-400 bg-blue-950/80 px-1 rounded">SAFE ZONE</span>
                  </div>
                )}

                {/* Brand Logo placement */}
                <div className={'relative z-10 flex ' + (logoPosition.indexOf('right') !== -1 ? 'justify-end' : 'justify-start')}>
                  <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-[#0F141F]/80 border border-[#1E293B]">
                    <div className="w-5 h-5 rounded bg-blue-600 flex items-center justify-center font-black text-white text-[11px]">N</div>
                    <span className="font-extrabold text-xs text-white tracking-wider">NOVA <span className="text-orange-400">X</span></span>
                  </div>
                </div>

                {/* Banner Content */}
                <div className="relative z-10 text-center my-auto space-y-3 px-4">
                  <div className="text-2xl sm:text-3xl font-black text-white leading-tight tracking-tight drop-shadow-md">
                    {bannerHeadline}
                  </div>
                  <div className="text-xs sm:text-sm text-slate-300 max-w-md mx-auto">
                    Experience measured 99.9% uptime with instant automated failover across 12 zones.
                  </div>
                  <div>
                    <button
                      className="px-6 py-2.5 rounded-lg font-black text-xs sm:text-sm text-white shadow-xl transition-transform hover:scale-105 active:scale-95"
                      style={{background: bannerBtnColor}}
                    >
                      {bannerCTA}
                    </button>
                  </div>
                </div>

                {/* Footer badge */}
                <div className="relative z-10 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>ISO 27001 Certified</span>
                  <span>14-Day Free Evaluation</span>
                </div>
              </div>

              {/* Editing Controls */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Headline Text</label>
                  <input
                    value={bannerHeadline}
                    onChange={function(e) { setBannerHeadline(e.target.value); }}
                    className="w-full bg-[#131926] border border-[#1E293B] rounded-lg p-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">CTA Button Text</label>
                  <input
                    value={bannerCTA}
                    onChange={function(e) { setBannerCTA(e.target.value); }}
                    className="w-full bg-[#131926] border border-[#1E293B] rounded-lg p-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>

                {/* Approved Brand Color Preset Dropdown */}
                <div className="sm:col-span-2 p-3 rounded-lg bg-[#131926] border border-[#1E293B] space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-slate-300 font-bold text-xs flex items-center gap-1.5">
                      <span>🎨</span> Pick Approved Brand Color Preset:
                    </label>
                    <span className="px-2 py-0.5 rounded bg-[#072418] text-emerald-300 border border-emerald-700 font-mono font-bold text-[10px]">
                      {activePreset ? activePreset.contrast : '8.4:1 · AAA PASS'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={bannerBtnColor}
                      onChange={function(e) { setBannerBtnColor(e.target.value); }}
                      className="flex-1 bg-[#0F141F] border border-[#1E293B] rounded-lg p-2 text-white font-mono text-xs focus:border-blue-500 focus:outline-none"
                    >
                      {brandColorPresets.map(function(cp) {
                        return (
                          <option key={cp.hex} value={cp.hex}>
                            {cp.name}
                          </option>
                        );
                      })}
                    </select>
                    <input
                      type="color"
                      value={bannerBtnColor}
                      onChange={function(e) { setBannerBtnColor(e.target.value); }}
                      className="w-9 h-9 rounded-lg border border-[#1E293B] cursor-pointer bg-transparent p-0.5"
                      title="Custom Brand Hex"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* PDF WHITE PAPER VIEWER */}
          {format === 'pdf' && (
            <div className="space-y-4">
              
              {/* PDF Toolbar */}
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs bg-[#131926] p-2.5 rounded-lg border border-[#1E293B]">
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 font-bold">Document:</span>
                  <span className="text-white font-semibold">Nova_X_Security_Whitepaper_v2.4.pdf</span>
                  <span className="text-[10px] font-mono text-slate-500">(14.2 MB · Signed)</span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={function() { setPdfZoom(function(z) { return Math.max(75, z - 25); }); }}
                    className="w-7 h-7 rounded bg-[#0F141F] hover:bg-[#1C2538] border border-[#1E293B] text-slate-300 text-xs font-bold"
                  >
                    -
                  </button>
                  <span className="font-mono text-xs text-slate-300 w-12 text-center">{pdfZoom}%</span>
                  <button
                    type="button"
                    onClick={function() { setPdfZoom(function(z) { return Math.min(150, z + 25); }); }}
                    className="w-7 h-7 rounded bg-[#0F141F] hover:bg-[#1C2538] border border-[#1E293B] text-slate-300 text-xs font-bold"
                  >
                    +
                  </button>
                </div>
              </div>

              {/* PDF Grid: Thumbnails sidebar + Main Reader */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                
                {/* Thumbnails Sidebar */}
                <div className="md:col-span-3 space-y-2">
                  {[
                    { page: 1, title: 'Cover & Abstract', flag: null },
                    { page: 2, title: 'Architecture SLAs', flag: 'NDA Reference' },
                    { page: 3, title: 'ISO 27001 Standards', flag: null },
                    { page: 4, title: 'Appendix & Ledger', flag: null }
                  ].map(function(p) {
                    return (
                      <button
                        key={p.page}
                        type="button"
                        onClick={function() { setPdfPage(p.page); }}
                        className={'w-full p-2 rounded-lg text-left border transition-all text-xs flex items-center justify-between ' + (
                          pdfPage === p.page ? 'bg-[#1A2336] border-blue-500 text-white' : 'bg-[#131926] border-[#1E293B] text-slate-400 hover:text-white'
                        )}
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-[10px]">p.{p.page}</span>
                          <span className="truncate">{p.title}</span>
                        </div>
                        {p.flag && (
                          <span className="px-1 py-0.5 rounded bg-red-950 text-red-300 text-[8px] font-bold border border-red-800">
                            FLAG
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Main Rendered PDF Page */}
                <div className="md:col-span-9 bg-[#0B0F19] p-8 rounded-xl border border-[#1E293B] font-serif text-slate-200 space-y-4 shadow-xl">
                  
                  {/* Page Header */}
                  <div className="flex items-center justify-between border-b border-[#1E293B] pb-2 font-sans text-[10px] text-slate-500 font-mono uppercase">
                    <span>VERITAS BRAND ENTERPRISE WHITEPAPER SERIES</span>
                    <span>CONFIDENTIAL · PAGE {pdfPage} OF 4</span>
                  </div>

                  {pdfPage === 1 && (
                    <div className="space-y-4 py-4">
                      <div className="font-sans font-bold text-xs uppercase tracking-widest text-orange-400">Technical Briefing</div>
                      <h1 className="text-2xl font-black font-sans text-white leading-tight">
                        Continuous Compliance & Multi-Region Cloud Governance
                      </h1>
                      <p className="text-sm leading-relaxed text-slate-300">
                        This whitepaper defines the technical and brand compliance foundation engineered for Nova X enterprise deployments. Designed from first principles to ensure complete regulatory alignment across SOC-2 Type II, ISO 27001, and global GDPR mandates.
                      </p>
                    </div>
                  )}

                  {pdfPage === 2 && (
                    <div className="space-y-4 py-2">
                      <h2 className="text-lg font-bold font-sans text-white">Section 3: Low-Latency Fabric & Measured SLAs</h2>
                      <p className="text-xs leading-relaxed text-slate-300">
                        Our multi-zone routing engine isolates customer tenant workloads across redundant physical data centers. Under standard enterprise agreements, we guarantee a measured <strong>99.9% uptime SLA</strong> backed by automated financial credits.
                      </p>

                      {/* Flagged Callout in PDF */}
                      <div className="p-3 rounded-lg bg-orange-950/30 border border-orange-700/80 font-sans text-xs space-y-1">
                        <div className="flex items-center justify-between text-orange-300 font-bold">
                          <span>⚠️ POLICY VIOLATION DETECTED · LINE 42</span>
                          <span className="font-mono text-[9px] bg-orange-950 px-1.5 py-0.5 rounded border border-orange-800">MUST FIX</span>
                        </div>
                        <p className="text-slate-300 italic">
                          "Preliminary internal benchmarks developed under <mark className="bg-orange-500/30 text-orange-200 border-b border-orange-400 px-1 rounded font-bold">Project Apollo</mark> indicate ultra-low 2ms latency across edge regions."
                        </p>
                        <p className="text-[11px] text-slate-400">
                          Rationale: <strong>Project Apollo</strong> is an active NDA codename. Must be replaced with generic term: "our advanced engineering benchmarks".
                        </p>
                      </div>

                      <p className="text-xs leading-relaxed text-slate-300">
                        Zero packet inspection or customer telemetry is retained unencrypted in transit. All audit logs are sealed via SHA-256 ledger.
                      </p>
                    </div>
                  )}

                  {pdfPage === 3 && (
                    <div className="space-y-4 py-2">
                      <h2 className="text-lg font-bold font-sans text-white">Section 4: ISO 27001 & Regulatory Framework</h2>
                      <p className="text-xs leading-relaxed text-slate-300">
                        Nova X operates under audited ISO 27001 certification. All cryptographic keys are rotated every 90 days with hardware security module (HSM) attestation.
                      </p>
                      <p className="text-xs leading-relaxed text-slate-300">
                        Notice: SOC2 compliance is currently in audit review; marketing communications must omit SOC2 claims until certification completion in Q4 2026.
                      </p>
                    </div>
                  )}

                  {pdfPage === 4 && (
                    <div className="space-y-4 py-2">
                      <h2 className="text-lg font-bold font-sans text-white">Appendix: Verification Proof</h2>
                      <p className="text-xs leading-relaxed text-slate-300">
                        This whitepaper draft carries SHA-256 root hash <code className="text-blue-400 font-mono text-[10px]">7f4a...881c</code> registered in the Veritas tamper-evident approval ledger.
                      </p>
                    </div>
                  )}

                  {/* Page Footer */}
                  <div className="border-t border-[#1E293B] pt-2 flex items-center justify-between font-sans text-[10px] text-slate-500 font-mono">
                    <span>STATUS: DRAFT · IN REVIEW</span>
                    <span>VERITAS BRAND TECHNOLOGIES, INC.</span>
                  </div>

                </div>

              </div>
            </div>
          )}

          {/* VIDEO & AUDIO CANVAS */}
          {(format === 'video' || format === 'audio') && (
            <div className="space-y-4">
              
              {/* Media Viewport */}
              <div className="relative aspect-video rounded-xl bg-black border border-[#1E293B] flex flex-col justify-between p-4 overflow-hidden shadow-2xl">
                
                {/* Top Status Indicators */}
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-1 rounded bg-[#0F141F]/90 text-[11px] font-mono font-bold text-orange-400 border border-orange-900 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    {format === 'audio' ? 'AUDIO STUDIO · ' : 'TIMELINE · '} {fmtTime(videoTime)} / 00:30
                  </span>
                  
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-[#0F141F]/90 text-[10px] text-slate-400 font-mono border border-[#1E293B]">
                      {format === 'audio' ? 'Stereo 48kHz WAV · 24-bit' : '1080p 60fps · ProRes 422'}
                    </span>
                    <button
                      type="button"
                      onClick={function() { setPlaybackSpeed(function(s) { return s === 1.0 ? 1.5 : s === 1.5 ? 2.0 : 1.0; }); }}
                      className="px-2 py-0.5 rounded bg-[#131926] text-[10px] font-mono font-bold text-blue-400 border border-blue-900"
                    >
                      {playbackSpeed}x
                    </button>
                  </div>
                </div>

                {/* Center Audio Waveform Visualizer & Scene Title */}
                <div className="text-center my-auto space-y-3">
                  <div className="flex items-center justify-center gap-1 h-12">
                    {[30, 60, 45, 90, 75, 40, 85, 95, 60, 40, 70, 100, 80, 50, 65, 85, 40, 90, 75, 55, 70, 95, 80, 45, 60, 85, 50, 40, 75, 90, 60, 35].map(function(h, idx) {
                      var barHeight = videoPlaying ? Math.max(15, (h * ((videoTime % 4) + 1)) % 100) : h * 0.4;
                      return (
                        <div
                          key={idx}
                          className="w-1.5 bg-gradient-to-t from-blue-600 to-orange-400 rounded-full transition-all duration-300"
                          style={{height: barHeight + '%'}}
                        />
                      );
                    })}
                  </div>

                  <p className="text-sm sm:text-base font-extrabold text-white drop-shadow">
                    {scene}
                  </p>

                  {captionsOn && (
                    <div className="inline-block mt-2 px-3 py-1.5 rounded-lg bg-black/85 border border-[#1E293B] text-xs text-yellow-300 font-mono shadow-lg">
                      [CC · English] {caption}
                    </div>
                  )}
                </div>

                {/* Bottom Timeline Controls */}
                <div className="space-y-2">
                  <input
                    type="range"
                    min={0}
                    max={30}
                    value={videoTime}
                    onChange={function(e) { setVideoTime(Number(e.target.value)); }}
                    className="w-full accent-blue-600 cursor-pointer"
                  />
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={function() { setVideoPlaying(!videoPlaying); playChime('chime'); }}
                        className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all"
                      >
                        {videoPlaying ? '⏸ Pause' : '▶ Play'}
                      </button>
                      <button
                        type="button"
                        onClick={function() { setCaptionsOn(!captionsOn); }}
                        className={'px-3 py-1 rounded-lg text-xs font-bold border transition-all ' + (
                          captionsOn ? 'bg-orange-950 border-orange-700 text-orange-300' : 'bg-[#151B28] border-[#1E293B] text-slate-400'
                        )}
                      >
                        [CC] Captions
                      </button>
                      <button
                        type="button"
                        onClick={function() { setVideoTime(0); setVideoPlaying(false); }}
                        className="px-2.5 py-1 rounded-lg bg-[#151B28] hover:bg-[#1E293B] text-slate-300 text-xs border border-[#1E293B]"
                      >
                        ↺ Reset
                      </button>
                    </div>

                    <div className="text-[11px] font-mono text-slate-400">
                      Cue Sync: Active
                    </div>
                  </div>
                </div>

              </div>

              {/* Synchronized Scene Cue Cards */}
              <div className="space-y-2">
                {[
                  { timeSec: 0, scene: 'Scene 1', time: '00:00–00:08', flag: null, speaker: 'Brand Narrator', copy: 'Opening animated logo reveal. Voiceover: "Introducing Nova X — built for the modern cloud era." Visual uses approved dark variant with safe margins.' },
                  { timeSec: 8, scene: 'Scene 2', time: '00:08–00:19', flag: 'secret', speaker: 'Technical Architect', copy: 'Platform overview. Voiceover cites Project Apollo benchmark numbers. ⚠️ NDA violation: Project Apollo codename detected in spoken audio.' },
                  { timeSec: 19, scene: 'Scene 3', time: '00:19–00:30', flag: 'claim', speaker: 'Brand Narrator', copy: 'Closing CTA with March 2026 waitlist date. Voiceover claims "100% guaranteed uptime" — must be replaced with "99.9% measured uptime".' }
                ].map(function(sc) {
                  var isCurrent = videoTime >= sc.timeSec && (sc.timeSec === 19 ? videoTime <= 30 : videoTime < sc.timeSec + 11);
                  return (
                    <div
                      key={sc.scene}
                      onClick={function() { setVideoTime(sc.timeSec); }}
                      className={'p-3 rounded-xl border text-xs space-y-1.5 cursor-pointer transition-all ' + (
                        isCurrent ? 'bg-[#182338] border-blue-500 shadow-md ring-1 ring-blue-500/50' :
                        sc.flag ? 'bg-orange-950/20 border-orange-900/60 hover:border-orange-600' :
                        'bg-[#131926] border-[#1E293B] hover:border-slate-500'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white">{sc.scene}</span>
                          <span className="text-[10px] text-slate-400 font-mono">({sc.speaker})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-500 font-mono text-[11px]">{sc.time}</span>
                          {sc.flag === 'secret' && (
                            <span className="px-1.5 py-0.5 rounded bg-orange-950 text-orange-300 border border-orange-700 font-bold text-[9px]">
                              🔒 SECRET CODENAME
                            </span>
                          )}
                          {sc.flag === 'claim' && (
                            <span className="px-1.5 py-0.5 rounded bg-red-950 text-red-300 border border-red-700 font-bold text-[9px]">
                              ⚠️ MUST FIX CLAIM
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-slate-300 text-[11px] leading-relaxed">{sc.copy}</p>
                    </div>
                  );
                })}
              </div>

            </div>
          )}

        </div>
      );
    }
'''

# Replace old MultiModalCanvas with sound synth + certificate modal + command palette + team discussion + upgraded canvas
old_canvas_pattern = re.compile(r'    // ─── MULTI-MODAL CANVAS & REVIEW ENGINE \(WITH APPROVED BRAND COLOR PRESETS\).*?    // ─── BRAND MANAGER AUTOMATION PANEL ───', re.DOTALL)

replacement_block = sound_synth_code + '\n\n' + upgraded_canvas_code + '\n\n    // ─── BRAND MANAGER AUTOMATION PANEL ───'

content = old_canvas_pattern.sub(replacement_block, content, count=1)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Canvas and realism modals added successfully.")
