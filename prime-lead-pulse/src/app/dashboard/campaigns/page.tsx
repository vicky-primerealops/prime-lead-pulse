'use client';

import { useState, useEffect } from 'react';
import { useDashboardData } from '@/hooks/useDashboardData';

export default function CampaignsPage() {
  const { user, supabase } = useDashboardData();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    body: '',
    sheet_url: '',
    batch_size: 50,
    delay_seconds: 40
  });

  useEffect(() => {
    if (user) fetchCampaigns();
  }, [user]);

  const fetchCampaigns = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      const res = await fetch('/api/campaigns', {
        headers: { Authorization: `Bearer ${session.access_token}` }
      });
      const data = await res.json();
      if (data.success) {
        setCampaigns(data.campaigns);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;
      
      const res = await fetch('/api/campaigns', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      const data = await res.json();
      if (data.success) {
        setIsModalOpen(false);
        setFormData({ name: '', subject: '', body: '', sheet_url: '', batch_size: 50, delay_seconds: 40 });
        fetchCampaigns();
      }
    } catch (err) {
      console.error(err);
      alert('Failed to create campaign');
    }
  };

  const downloadScript = async (id: string) => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return;
    window.location.href = `/api/campaigns/download/${id}?token=${session.access_token}`;
  };

  if (loading) return <div className="p-8 text-slate-500">Loading campaigns...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Email Campaigns</h1>
          <p className="text-slate-500 mt-1">Send personalized bulk emails directly from your Google Sheet using Google's servers.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-sm transition-all hover:shadow-md flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          Create New Campaign
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {campaigns.length === 0 ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 border border-slate-100">
              <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
              </svg>
            </div>
            <p className="text-lg font-semibold text-slate-900">No campaigns created yet</p>
            <p className="mt-1 mb-6 text-sm">Create your first campaign to generate your sending script.</p>
            <button onClick={() => setIsModalOpen(true)} className="text-indigo-600 font-medium hover:text-indigo-800">
              + Get Started
            </button>
          </div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-medium">
              <tr>
                <th className="px-6 py-4">Campaign Name</th>
                <th className="px-6 py-4">Subject</th>
                <th className="px-6 py-4">Created Date</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {campaigns.map(camp => (
                <tr key={camp.id} className="hover:bg-slate-50 transition-colors group">
                  <td className="px-6 py-4 font-medium text-slate-900">{camp.name}</td>
                  <td className="px-6 py-4 text-slate-500 truncate max-w-[200px]">{camp.subject}</td>
                  <td className="px-6 py-4 text-slate-500">
                    {new Date(camp.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => downloadScript(camp.id)}
                      className="text-indigo-600 font-medium inline-flex items-center gap-2 bg-indigo-50 px-4 py-2 rounded-xl transition-colors hover:bg-indigo-600 hover:text-white"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                      Copy Script
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* MODAL */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
            
            {/* Header */}
            <div className="px-8 py-5 border-b border-slate-100 flex items-center justify-between shrink-0">
              <div>
                <h2 className="text-xl font-bold text-slate-900">Campaign Builder</h2>
                <p className="text-sm text-slate-500 mt-1">Configure your email blast. We'll generate a script that sends it for you.</p>
              </div>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-50 rounded-full transition-colors">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            
            {/* Scrollable Form */}
            <div className="overflow-y-auto p-8 shrink">
              <form id="campaignForm" onSubmit={handleCreate} className="space-y-8">
                
                {/* Step 1 */}
                <div className="space-y-4">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs">1</span>
                    <h3 className="font-semibold text-slate-900">Campaign Details</h3>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">What is this campaign for?</label>
                    <p className="text-xs text-slate-500 mb-2">Just for your own reference (e.g. "Summer Investor Outreach").</p>
                    <input 
                      required type="text"
                      className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-sm"
                      value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})}
                    />
                  </div>
                </div>

                {/* Step 2 */}
                <div className="space-y-4">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs">2</span>
                    <h3 className="font-semibold text-slate-900">Link your Gmail Draft</h3>
                  </div>
                  
                  <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-2 text-sm text-blue-800 leading-relaxed">
                    <p className="font-semibold mb-1">How this works:</p>
                    <ol className="list-decimal ml-4 space-y-1">
                      <li>Go to Gmail and create a new email draft with all your formatting, images, and signature.</li>
                      <li>You can use <code className="bg-blue-100/50 px-1 py-0.5 rounded text-blue-700">{`{first_name}`}</code> anywhere in the draft's subject or body to personalize it.</li>
                      <li>Copy the exact Subject of that draft and paste it below. Our script will automatically find it and send it!</li>
                    </ol>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Exact Subject of your Gmail Draft</label>
                    <input 
                      required type="text"
                      placeholder="e.g. Quick question for {first_name}"
                      className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-sm font-medium"
                      value={formData.subject} onChange={e => setFormData({...formData, subject: e.target.value})}
                    />
                  </div>
                </div>

                {/* Step 3 */}
                <div className="space-y-4">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs">3</span>
                    <h3 className="font-semibold text-slate-900">Connect your Data</h3>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Google Sheet Link</label>
                    <div className="bg-amber-50 border border-amber-100 rounded-lg p-3 mb-3 text-xs text-amber-800 leading-relaxed">
                      <strong>Important:</strong> 
                      <ol className="list-decimal ml-4 mt-1 space-y-1">
                        <li>Your sheet must have a column named <strong>Name</strong> and a column named <strong>Email</strong>.</li>
                        <li>You must click the "Share" button in Google Sheets and set it to <strong>"Anyone with the link can view"</strong>.</li>
                      </ol>
                    </div>
                    <input 
                      required type="url"
                      placeholder="Paste your Google Sheet link here..."
                      className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-sm"
                      value={formData.sheet_url} onChange={e => setFormData({...formData, sheet_url: e.target.value})}
                    />
                  </div>
                </div>

                {/* Step 4 */}
                <div className="space-y-4">
                  <div className="flex items-center gap-3 border-b border-slate-100 pb-2">
                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs">4</span>
                    <h3 className="font-semibold text-slate-900">Sending Speed</h3>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Batch Size</label>
                      <p className="text-xs text-slate-500 mb-2">How many emails to send total?</p>
                      <input 
                        required type="number" min="1" max="500"
                        className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-sm"
                        value={formData.batch_size} onChange={e => setFormData({...formData, batch_size: parseInt(e.target.value)})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Delay (Seconds)</label>
                      <p className="text-xs text-slate-500 mb-2">Wait time between each email.</p>
                      <input 
                        required type="number" min="0" max="300"
                        className="w-full border border-slate-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-sm"
                        value={formData.delay_seconds} onChange={e => setFormData({...formData, delay_seconds: parseInt(e.target.value)})}
                      />
                    </div>
                  </div>
                </div>

              </form>
            </div>
            
            {/* Footer */}
            <div className="p-6 border-t border-slate-100 bg-slate-50 shrink-0 flex items-center justify-between rounded-b-2xl">
              <span className="text-sm text-slate-500">
                You will get a script to run in your Google Sheet on the next step.
              </span>
              <div className="flex gap-3">
                <button type="button" onClick={() => setIsModalOpen(false)} className="px-5 py-2.5 text-slate-600 font-semibold hover:bg-slate-200 rounded-xl transition-colors">
                  Cancel
                </button>
                <button type="submit" form="campaignForm" className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-semibold shadow-sm transition-all hover:shadow-md hover:-translate-y-0.5">
                  Save & Next
                </button>
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
