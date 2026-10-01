import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useEmail } from "../../hooks/useEmail";
import { emailService } from "../../services/emailService";

import { SearchBar } from "../../components/common/SearchBar";
import { EmailCard } from "../../components/ui/EmailCard";
import { SkeletonLoader } from "../../components/common/SkeletonLoader";
import { EmptyState } from "../../components/common/EmptyState";
import { Modal } from "../../components/common/Modal";

import type {
  Email,
  EmailCategory,
  EmailSummary,
} from "../../types/email";

import {
  Sparkles,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

export const InboxPage: React.FC = () => {
    const [isSyncing, setIsSyncing] = useState(false);
    const [syncError, setSyncError] = useState<string | null>(null);
    const [activeTab, setActiveTab] =
      useState<EmailCategory | "All">("All");

  const [searchQuery, setSearchQuery] =
    useState("");

  const [selectedEmail, setSelectedEmail] =
    useState<Email | null>(null);

  const [summary, setSummary] =
    useState<EmailSummary | null>(null);

  const [isAnalyzing, setIsAnalyzing] =
    useState(false);

  const [analysisError, setAnalysisError] =
    useState<string | null>(null);

    const {
    emails,
    isLoading,
    toggleStar,
    archiveEmail,
    refetch,
  } = useEmail({
    category: activeTab,
    searchQuery,
  });

    useEffect(() => {
    const syncGmail = async () => {
      setIsSyncing(true);
      setSyncError(null);

      try {
        const result = await emailService.syncEmails();

        console.log("Gmail sync completed:", result);

        // Reload emails from Supabase after Gmail sync.
        await refetch({
          category: activeTab,
          searchQuery,
        });
      } catch (error) {
        console.error("Gmail sync failed:", error);

        setSyncError(
          error instanceof Error
            ? error.message
            : "Failed to synchronize Gmail."
        );
      } finally {
        setIsSyncing(false);
      }
    };

    syncGmail();
  }, []);

  const navigate = useNavigate();

  const categories: (
    | EmailCategory
    | "All"
  )[] = [
    "All",
    "Career",
    "System",
    "Design",
    "Newsletters",
  ];

  const handleGenerateSummary = async (
    email: Email
  ) => {
    setSelectedEmail(email);
    setSummary(null);
    setAnalysisError(null);
    setIsAnalyzing(true);

    try {
      const result =
        await emailService.generateSummary(
          email.id
        );

      setSummary({
        keyTakeaways:
          result.key_takeaways || [],

        recommendedAction:
          result.recommended_action ||
          "Review this email.",

        sentiment:
          (result.sentiment as EmailSummary["sentiment"]) ||
          "neutral",
      });
    } catch (error) {
      console.error(
        "AI summary error:",
        error
      );

      setAnalysisError(
        error instanceof Error
          ? error.message
          : "Failed to generate AI summary."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold font-headline text-on-surface">
            Inbox Workstation
          </h2>

          <p className="text-xs text-on-surface-variant mt-1">
            Real-time synchronized emails categorized by AI priority engine.
          </p>
        </div>

                <div className="flex items-center gap-3">
          {isSyncing && (
            <div className="flex items-center gap-2 text-xs text-on-surface-variant">
              <div className="w-3.5 h-3.5 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
              Syncing Gmail...
            </div>
          )}

          {!isSyncing && !syncError && (
            <div className="text-xs text-on-surface-variant">
              Gmail synchronized
            </div>
          )}

          {syncError && (
            <div className="text-xs text-error">
              Gmail sync failed
            </div>
          )}

          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
          />
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none border-b border-white/10">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveTab(cat)}
            className={`px-4 py-2 text-xs font-semibold rounded-2xl transition-all whitespace-nowrap ${
              activeTab === cat
                ? "bg-primary text-on-primary shadow-md"
                : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Email Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <SkeletonLoader
            count={6}
            className="h-56"
          />
        </div>
      ) : emails.length === 0 ? (
        <EmptyState
          title="No emails match your filter"
          description="Try selecting a different category or clearing your search term."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {emails.map((email) => (
            <EmailCard
              key={email.id}
              email={email}
              onSelect={(e) =>
                navigate(`/inbox/${e.id}`)
              }
              onToggleStar={toggleStar}
              onArchive={archiveEmail}
              onGenerateSummary={
                handleGenerateSummary
              }
            />
          ))}
        </div>
      )}

      {/* AI Summary Modal */}
      <Modal
        isOpen={!!selectedEmail}
        onClose={() => {
          setSelectedEmail(null);
          setSummary(null);
          setAnalysisError(null);
        }}
        title="AI Email Analysis"
        maxWidth="lg"
      >
        {selectedEmail && (
          <div className="space-y-5">

            {/* Email context */}
            <div className="glass-panel p-4 rounded-2xl border border-white/10">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>

                <div className="min-w-0">
                  <p className="text-xs text-on-surface-variant">
                    {selectedEmail.sender.name}
                  </p>

                  <h3 className="font-bold text-on-surface mt-1">
                    {selectedEmail.subject}
                  </h3>
                </div>
              </div>
            </div>

            {/* Loading */}
            {isAnalyzing && (
              <div className="py-10 flex flex-col items-center justify-center text-center">
                <div className="w-12 h-12 rounded-full border-2 border-primary/30 border-t-primary animate-spin mb-4" />

                <p className="font-semibold text-on-surface">
                  Gemini is analyzing this email...
                </p>

                <p className="text-xs text-on-surface-variant mt-1">
                  Extracting key information and recommended actions.
                </p>
              </div>
            )}

            {/* Error */}
            {!isAnalyzing &&
              analysisError && (
                <div className="p-4 rounded-2xl bg-error/10 border border-error/20">
                  <div className="flex gap-3">
                    <AlertCircle className="w-5 h-5 text-error shrink-0" />

                    <div>
                      <p className="font-semibold text-error">
                        AI analysis failed
                      </p>

                      <p className="text-xs text-on-surface-variant mt-1 break-words">
                        {analysisError}
                      </p>
                    </div>
                  </div>
                </div>
              )}

            {/* Result */}
            {!isAnalyzing &&
              summary && (
                <div className="space-y-4">

                  {/* Takeaways */}
                  <div className="glass-panel p-5 rounded-2xl border border-white/10">
                    <div className="flex items-center gap-2 mb-3">
                      <CheckCircle2 className="w-4 h-4 text-primary" />

                      <h4 className="font-bold text-sm text-on-surface">
                        Key Takeaways
                      </h4>
                    </div>

                    <ul className="space-y-2">
                      {summary.keyTakeaways.map(
                        (point, index) => (
                          <li
                            key={index}
                            className="text-sm text-on-surface-variant flex gap-2"
                          >
                            <span className="text-primary">
                              •
                            </span>

                            <span>
                              {point}
                            </span>
                          </li>
                        )
                      )}
                    </ul>
                  </div>

                  {/* Recommended Action */}
                  <div className="glass-panel p-5 rounded-2xl border border-primary/20 bg-primary/5">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-primary mb-2">
                      Recommended Action
                    </p>

                    <p className="text-sm font-semibold text-on-surface">
                      {summary.recommendedAction}
                    </p>
                  </div>

                  {/* Sentiment */}
                  <div className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/10">
                    <span className="text-xs font-semibold text-on-surface-variant">
                      AI-detected sentiment
                    </span>

                    <span className="text-xs font-bold text-primary capitalize">
                      {summary.sentiment.replace(
                        "_",
                        " "
                      )}
                    </span>
                  </div>

                </div>
              )}

          </div>
        )}
      </Modal>
    </div>
  );
};