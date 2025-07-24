/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable no-unused-vars */
import { useState, useEffect } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { FileText, ArrowLeft } from "lucide-react";
import OperationSelector from "../components/OperationSelector";
import LoadingSpinner from "../components/LoadingSpinner";
import toast from "react-hot-toast";

const AnalysisPage = () => {
  const { fileId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [fileData, setFileData] = useState(location.state?.fileData || null);
  const [fileInfo, setFileInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (!fileData && fileId) {
      // Fetch file info if not provided via navigation state
      fetchFileInfo();
    } else if (fileData) {
      setFileInfo(fileData);
    }
  }, [fileId, fileData]);

  const fetchFileInfo = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/file/${fileId}/info`
      );
      if (!response.ok) {
        throw new Error("Failed to fetch file information");
      }
      const data = await response.json();
      setFileInfo(data);
    } catch (error) {
      console.error("Error fetching file info:", error);
      toast.error("Failed to load file information");
      navigate("/upload");
    } finally {
      setIsLoading(false);
    }
  };

  const handleOperationSelect = async (operationData) => {
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append("file_id", operationData.fileId);
      formData.append("operation", operationData.operation);
      formData.append("mode", operationData.mode);
      formData.append("options", JSON.stringify(operationData.options));

      const response = await fetch("http://localhost:8000/api/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Processing failed");
      }

      const result = await response.json();

      toast.success("Processing completed successfully!");

      // Navigate to results page with the processing results
      navigate(`/results/${fileId}`, {
        state: {
          fileData: fileInfo,
          operationData,
          results: result,
        },
      });
    } catch (error) {
      console.error("Processing error:", error);
      toast.error("Failed to process data. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const goBack = () => {
    navigate("/upload");
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading file information..." />;
  }

  if (!fileInfo) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-500 mb-4">File not found</p>
        <button onClick={goBack} className="btn-primary">
          Back to Upload
        </button>
      </div>
    );
  }

  if (isProcessing) {
    return (
      <div className="max-w-4xl mx-auto">
        <LoadingSpinner
          message="Processing your data... This may take a few moments depending on the operation and file size."
          className="py-16"
        />
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Please don't close this page while processing is in progress.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <button
            onClick={goBack}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Configure Analysis
            </h1>
            <p className="text-gray-600">
              Choose how you want to analyze your data
            </p>
          </div>
        </div>
      </div>

      {/* File Information Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <FileText className="w-6 h-6 text-blue-500" />
          <h2 className="text-lg font-semibold">Dataset Overview</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">File Details</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>
                <span className="font-medium">Name:</span> {fileInfo.filename}
              </li>
              <li>
                <span className="font-medium">Rows:</span>{" "}
                {fileInfo.shape?.[0]?.toLocaleString() || "N/A"}
              </li>
              <li>
                <span className="font-medium">Columns:</span>{" "}
                {fileInfo.shape?.[1] || fileInfo.columns?.length || "N/A"}
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-2">Data Quality</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              {fileInfo.missing_values && (
                <li>
                  <span className="font-medium">Missing Values:</span>{" "}
                  {Object.values(fileInfo.missing_values).reduce(
                    (sum, val) => sum + val,
                    0
                  )}
                </li>
              )}
              <li>
                <span className="font-medium">Data Types:</span>{" "}
                {fileInfo.dtypes ? Object.keys(fileInfo.dtypes).length : "N/A"}{" "}
                types
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-medium text-gray-900 mb-2">Quick Stats</h3>
            <div className="text-sm text-gray-600">
              {fileInfo.numerical_summary && (
                <p>
                  <span className="font-medium">Numerical Columns:</span>{" "}
                  {Object.keys(fileInfo.numerical_summary).length}
                </p>
              )}
              {fileInfo.categorical_summary && (
                <p>
                  <span className="font-medium">Categorical Columns:</span>{" "}
                  {Object.keys(fileInfo.categorical_summary).length}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Operation Selection */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-6">
          Select Analysis Operation
        </h2>
        <OperationSelector
          onSelectOperation={handleOperationSelect}
          selectedFile={fileInfo}
        />
      </div>

      {/* Help Section */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">
          Need Help Choosing?
        </h3>
        <div className="text-blue-700 text-sm space-y-2">
          <p>
            <strong>Data Cleaning:</strong> Start here if your data has missing
            values, duplicates, or inconsistent formatting.
          </p>
          <p>
            <strong>Data Transformation:</strong> Use this to scale features,
            encode categories, or create new features for machine learning.
          </p>
          <p>
            <strong>Data Classification:</strong> Get a comprehensive analysis
            of your data types, quality, and patterns.
          </p>
          <p>
            <strong>Data Visualization:</strong> Generate charts and dashboards
            to explore relationships and patterns in your data.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
