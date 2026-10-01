import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../../services/dashboardService';
import type { DashboardSummary } from '../../services/dashboardService';
import { useEmail } from '../../hooks/useEmail';
import { MetricCard } from '../../components/ui/MetricCard';
import { EmailCard } from '../../components/ui/EmailCard';
import { AIChatInput } from '../../components/ai/AIChatInput';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { SkeletonLoader } from '../../components/common/SkeletonLoader';
import type { Email } from '../../types/email';
import { Sparkles, ArrowRight, Send } from 'lucide-react';
import { motion } from 'framer-motion';

import { useAuth } from '../../hooks/useAuth';
import { emailService } from '../../services/emailService';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [draftReplyText, setDraftReplyText] = useState('');

  const { user } = useAuth();
  const { emails, isLoading: isLoadingEmails, toggleStar, archiveEmail } = useEmail();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await dashboardService.getDashboardSummary();
        setSummary(data);
      } finally {
        setIsLoadingSummary(false);
      }
    };
    fetchDashboard();
  }, []);

  const handleAskAI = (text: string) => {
    navigate('/ai-chat', { state: { initialPrompt: text } });
  };

  const handleOpenDraftReply = async (email: Email) => {
    setSelectedEmail(email);
    setDraftReplyText('Generating AI draft reply...');
    try {
      const draft = await emailService.generateDraftReply(email.id);
      setDraftReplyText(draft);
    } catch {
      setDraftReplyText(`Hi ${email.sender.name.split(' ')[0]},\n\nThank you for reaching out regarding "${email.subject}". I have received your email and will follow up shortly.\n\nBest regards,\n${user?.name || ''}`);
    }
  };

  return (
    <div className="space-y-8">
      {/* Workspace Summary Bento Grid Header */}
      <section>
        <h2 className="text-2xl font-extrabold font-headline text-on-surface tracking-tight mb-4">
          Today's Workspace Summary
        </h2>
        {isLoadingSummary ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <SkeletonLoader count={4} className="h-40" />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {summary?.metrics.map((m) => (
              <MetricCard key={m.id} metric={m} />
            ))}
          </div>
        )}
      </section>

      {/* AI Advice & Ask MailPilot Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AI Smart Advice Card */}
        <motion.div
          whileHover={{ y: -2 }}
          className="lg:col-span-1 glass-panel p-6 rounded-3xl border border-primary/40 relative overflow-hidden flex flex-col justify-between"
        >
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-xs font-bold text-primary uppercase tracking-wider">AI SMART ADVICE</span>
          </div>

          <div>
            <h3 className="text-lg font-bold text-on-surface leading-snug mb-2">
              {summary?.smartAdvice.title || 'Review Google Interview Invitation'}
            </h3>
            <p className="text-xs text-on-surface-variant leading-relaxed mb-4">
              {summary?.smartAdvice.description}
            </p>
          </div>

          <Button
            variant="outline"
            onClick={() => {
              const target = emails.find((e) => e.id === summary?.smartAdvice.emailId) || emails[0];
              if (target) handleOpenDraftReply(target);
            }}
            className="w-full justify-center bg-primary/10 text-primary border-primary/30 hover:bg-primary hover:text-on-primary font-bold"
          >
            Draft Reply with AI
          </Button>
        </motion.div>

        {/* Ask MailPilot Box */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-white/10 flex flex-col justify-between relative overflow-hidden">
          <div>
            <h3 className="text-xl font-bold text-on-surface mb-1">Ask MailPilot Assistant</h3>
            <p className="text-xs text-on-surface-variant mb-4">
              Type any query or select a workflow prompt below to query Gemini AI.
            </p>
            <AIChatInput onSend={handleAskAI} />
          </div>

          <div className="flex flex-wrap gap-2 mt-4">
            {["Summarize today's emails", "Find internship opportunities", "Track Amazon order"].map((pill) => (
              <button
                key={pill}
                onClick={() => handleAskAI(pill)}
                className="px-3.5 py-1.5 bg-white/5 hover:bg-white/10 rounded-full border border-white/10 text-xs text-on-surface-variant transition-colors"
              >
                {pill}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Emails Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-on-surface">Recent Emails</h3>
          <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="w-4 h-4" />} onClick={() => navigate('/inbox')}>
            View All Inbox
          </Button>
        </div>

        {isLoadingEmails ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <SkeletonLoader count={3} className="h-56" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {emails.slice(0, 3).map((email) => (
              <EmailCard
                key={email.id}
                email={email}
                onSelect={(e) => navigate(`/inbox/${e.id}`)}
                onToggleStar={toggleStar}
                onArchive={archiveEmail}
                onGenerateSummary={(e) => handleOpenDraftReply(e)}
              />
            ))}
          </div>
        )}
      </section>

      {/* AI Draft Modal */}
      <Modal
        isOpen={!!selectedEmail}
        onClose={() => setSelectedEmail(null)}
        title={selectedEmail ? `AI Draft: ${selectedEmail.subject}` : ''}
        maxWidth="lg"
      >
        {selectedEmail && (
          <div className="space-y-4">
            <div className="p-3 bg-surface-container-low rounded-2xl border border-white/5 text-xs space-y-1">
              <p><span className="text-on-surface-variant">To:</span> {selectedEmail.sender.email}</p>
              <p><span className="text-on-surface-variant">Sender:</span> {selectedEmail.sender.name}</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-2">
                Contextual AI Response
              </label>
              <textarea
                rows={6}
                value={draftReplyText}
                onChange={(e) => setDraftReplyText(e.target.value)}
                className="w-full bg-surface-container-lowest border border-white/10 rounded-2xl p-4 text-sm text-on-surface focus:ring-2 focus:ring-primary/40 focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <Button variant="ghost" onClick={() => setSelectedEmail(null)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                leftIcon={<Send className="w-4 h-4" />}
                onClick={() => {
                  alert('Email Response Dispatched via MailPilot service!');
                  setSelectedEmail(null);
                }}
              >
                Send Email
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
