import React, { useState } from 'react';
import { Upload } from 'lucide-react';
import { Sidebar } from '../components/layout/Sidebar';
import { FileUploadZone } from '../components/upload/FileUploadZone';
import { UploadProgress } from '../components/upload/UploadProgress';
import { EmptyState } from '../components/ui/EmptyState';
import { Button } from '../components/ui/Button';
import { useDatasets, useUploadDataset } from '../hooks/useDatasets';
import { useDatasetStore } from '../store/datasetStore';
import DatasetPage from './DatasetPage';

const DashboardPage: React.FC = () => {
    const [showUpload, setShowUpload] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [datasetName, setDatasetName] = useState('');

    const { isLoading: loadingDatasets } = useDatasets();
    const uploadMutation = useUploadDataset();
    const { selectedDataset } = useDatasetStore();

    const handleFileSelect = (file: File) => {
        setSelectedFile(file);
        if (!datasetName) {
            setDatasetName(file.name.replace(/\.(csv|pdf)$/i, ''));
        }
    };

    const handleUpload = async () => {
        if (!selectedFile || !datasetName) return;
        await uploadMutation.mutateAsync({ file: selectedFile, name: datasetName });
        setSelectedFile(null);
        setDatasetName('');
        setShowUpload(false);
    };

    const uploadStatus = uploadMutation.isPending
        ? 'uploading'
        : uploadMutation.isSuccess
            ? 'ready'
            : uploadMutation.isError
                ? 'failed'
                : null;

    return (
        <div className="flex w-full h-[calc(100vh-4rem)]">
            <Sidebar onUploadClick={() => setShowUpload(true)} />

            <div className="flex-1 overflow-y-auto">
                {showUpload ? (
                    <div className="max-w-2xl mx-auto p-8 animate-fade-in">
                        <h2 className="text-2xl font-bold text-text-primary mb-6">Upload Dataset</h2>

                        <div className="space-y-6">
                            <FileUploadZone
                                onFileSelect={handleFileSelect}
                                isUploading={uploadMutation.isPending}
                                selectedFile={selectedFile}
                                onClear={() => { setSelectedFile(null); setDatasetName(''); }}
                            />

                            {selectedFile && (
                                <div className="space-y-4 animate-fade-in">
                                    <div>
                                        <label className="block text-sm font-medium text-text-secondary mb-1.5">Dataset Name</label>
                                        <input
                                            type="text"
                                            value={datasetName}
                                            onChange={(e) => setDatasetName(e.target.value)}
                                            placeholder="e.g. Q1 Sales Data"
                                            className="input-field"
                                            id="dataset-name-input"
                                        />
                                    </div>

                                    <div className="flex gap-3">
                                        <Button onClick={handleUpload} isLoading={uploadMutation.isPending} disabled={!datasetName}>
                                            Upload & Process
                                        </Button>
                                        <Button variant="secondary" onClick={() => setShowUpload(false)}>
                                            Cancel
                                        </Button>
                                    </div>
                                </div>
                            )}

                            {uploadStatus && (
                                <UploadProgress
                                    status={uploadStatus}
                                    error={uploadMutation.error?.message}
                                />
                            )}
                        </div>
                    </div>
                ) : selectedDataset ? (
                    <DatasetPage />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <EmptyState
                            icon={<Upload className="h-10 w-10 text-text-muted" />}
                            title="No dataset selected"
                            description="Upload a CSV or PDF file, then ask questions in plain English to get instant AI-powered insights."
                            action={
                                <Button onClick={() => setShowUpload(true)}>
                                    <Upload className="h-4 w-4 mr-2" />
                                    Upload Your First Dataset
                                </Button>
                            }
                        />
                    </div>
                )}
            </div>
        </div>
    );
};

export default DashboardPage;
