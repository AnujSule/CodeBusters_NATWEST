import React, { useState } from 'react';
import { Shield } from 'lucide-react';
import { AuditTable } from '../components/audit/AuditTable';
import { Spinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { useAuditLog } from '../hooks/useAuditLog';

const AuditPage: React.FC = () => {
    const [page, setPage] = useState(1);
    const { data, isLoading, isError } = useAuditLog(page);

    return (
        <div className="flex-1 p-8 overflow-y-auto">
            <div className="max-w-6xl mx-auto">
                <div className="flex items-center gap-3 mb-8">
                    <div className="p-2 rounded-lg bg-accent-purple/10">
                        <Shield className="h-6 w-6 text-accent-purple" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-text-primary">Audit Log</h1>
                        <p className="text-sm text-text-secondary">Complete transparency — every query, every model, every token.</p>
                    </div>
                </div>

                {isLoading ? (
                    <Spinner size="lg" className="py-20" />
                ) : isError ? (
                    <EmptyState
                        title="Failed to load audit log"
                        description="Please try again later."
                    />
                ) : !data || data.entries.length === 0 ? (
                    <EmptyState
                        icon={<Shield className="h-10 w-10 text-text-muted" />}
                        title="No queries yet"
                        description="Your query audit trail will appear here once you start asking questions."
                    />
                ) : (
                    <AuditTable
                        entries={data.entries}
                        total={data.total}
                        page={data.page}
                        pageSize={data.page_size}
                        onPageChange={setPage}
                    />
                )}
            </div>
        </div>
    );
};

export default AuditPage;
