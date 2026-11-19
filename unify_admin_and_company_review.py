import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update initialUserRoster to unify Admin & Company Review
old_roster = '''  var initialUserRoster = [
   { id: 1, name: 'Sarah Chen', email: 'admin@veritasbrand.io', role: 'Admin', department: 'Executive Governance', status: 'Active' },
   { id: 2, name: 'Alex Rivera', email: 'creator@veritasbrand.io', role: 'Creator', department: 'Content Production', status: 'Active' },
   { id: 3, name: 'Jordan Miller', email: 'manager@veritasbrand.io', role: 'Brand Manager', department: 'Brand Strategy', status: 'Active' },
   { id: 4, name: 'Elena Vance', email: 'legal@veritasbrand.io', role: 'Legal Reviewer', department: 'Legal & Regulatory', status: 'Active' }
  ];'''

new_roster = '''  var initialUserRoster = [
   { id: 1, name: 'Sarah Chen', email: 'admin@veritasbrand.io', role: 'Admin & Company Review', department: 'Executive Governance & Master Monitoring', status: 'Active' },
   { id: 2, name: 'Alex Rivera', email: 'creator@veritasbrand.io', role: 'Creator', department: 'Content Production', status: 'Active' },
   { id: 3, name: 'Jordan Miller', email: 'manager@veritasbrand.io', role: 'Brand Manager', department: 'Brand Strategy', status: 'Active' },
   { id: 4, name: 'Elena Vance, Esq.', email: 'legal@veritasbrand.io', role: 'Admin & Company Review', department: 'Company Review & Legal Compliance', status: 'Active' }
  ];

  function isMonitorOrAdmin(roleOrUser) {
   var r = (typeof roleOrUser === 'string' ? roleOrUser : (roleOrUser && roleOrUser.role)) || '';
   return r === 'Admin' || r === 'Legal Reviewer' || r === 'Company Review' || r === 'Admin & Company Review';
  }'''

text = text.replace(old_roster, new_roster)

# 2. Update demoAccounts in SignInScreen
old_demo = '''    var demoAccounts = [
      {
        id: 'creator',
        role: 'Creator',
        name: 'Alex Rivera',
        email: 'creator@veritasbrand.io',
        badge: 'CREATOR DESK',
        icon: '',
        accent: 'border-emerald-300 bg-emerald-50/50 hover:bg-emerald-100/50 text-emerald-900',
        desc: 'Review Studio, Knowledge Base, Media Dropzone, Inbox & AI Writing Helper.'
      },
      {
        id: 'admin',
        role: 'Admin',
        name: 'Sarah Chen',
        email: 'admin@veritasbrand.io',
        badge: 'SYSTEM ADMINISTRATOR',
        icon: '',
        accent: 'border-blue-300 bg-blue-50/50 hover:bg-blue-100/50 text-blue-900',
        desc: 'Full governance controls, user provisioning, and full cross-dashboard access.'
      },
      {
        id: 'manager',
        role: 'Brand Manager',
        name: 'Jordan Miller',
        email: 'manager@veritasbrand.io',
        badge: 'STEP 1 GOVERNANCE',
        icon: '',
        accent: 'border-blue-300 bg-blue-50/50 hover:bg-blue-100/50 text-blue-900',
        desc: 'Step 1 approval, 3-Level automation engine, original file mistake map & auto-email.'
      },
      {
        id: 'legal',
        role: 'Legal Reviewer',
        name: 'Elena Vance',
        email: 'legal@veritasbrand.io',
        badge: 'LEGAL & COMPLIANCE',
        icon: '',
        accent: 'border-emerald-300 bg-emerald-50/50 hover:bg-emerald-100/50 text-emerald-900',
        desc: 'Final legal verification, unverified SLA blocks, secret name NDA checks & publishing.'
      }
    ];'''

new_demo = '''    var demoAccounts = [
      {
        id: 'creator',
        role: 'Creator',
        name: 'Alex Rivera',
        email: 'creator@veritasbrand.io',
        badge: 'CREATOR DESK',
        icon: '',
        accent: 'border-emerald-300 bg-emerald-50/50 hover:bg-emerald-100/50 text-emerald-900',
        desc: 'Drafts copy, drops media files, receives reviewer feedback, AI writing helper.'
      },
      {
        id: 'manager',
        role: 'Brand Manager',
        name: 'Jordan Miller',
        email: 'manager@veritasbrand.io',
        badge: 'BRAND MANAGER · STEP 1',
        icon: '',
        accent: 'border-blue-300 bg-blue-50/50 hover:bg-blue-100/50 text-blue-900',
        desc: 'Step 1 approval, 3-Level automation engine, original file mistake map & auto-email.'
      },
      {
        id: 'admin',
        role: 'Admin & Company Review',
        name: 'Sarah Chen',
        email: 'admin@veritasbrand.io',
        badge: 'ADMIN & COMPANY REVIEW · MASTER MONITOR',
        icon: '',
        accent: 'border-blue-400 bg-blue-50/60 hover:bg-blue-100 text-blue-950 font-bold',
        desc: 'Full system oversight, monitors all workspaces, user provisioning, legal sign-off & final approvals.'
      },
      {
        id: 'legal',
        role: 'Admin & Company Review',
        name: 'Elena Vance, Esq.',
        email: 'legal@veritasbrand.io',
        badge: 'ADMIN & COMPANY REVIEW · MASTER MONITOR',
        icon: '',
        accent: 'border-emerald-400 bg-emerald-50/60 hover:bg-emerald-100 text-emerald-950 font-bold',
        desc: 'Full system oversight, secret NDA vault, SLA compliance, legal sign-off & final approvals.'
      }
    ];'''

text = text.replace(old_demo, new_demo)

# 3. Update Quick Sign-In Dropdown options
old_signin_drop = '''                      <option value="" disabled>Select Role to Sign In Immediately ▼</option>
                      <option value="creator">Alex Rivera — Creator Desk (Review Studio & Knowledge Base)</option>
                      <option value="manager">Jordan Miller — Brand Manager (Step 1 Governance)</option>
                      <option value="legal">Elena Vance — Legal Reviewer (Step 2 Legal Verification)</option>
                      <option value="admin">Sarah Chen — Admin (Full System Access)</option>'''

new_signin_drop = '''                      <option value="" disabled>Select Role to Sign In Immediately ▼</option>
                      <option value="creator">Alex Rivera — Creator Desk (Review Studio & Knowledge Base)</option>
                      <option value="manager">Jordan Miller — Brand Manager (Step 1 Governance & Automation)</option>
                      <option value="admin">Sarah Chen — Admin & Company Review (Monitors Everything · Master Access)</option>
                      <option value="legal">Elena Vance, Esq. — Admin & Company Review (Monitors Everything · Legal Sign-off)</option>'''

text = text.replace(old_signin_drop, new_signin_drop)

# 4. Handle email login mapping
old_email_map = '''        var role = 'Creator';
        var name = trimmed.split('@')[0];
        if (trimmed.indexOf('admin') !== -1) role = 'Admin';
        else if (trimmed.indexOf('manager') !== -1) role = 'Brand Manager';
        else if (trimmed.indexOf('legal') !== -1) role = 'Legal Reviewer';'''

new_email_map = '''        var role = 'Creator';
        var name = trimmed.split('@')[0];
        if (trimmed.indexOf('admin') !== -1 || trimmed.indexOf('legal') !== -1) role = 'Admin & Company Review';
        else if (trimmed.indexOf('manager') !== -1) role = 'Brand Manager';'''

text = text.replace(old_email_map, new_email_map)

# 5. Update Registration role options
old_reg_roles = '''                <select
                  value={regRole}
                  onChange={function(e) { setRegRole(e.target.value); }}
                  className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:border-blue-500 focus:outline-none"
                >
                  <option value="Creator">Creator (Creator Desk)</option>
                  <option value="Brand Manager">Brand Manager (Step 1 Review)</option>
                  <option value="Legal Reviewer">Company Review (Step 2 Legal)</option>
                </select>'''

new_reg_roles = '''                <select
                  value={regRole}
                  onChange={function(e) { setRegRole(e.target.value); }}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 font-semibold focus:border-blue-500 shadow-xs cursor-pointer"
                >
                  <option value="Creator">Creator (Creator Desk)</option>
                  <option value="Brand Manager">Brand Manager (Step 1 Review)</option>
                  <option value="Admin & Company Review">Admin & Company Review (Monitors Everything)</option>
                </select>'''

text = text.replace(old_reg_roles, new_reg_roles)

# 6. Update AdminAccessControlModal role options and display
old_admin_modal_roles = '''                <select
                  value={role}
                  onChange={function(e) { setRole(e.target.value); }}
                  className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 focus:border-blue-500 focus:outline-none"
                >
                  <option value="Creator">Creator (Creator Desk)</option>
                  <option value="Brand Manager">Brand Manager (Step 1)</option>
                  <option value="Legal Reviewer">Legal Reviewer (Step 2)</option>
                  <option value="Admin">Admin (Full Access)</option>
                </select>'''

new_admin_modal_roles = '''                <select
                  value={role}
                  onChange={function(e) { setRole(e.target.value); }}
                  className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 font-semibold focus:border-blue-500 shadow-xs cursor-pointer"
                >
                  <option value="Creator">Creator (Creator Desk)</option>
                  <option value="Brand Manager">Brand Manager (Step 1)</option>
                  <option value="Admin & Company Review">Admin & Company Review (Monitors Everything)</option>
                </select>'''

text = text.replace(old_admin_modal_roles, new_admin_modal_roles)

# Also update the user role update select in AdminAccessControlModal
old_user_role_sel = '''                      <select
                        value={u.role}
                        onChange={function(e) { onUpdateRole(u.id, e.target.value); }}
                        className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-[11px] text-slate-900 focus:border-blue-500 focus:outline-none"
                      >
                        <option value="Admin">Admin</option>
                        <option value="Creator">Creator</option>
                        <option value="Brand Manager">Brand Manager</option>
                        <option value="Legal Reviewer">Company Review</option>
                      </select>'''

new_user_role_sel = '''                      <select
                        value={u.role}
                        onChange={function(e) { onUpdateRole(u.id, e.target.value); }}
                        className="bg-white border border-slate-300 rounded-lg px-2 py-1 text-[11px] text-slate-900 font-bold focus:border-blue-500 shadow-xs cursor-pointer"
                      >
                        <option value="Admin & Company Review">Admin & Company Review (Master Monitor)</option>
                        <option value="Creator">Creator</option>
                        <option value="Brand Manager">Brand Manager</option>
                      </select>'''

text = text.replace(old_user_role_sel, new_user_role_sel)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied User Roster & Sign In Role Unification.")
