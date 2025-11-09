import { Fragment, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Dialog, Transition } from "@headlessui/react";
import { ChevronDown, ChevronUp, MailPlus, Reply } from "lucide-react";

import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";
import { EmailMessage, EmailSendPayload } from "../../types";
import {
  fetchLeadEmails,
  listEmailAccounts,
  sendEmail,
} from "../../services/integrations";
import { generateEmailTemplate } from "../../services/ai";

type LeadEmailPanelProps = {
  leadId: string;
  leadEmail: string;
  leadName: string;
};

const templateOptions = [
  { value: "initial_outreach", label: "Initial Outreach" },
  { value: "follow_up", label: "Follow Up" },
  { value: "demo_invite", label: "Demo Invite" },
  { value: "pricing_discussion", label: "Pricing Discussion" },
] as const;

type TemplateValue = (typeof templateOptions)[number]["value"];

export function LeadEmailPanel({ leadId, leadEmail, leadName }: LeadEmailPanelProps) {
  const queryClient = useQueryClient();
  const [expandedIds, setExpandedIds] = useState<Record<number, boolean>>({});
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [composeSubject, setComposeSubject] = useState("");
  const [composeBody, setComposeBody] = useState("");
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateValue>("follow_up");
  const [isLoadingTemplate, setIsLoadingTemplate] = useState(false);

  const { data: accounts = [] } = useQuery({
    queryKey: ["emailAccounts"],
    queryFn: listEmailAccounts,
  });

  const { data: emails = [], isLoading } = useQuery({
    queryKey: ["leadEmails", leadId],
    queryFn: () => fetchLeadEmails(leadId),
  });

  const sendMutation = useMutation({
    mutationFn: (payload: EmailSendPayload) => sendEmail(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["leadEmails", leadId] });
      setIsComposeOpen(false);
      setComposeSubject("");
      setComposeBody("");
    },
  });

  const selectedAccount = useMemo(
    () => accounts.find((account) => account.id === selectedAccountId),
    [accounts, selectedAccountId]
  );

  const hasAccounts = accounts.length > 0;
  const canCompose = hasAccounts && Boolean(leadEmail);

  useEffect(() => {
    if (!accounts.length) {
      setSelectedAccountId(null);
      return;
    }
    if (!selectedAccountId) {
      setSelectedAccountId(accounts[0].id);
    }
  }, [accounts, selectedAccountId]);

  const toggleExpanded = (id: number) => {
    setExpandedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const openCompose = (subject?: string, quotedMessage?: EmailMessage) => {
    if (!selectedAccountId && accounts.length > 0) {
      setSelectedAccountId(accounts[0].id);
    }
    if (subject) {
      setComposeSubject(subject);
    }
    if (quotedMessage) {
      setComposeBody(
        `\n\n--- Original Message ---\nFrom: ${quotedMessage.sender}\nDate: ${new Date(
          quotedMessage.sent_at
        ).toLocaleString()}\nSubject: ${quotedMessage.subject}\n\n${quotedMessage.body_text}`
      );
    }
    setIsComposeOpen(true);
  };

  const handleSend = () => {
    if (!selectedAccountId) return;
    if (!composeSubject.trim() || !composeBody.trim()) return;

    sendMutation.mutate({
      email_account_id: selectedAccountId,
      lead_id: leadId,
      subject: composeSubject,
      body: composeBody,
      recipients: [leadEmail],
    });
  };

  const applyTemplate = async () => {
    if (!leadId) return;
    setIsLoadingTemplate(true);
    try {
      const template = await generateEmailTemplate({
        lead_id: leadId,
        email_type: selectedTemplate,
      });
      setComposeSubject(template.subject);
      setComposeBody(template.body);
    } catch (error) {
      console.error("Failed to load template", error);
    } finally {
      setIsLoadingTemplate(false);
    }
  };

  const renderEmail = (email: EmailMessage) => {
    const isExpanded = expandedIds[email.id] ?? false;
    return (
      <div key={email.id} className="rounded-md border bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="font-semibold">{email.subject}</p>
            <p className="text-sm text-muted-foreground">
              {email.direction === "sent" ? "You" : email.sender} →{" "}
              {email.recipients.join(", ")}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              {email.direction === "sent" ? "Sent" : "Received"}
            </p>
            <p className="text-sm font-medium">
              {new Date(email.sent_at).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="mt-3 space-y-3 text-sm text-slate-700">
          <p className={isExpanded ? "" : "line-clamp-3"}>{email.body_text}</p>
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => openCompose(`Re: ${email.subject}`, email)}
            >
              <Reply className="mr-2 h-4 w-4" />
              Reply
            </Button>
            <Button variant="link" size="sm" onClick={() => toggleExpanded(email.id)}>
              {isExpanded ? (
                <>
                  Show less <ChevronUp className="ml-1 h-4 w-4" />
                </>
              ) : (
                <>
                  View full email <ChevronDown className="ml-1 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Email Thread</h2>
          <p className="text-sm text-muted-foreground">
            All emails exchanged with {leadName}. Messages are synced automatically from
            connected accounts.
          </p>
        </div>
        <Button onClick={() => openCompose()} disabled={!canCompose}>
          <MailPlus className="mr-2 h-4 w-4" />
          Compose Email
        </Button>
      </div>

      {!hasAccounts ? (
        <Card className="p-6 text-sm text-muted-foreground">
          Connect a Gmail or Outlook account from the Integrations page to compose and sync emails
          for this lead.
        </Card>
      ) : !leadEmail ? (
        <Card className="p-6 text-sm text-amber-600">
          This lead does not have an email address on file. Add one to send emails and track replies.
        </Card>
      ) : null}

      <div className="space-y-3">
        {isLoading ? (
          <Card className="p-6 text-sm text-muted-foreground">Loading emails…</Card>
        ) : emails.length === 0 ? (
          <Card className="p-6 text-sm text-muted-foreground">
            No emails with this lead yet. Start a conversation to see it appear here.
          </Card>
        ) : (
          emails.map(renderEmail)
        )}
      </div>

      <Transition appear show={isComposeOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setIsComposeOpen(false)}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-200"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-150"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/30" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-200"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-150"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-2xl overflow-hidden rounded-xl bg-white shadow-xl">
                  <Dialog.Title className="border-b px-6 py-4 text-lg font-semibold">
                    Compose Email
                  </Dialog.Title>
                  <div className="space-y-4 px-6 py-4">
                    <div className="grid gap-2 text-sm">
                      <label className="font-medium">From</label>
                      <select
                        className="rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                        value={selectedAccountId ?? ""}
                        onChange={(event) => setSelectedAccountId(Number(event.target.value))}
                      >
                        <option value="" disabled>
                          Select connected account
                        </option>
                        {accounts.map((account) => (
                          <option key={account.id} value={account.id}>
                            {account.email_address} ({account.provider})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="grid gap-2 text-sm">
                      <label className="font-medium">To</label>
                        <Input value={leadEmail || ""} readOnly />
                    </div>
                    <div className="grid gap-2 text-sm">
                      <label className="font-medium">Subject</label>
                      <Input
                        placeholder="Email subject"
                        value={composeSubject}
                        onChange={(event) => setComposeSubject(event.target.value)}
                      />
                    </div>
                    <div className="grid gap-2 text-sm">
                      <div className="flex items-center justify-between">
                        <label className="font-medium">Body</label>
                        <div className="flex items-center gap-2">
                          <select
                            className="rounded-md border border-slate-200 px-2 py-1 text-xs focus:border-primary focus:outline-none"
                            value={selectedTemplate}
                            onChange={(event) =>
                              setSelectedTemplate(event.target.value as TemplateValue)
                            }
                          >
                            {templateOptions.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={applyTemplate}
                            disabled={isLoadingTemplate}
                          >
                            {isLoadingTemplate ? "Loading..." : "Use Template"}
                          </Button>
                        </div>
                      </div>
                      <Textarea
                        className="min-h-[200px]"
                        value={composeBody}
                        onChange={(event) => setComposeBody(event.target.value)}
                        placeholder="Write your email..."
                      />
                      <p className="text-xs text-muted-foreground">
                        Attachments support is coming soon. Paste links or use cloud storage for now.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center justify-between border-t bg-slate-50 px-6 py-4">
                    <p className="text-xs text-muted-foreground">
                      Emails are sent securely via the connected provider and logged to the lead
                      timeline.
                    </p>
                    <div className="flex gap-2">
                      <Button variant="ghost" onClick={() => setIsComposeOpen(false)}>
                        Cancel
                      </Button>
                      <Button
                        onClick={handleSend}
                        disabled={!selectedAccount || sendMutation.isPending}
                      >
                        {sendMutation.isPending ? "Sending..." : "Send Email"}
                      </Button>
                    </div>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
}

export default LeadEmailPanel;
