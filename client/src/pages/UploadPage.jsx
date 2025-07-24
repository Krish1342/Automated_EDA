import { useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import { FileSpreadsheet, ArrowRight } from "lucide-react";

const UploadPage = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const navigate = useNavigate();

  const handleFileUploaded = (fileData) => {
    setUploadedFile(fileData);
    setIsUploading(false);
  };

  const handleContinue = () => {
    if (uploadedFile) {
      navigate(`/analysis/${uploadedFile.file_id}`, {
        state: { fileData: uploadedFile },
      });
    }
  };

  const formatShape = (shape) => {
    return `${shape[0].toLocaleString()} rows × ${shape[1]} columns`;
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Your Data
        </h1>
        <p className="text-lg text-gray-600">
          Upload your CSV file to begin automated exploratory data analysis
        </p>
      </div>

      <div className="mb-8">
        <FileUpload
          onFileUploaded={handleFileUploaded}
          isUploading={isUploading}
        />
      </div>

      {uploadedFile && (
        <div className="fade-in">
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
            <div className="flex items-center space-x-3 mb-4">
              <FileSpreadsheet className="w-6 h-6 text-green-500" />
              <h3 className="text-lg font-semibold text-gray-900">
                File Uploaded Successfully!
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">
                  File Information
                </h4>
                <ul className="space-y-1 text-sm">
                  <li>
                    <span className="font-medium">Name:</span>{" "}
                    {uploadedFile.filename}
                  </li>
                  <li>
                    <span className="font-medium">Size:</span>{" "}
                    {formatShape(uploadedFile.shape)}
                  </li>
                  <li>
                    <span className="font-medium">Columns:</span>{" "}
                    {uploadedFile.columns.length}
                  </li>
                </ul>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Columns</h4>
                <div className="max-h-32 overflow-y-auto">
                  <div className="flex flex-wrap gap-1">
                    {uploadedFile.columns.map((column, index) => (
                      <span
                        key={index}
                        className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                      >
                        {column}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {uploadedFile.preview && uploadedFile.preview.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
              <h4 className="font-medium text-gray-900 mb-4">Data Preview</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {uploadedFile.columns.map((column, index) => (
                        <th
                          key={index}
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          {column}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {uploadedFile.preview.slice(0, 5).map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {uploadedFile.columns.map((column, colIndex) => (
                          <td
                            key={colIndex}
                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                          >
                            {row[column]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Showing first 5 rows of your data
              </p>
            </div>
          )}

          <div className="text-center">
            <button
              onClick={handleContinue}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              Continue to Analysis
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        </div>
      )}

      {!uploadedFile && (
        <div className="text-center py-8">
          <div className="bg-blue-50 rounded-lg p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">
              Supported File Format
            </h3>
            <p className="text-blue-700 mb-4">
              Currently, we support CSV (Comma Separated Values) files up to
              100MB in size.
            </p>
            <ul className="text-sm text-blue-600 text-left max-w-md mx-auto">
              <li>• Ensure your CSV has column headers in the first row</li>
              <li>• Check that data is properly formatted</li>
              <li>• Remove any special characters that might cause issues</li>
              <li>• Consider reducing file size if over 100MB</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
